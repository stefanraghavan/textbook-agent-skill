"""
Core PDF-to-Markdown conversion logic.

Refactored from pdf_to_markdown.py into importable async functions
for use in the Modal API. The original CLI script is unchanged.
"""

from __future__ import annotations

import asyncio
import base64
import io
import json
import re
import time
from pathlib import Path
from typing import Callable

from openai import AsyncOpenAI
from pdf2image import convert_from_path
from PIL import Image


SYSTEM_PROMPT = """You are converting a textbook page image to Markdown. Follow these rules:

1. Reproduce ALL text content faithfully — do not summarize or skip anything.
2. Use proper Markdown heading levels (# for chapter titles, ## for sections, ### for subsections).
3. Convert all equations to LaTeX notation using $...$ for inline and $$...$$ for display equations.
4. Convert tables to Markdown tables. Preserve all values exactly.
5. For figures/diagrams: write the image reference as ![caption](figures/page_PPPP_fig_NN.png) where PPPP is the zero-padded page number and NN is the figure number on that page (01, 02, etc.). Describe the figure briefly in a comment below it: <!-- Description: ... -->
6. Preserve footnotes, references, and example numbering.
7. If the page is a table of contents, index, or mostly blank, still convert what's there.
8. Do NOT add any commentary, explanations, or notes of your own. Only output the Markdown content.

IMPORTANT — Figure bounding boxes:
After the Markdown content, output a JSON block fenced with ```json that lists bounding boxes for every figure/diagram on the page. Each entry should have:
- "id": the filename used in the Markdown (e.g. "page_0021_fig_01")
- "bbox": [left, top, right, bottom] as percentages (0-100) of the page image dimensions
- "caption": short caption text

If there are no figures on the page, output an empty array: ```json\n[]\n```

Example:
```json
[
  {"id": "page_0021_fig_01", "bbox": [5, 8, 95, 45], "caption": "Stress components"},
  {"id": "page_0021_fig_02", "bbox": [10, 55, 85, 90], "caption": "Complete state of stress"}
]
```"""

MODEL = "gpt-5.4"
DEFAULT_CONCURRENCY = 50
DEFAULT_DPI = 200


def get_page_count(pdf_bytes: bytes) -> int:
    """Get total page count without rendering."""
    import tempfile
    from pdf2image.pdf2image import pdfinfo_from_path
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        info = pdfinfo_from_path(tmp.name)
        return info["Pages"]


def render_page_range(pdf_bytes: bytes, first_page: int, last_page: int, dpi: int = DEFAULT_DPI) -> list[Image.Image]:
    """Render a specific range of PDF pages as PIL images."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        return convert_from_path(
            tmp.name, dpi=dpi, fmt="jpeg",
            first_page=first_page, last_page=last_page,
        )


def image_to_base64(image: Image.Image) -> str:
    """Convert a PIL image to a base64-encoded JPEG string."""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def extract_figures(raw_text: str, image: Image.Image, page_num: int, figures_dir: Path) -> str:
    """Parse the JSON bounding-box block, crop figures, return clean Markdown."""
    json_match = re.search(r"```json\s*\n(\[.*?\])\s*\n```", raw_text, re.DOTALL)
    if not json_match:
        return raw_text

    markdown = raw_text[: json_match.start()].rstrip()
    try:
        figures = json.loads(json_match.group(1))
    except json.JSONDecodeError:
        return markdown

    if not figures:
        return markdown

    width, height = image.size
    for fig in figures:
        fig_id = fig.get("id", "")
        bbox = fig.get("bbox", [])
        if len(bbox) != 4 or not fig_id:
            continue

        left_pct, top_pct, right_pct, bottom_pct = bbox
        left = max(0, min(int(width * left_pct / 100), width))
        top = max(0, min(int(height * top_pct / 100), height))
        right = max(left + 1, min(int(width * right_pct / 100), width))
        bottom = max(top + 1, min(int(height * bottom_pct / 100), height))

        cropped = image.crop((left, top, right, bottom))
        fig_path = figures_dir / f"{fig_id}.png"
        cropped.save(fig_path, format="PNG")

    return markdown


async def convert_page(
    client: AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    image: Image.Image,
    page_num: int,
    total_pages: int,
    figures_dir: Path,
) -> tuple[int, str]:
    """Convert a single page image to Markdown via GPT vision."""
    async with semaphore:
        b64 = image_to_base64(image)
        try:
            response = await client.responses.create(
                model=MODEL,
                instructions=SYSTEM_PROMPT,
                input=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{b64}",
                            },
                            {
                                "type": "input_text",
                                "text": f"Convert this page (page {page_num:04d} of {total_pages}) to Markdown. Use page number {page_num:04d} in figure filenames.",
                            },
                        ],
                    }
                ],
            )
            markdown = extract_figures(response.output_text, image, page_num, figures_dir)
            return page_num, markdown
        except Exception as e:
            return page_num, f"<!-- ERROR converting page {page_num}: {e} -->\n"


async def convert_batch(
    pdf_bytes: bytes,
    first_page: int,
    last_page: int,
    total_pages: int,
    output_dir: Path,
    dpi: int = DEFAULT_DPI,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> dict:
    """
    Convert a range of pages from a PDF. Used by fan-out workers.

    Returns {pages: [...(page_num, markdown)], figures: int, errors: int}.
    """
    images = render_page_range(pdf_bytes, first_page, last_page, dpi=dpi)

    pages_dir = output_dir / "pages"
    figures_dir = output_dir / "figures"
    pages_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    client = AsyncOpenAI()
    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        convert_page(client, semaphore, img, first_page + i, total_pages, figures_dir)
        for i, img in enumerate(images)
    ]
    results = await asyncio.gather(*tasks)

    # Write page files
    for page_num, markdown in results:
        page_file = pages_dir / f"page_{page_num:04d}.md"
        page_file.write_text(markdown, encoding="utf-8")

    errors = sum(1 for _, md in results if md.startswith("<!-- ERROR"))
    fig_count = len(list(figures_dir.glob("*.png")))

    return {
        "first_page": first_page,
        "last_page": last_page,
        "converted": len(results),
        "errors": errors,
        "figures": fig_count,
    }


def write_combined_file(output_dir: Path, total_pages: int):
    """Merge individual page files into full_textbook.md."""
    pages_dir = output_dir / "pages"
    combined = output_dir / "full_textbook.md"
    with open(combined, "w", encoding="utf-8") as f:
        for page_num in range(1, total_pages + 1):
            page_file = pages_dir / f"page_{page_num:04d}.md"
            if page_file.exists():
                f.write(f"<!-- Page {page_num} -->\n\n")
                f.write(page_file.read_text(encoding="utf-8"))
                f.write("\n\n---\n\n")
