"""
Modal app: PDF-to-Skill API.

Endpoints:
  POST /create-skill  — Upload a PDF, start async conversion
  GET  /skill/{job_id} — Check job status
  GET  /skill/{job_id}/download — Download the finished skill as a zip

Deploy:
  modal deploy skill_api/app.py

Local dev:
  modal serve skill_api/app.py
"""

import json
import math
import zipfile
from io import BytesIO
from pathlib import Path

import modal
from fastapi import Form, UploadFile, File

# ---------------------------------------------------------------------------
# Modal infrastructure
# ---------------------------------------------------------------------------

app = modal.App("pdf-to-skill")

volume = modal.Volume.from_name("skills-storage", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("poppler-utils")
    .pip_install("openai", "pdf2image", "Pillow", "fastapi[standard]")
    .add_local_python_source("skill_api")
)

VOLUME_ROOT = Path("/data")
JOBS_DIR = VOLUME_ROOT / "jobs"

NUM_WORKERS = 4           # parallel containers for page conversion
CONCURRENCY_PER_WORKER = 50  # concurrent API calls per container


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def job_dir(job_id: str) -> Path:
    return JOBS_DIR / job_id


def read_status(job_id: str) -> dict:
    status_file = job_dir(job_id) / "status.json"
    if not status_file.exists():
        return None
    return json.loads(status_file.read_text())


def write_status(job_id: str, status: dict):
    d = job_dir(job_id)
    d.mkdir(parents=True, exist_ok=True)
    (d / "status.json").write_text(json.dumps(status))


# ---------------------------------------------------------------------------
# Fan-out worker: converts a batch of pages in its own container
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    volumes={str(VOLUME_ROOT): volume},
    timeout=1800,
    secrets=[modal.Secret.from_name("openai-secret")],
)
async def convert_page_batch(
    pdf_bytes: bytes,
    first_page: int,
    last_page: int,
    total_pages: int,
    output_dir_str: str,
    job_id: str,
):
    """Worker: render + convert a slice of the PDF."""
    from skill_api.converter import convert_batch

    output_dir = Path(output_dir_str)
    result = await convert_batch(
        pdf_bytes=pdf_bytes,
        first_page=first_page,
        last_page=last_page,
        total_pages=total_pages,
        output_dir=output_dir,
    )

    # Persist to volume so orchestrator can see the files
    volume.commit()

    return result


# ---------------------------------------------------------------------------
# Orchestrator: splits work, fans out, merges results
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    volumes={str(VOLUME_ROOT): volume},
    timeout=3600,
    secrets=[modal.Secret.from_name("openai-secret")],
)
async def run_conversion(job_id: str, pdf_bytes: bytes, skill_name: str, description: str):
    """Orchestrate the full PDF -> Markdown -> SKILL.md pipeline with fan-out."""
    from skill_api.converter import get_page_count, write_combined_file
    from skill_api.skill_gen import generate_skill_md

    output = job_dir(job_id) / skill_name
    content_subdir = skill_name.replace("-", "_")
    content_dir = output / content_subdir

    # Step 1: Get page count
    write_status(job_id, {"state": "preparing", "detail": "Counting pages..."})
    volume.commit()
    total_pages = get_page_count(pdf_bytes)

    # Step 2: Split into batches and fan out
    batch_size = math.ceil(total_pages / NUM_WORKERS)
    batches = []
    for i in range(NUM_WORKERS):
        first = i * batch_size + 1
        last = min((i + 1) * batch_size, total_pages)
        if first > total_pages:
            break
        batches.append((first, last))

    write_status(job_id, {
        "state": "converting",
        "detail": f"Converting {total_pages} pages across {len(batches)} workers...",
        "progress": {"total": total_pages, "workers": len(batches)},
    })
    volume.commit()

    # Fan out: launch all batch workers in parallel
    handles = []
    for first, last in batches:
        h = await convert_page_batch.spawn.aio(
            pdf_bytes, first, last, total_pages, str(content_dir), job_id,
        )
        handles.append(h)

    # Wait for all workers to finish
    batch_results = []
    for h in handles:
        result = await h.get.aio()
        batch_results.append(result)

    # Reload volume to see all worker outputs
    volume.reload()

    # Step 3: Merge into combined file
    total_errors = sum(r["errors"] for r in batch_results)
    total_figures = sum(r["figures"] for r in batch_results)
    total_converted = sum(r["converted"] for r in batch_results)
    write_combined_file(content_dir, total_pages)

    # Step 4: Generate SKILL.md
    write_status(job_id, {"state": "generating_index", "detail": "Generating SKILL.md index..."})
    volume.commit()

    pages_dir = content_dir / "pages"
    skill_md = await generate_skill_md(
        pages_dir=pages_dir,
        skill_name=skill_name,
        content_subdir=content_subdir,
        description=description,
    )
    (output / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # Done
    write_status(job_id, {
        "state": "done",
        "detail": "Conversion complete.",
        "stats": {
            "pages": total_converted,
            "errors": total_errors,
            "figures": total_figures,
            "workers": len(batches),
        },
        "skill_name": skill_name,
    })
    volume.commit()


# ---------------------------------------------------------------------------
# Web endpoints
# ---------------------------------------------------------------------------

@app.function(image=image, volumes={str(VOLUME_ROOT): volume})
@modal.fastapi_endpoint(method="POST", docs=True)
async def create_skill(
    pdf: UploadFile = File(description="The PDF file to convert"),
    skill_name: str = Form(description="Kebab-case skill name, e.g. 'fluid-dynamics'"),
    description: str = Form(default="", description="Optional description of the textbook/domain"),
):
    """
    Upload a PDF and start converting it into an agent skill.

    Returns a job ID to poll for status.
    """
    import uuid

    pdf_bytes = await pdf.read()
    job_id = uuid.uuid4().hex[:12]

    write_status(job_id, {"state": "queued", "detail": "Job queued."})
    await volume.commit.aio()

    await run_conversion.spawn.aio(job_id, pdf_bytes, skill_name, description)

    return {
        "job_id": job_id,
        "status_url": f"/skill/{job_id}",
        "message": f"Conversion started for '{skill_name}'. Poll /skill/{job_id} for progress.",
    }


@app.function(image=image, volumes={str(VOLUME_ROOT): volume})
@modal.fastapi_endpoint(method="GET", docs=True)
async def get_skill_status(job_id: str):
    """Check the status of a conversion job."""
    await volume.reload.aio()
    status = read_status(job_id)
    if status is None:
        return {"error": "Job not found"}, 404
    return {"job_id": job_id, **status}


@app.function(image=image, volumes={str(VOLUME_ROOT): volume})
@modal.fastapi_endpoint(method="GET", docs=True)
async def download_skill(job_id: str):
    """Download the finished skill as a zip file."""
    from starlette.responses import Response

    await volume.reload.aio()
    status = read_status(job_id)
    if status is None:
        return Response(content='{"error": "Job not found"}', status_code=404, media_type="application/json")
    if status.get("state") != "done":
        return Response(
            content=json.dumps({"error": "Job not finished yet", "state": status.get("state")}),
            status_code=409,
            media_type="application/json",
        )

    skill_name = status["skill_name"]
    skill_root = job_dir(job_id) / skill_name

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(skill_root.rglob("*")):
            if fpath.is_file():
                arcname = str(fpath.relative_to(skill_root))
                zf.write(fpath, arcname)
    buf.seek(0)

    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{skill_name}.zip"'},
    )
