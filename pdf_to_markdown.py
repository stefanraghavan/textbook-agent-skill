#!/usr/bin/env python3
"""
Convert a PDF textbook to Markdown using OpenAI GPT-5.4 vision.

Renders each page as an image, sends it to GPT-5.4 via the Responses API,
and gets back Markdown with LaTeX equations. Figures are cropped from rendered
pages using bounding boxes returned by the model. Runs pages in parallel.

Usage:
    python pdf_to_markdown.py "path/to/textbook.pdf" --output output_dir/
"""

import argparse
import asyncio
import base64
import io
import json
import os
import re
import sys
import time
from pathlib import Path

from openai import AsyncOpenAI
from pdf2image import convert_from_path


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
MAX_CONCURRENT = 30


def render_pages(pdf_path: str, dpi: int = 200) -> list:
    """Render all PDF pages as PIL images."""
    print(f"Rendering PDF pages at {dpi} DPI...")
    start = time.time()
    images = convert_from_path(pdf_path, dpi=dpi, fmt="jpeg")
    elapsed = time.time() - start
    print(f"Rendered {len(images)} pages in {elapsed:.1f}s")
    return images


def image_to_base64(image) -> str:
    """Convert a PIL image to a base64-encoded JPEG string."""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def extract_figures_from_response(raw_text: str, image, page_num: int, figures_dir: Path) -> str:
    """Parse the JSON bounding box block, crop figures, and return clean Markdown."""
    # Split off the JSON block from the end
    json_match = re.search(r"```json\s*\n(\[.*?\])\s*\n```", raw_text, re.DOTALL)

    if not json_match:
        return raw_text

    markdown = raw_text[:json_match.start()].rstrip()
    json_str = json_match.group(1)

    try:
        figures = json.loads(json_str)
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

        # Convert percentages to pixel coordinates
        left = int(width * left_pct / 100)
        top = int(height * top_pct / 100)
        right = int(width * right_pct / 100)
        bottom = int(height * bottom_pct / 100)

        # Clamp to image bounds
        left = max(0, min(left, width))
        top = max(0, min(top, height))
        right = max(left + 1, min(right, width))
        bottom = max(top + 1, min(bottom, height))

        # Crop and save
        cropped = image.crop((left, top, right, bottom))
        fig_path = figures_dir / f"{fig_id}.png"
        cropped.save(fig_path, format="PNG")

    return markdown


async def convert_page(
    client: AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    image,
    page_num: int,
    total_pages: int,
    figures_dir: Path,
) -> tuple[int, str]:
    """Send a single page image to GPT-5.4 and get Markdown + figure crops back."""
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
            raw_text = response.output_text

            # Extract figures and clean up markdown
            markdown = extract_figures_from_response(raw_text, image, page_num, figures_dir)

            print(f"  Page {page_num}/{total_pages} done")
            return page_num, markdown

        except Exception as e:
            print(f"  Page {page_num}/{total_pages} FAILED: {e}")
            return page_num, f"<!-- ERROR converting page {page_num}: {e} -->\n"


async def convert_all_pages(images: list, output_dir: Path, concurrency: int, page_offset: int = 0) -> None:
    """Convert all pages in parallel and write output."""
    client = AsyncOpenAI()
    semaphore = asyncio.Semaphore(concurrency)
    total = len(images)

    # Create output directories
    pages_dir = output_dir / "pages"
    figures_dir = output_dir / "figures"
    pages_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nConverting {total} pages with {concurrency} concurrent requests...")
    print(f"  Figures will be saved to: {figures_dir}/")
    start = time.time()

    tasks = [
        convert_page(client, semaphore, img, page_offset + i + 1, page_offset + total, figures_dir)
        for i, img in enumerate(images)
    ]
    results = await asyncio.gather(*tasks)

    # Sort by page number
    results.sort(key=lambda x: x[0])

    # Write individual page files
    for page_num, markdown in results:
        page_file = pages_dir / f"page_{page_num:04d}.md"
        page_file.write_text(markdown, encoding="utf-8")

    # Write combined file
    combined = output_dir / "full_textbook.md"
    with open(combined, "w", encoding="utf-8") as f:
        for page_num, markdown in results:
            f.write(f"<!-- Page {page_num} -->\n\n")
            f.write(markdown)
            f.write("\n\n---\n\n")

    elapsed = time.time() - start
    errors = sum(1 for _, md in results if md.startswith("<!-- ERROR"))
    fig_count = len(list(figures_dir.glob("*.png")))

    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Pages converted: {total - errors}/{total}")
    print(f"  Figures extracted: {fig_count}")
    if errors:
        print(f"  Failed pages: {errors} (see ERROR comments in output)")
    print(f"  Individual pages: {pages_dir}/")
    print(f"  Figures:          {figures_dir}/")
    print(f"  Combined file:    {combined}")


def main():
    parser = argparse.ArgumentParser(description="Convert a PDF textbook to Markdown using GPT-5.4 vision")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--output", "-o", default="markdown_output", help="Output directory (default: markdown_output)")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for rendering pages (default: 200)")
    parser.add_argument("--concurrency", "-c", type=int, default=MAX_CONCURRENT, help=f"Max concurrent API requests (default: {MAX_CONCURRENT})")
    parser.add_argument("--pages", "-p", help="Page range to convert, e.g. '1-10' or '5' (default: all)")
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Render PDF pages
    images = render_pages(args.pdf, dpi=args.dpi)

    # Slice if --pages specified
    page_offset = 0
    if args.pages:
        if "-" in args.pages:
            start, end = args.pages.split("-")
            start, end = int(start), int(end)
        else:
            start = end = int(args.pages)
        images = images[start - 1 : end]
        page_offset = start - 1
        print(f"Selected pages {start}-{end} ({len(images)} pages)")

    # Run conversion
    asyncio.run(convert_all_pages(images, output_dir, args.concurrency, page_offset))


if __name__ == "__main__":
    main()
