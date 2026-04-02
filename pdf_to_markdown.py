#!/usr/bin/env python3
"""
Convert a PDF textbook to Markdown using OpenAI GPT-5.4 vision.

Renders each page as an image, sends it to GPT-5.4 via the Responses API,
and gets back Markdown with LaTeX equations. Runs pages in parallel for speed.

Usage:
    python pdf_to_markdown.py "path/to/textbook.pdf" --output output_dir/
"""

import argparse
import asyncio
import base64
import io
import os
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
5. For figures/diagrams: write ![Figure X.X: caption](figures/figX_X.png) as a placeholder and describe the figure briefly in a comment below it: <!-- Description: ... -->
6. Preserve footnotes, references, and example numbering.
7. If the page is a table of contents, index, or mostly blank, still convert what's there.
8. Do NOT add any commentary, explanations, or notes of your own. Only output the Markdown content."""

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


async def convert_page(
    client: AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    image,
    page_num: int,
    total_pages: int,
) -> tuple[int, str]:
    """Send a single page image to GPT-5.4 and get Markdown back."""
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
                                "text": f"Convert this page (page {page_num} of {total_pages}) to Markdown.",
                            },
                        ],
                    }
                ],
            )
            markdown = response.output_text
            print(f"  Page {page_num}/{total_pages} done")
            return page_num, markdown

        except Exception as e:
            print(f"  Page {page_num}/{total_pages} FAILED: {e}")
            return page_num, f"<!-- ERROR converting page {page_num}: {e} -->\n"


async def convert_all_pages(images: list, output_dir: Path, concurrency: int) -> None:
    """Convert all pages in parallel and write output."""
    client = AsyncOpenAI()
    semaphore = asyncio.Semaphore(concurrency)
    total = len(images)

    print(f"\nConverting {total} pages with {concurrency} concurrent requests...")
    start = time.time()

    tasks = [
        convert_page(client, semaphore, img, i + 1, total)
        for i, img in enumerate(images)
    ]
    results = await asyncio.gather(*tasks)

    # Sort by page number
    results.sort(key=lambda x: x[0])

    # Write individual page files
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

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

    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Pages converted: {total - errors}/{total}")
    if errors:
        print(f"  Failed pages: {errors} (see ERROR comments in output)")
    print(f"  Individual pages: {pages_dir}/")
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
    if args.pages:
        if "-" in args.pages:
            start, end = args.pages.split("-")
            start, end = int(start), int(end)
        else:
            start = end = int(args.pages)
        images = images[start - 1 : end]
        print(f"Selected pages {start}-{end} ({len(images)} pages)")

    # Run conversion
    asyncio.run(convert_all_pages(images, output_dir, args.concurrency))


if __name__ == "__main__":
    main()
