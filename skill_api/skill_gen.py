"""
Auto-generate a SKILL.md index from converted textbook pages.

Reads the converted markdown pages, extracts structure (headings, tables,
key sections), and uses an LLM to produce a SKILL.md in the established
format with YAML frontmatter, lookup tables, and common workflows.
"""

import re
from pathlib import Path

from openai import AsyncOpenAI


# Two existing SKILL.md files as few-shot examples (trimmed for token budget)
EXAMPLE_SKILL_SNIPPET = """
---
name: structures-engineering
version: 1.0.0
description: Structural engineering analysis using Roark's Formulas for Stress and Strain (7th Edition). Look up and apply formulas for beams, plates, shells, torsion, columns, and stress concentration.
---

# Structures Engineering Skill

You are a structural engineering analyst. Use Roark's Formulas for Stress and Strain to look up and apply the correct formulas for structural analysis problems.

## How to Use This Skill

1. **Identify the structural element** — What type of structure? (beam, plate, shell, column, ring, bar, etc.)
2. **Identify the loading** — What forces/moments are applied?
3. **Look up the relevant table** using the index below
4. **Read the specific pages** from `roarks/pages/page_XXXX.md`
5. **Apply the formula** — always use Python scripts for calculations, never mental math
6. **Show your work** — cite the table, case number, and equation used

## Quick-Reference: Problem Type to Table

### Beams (Chapter 8, pages 130-270)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Simple beam loading | 8.1 | 195-205 | Shear, moment, and deflection for common beam cases |
| Rigid frames | 8.2 | 207-215 | Reactions and deformations for portal frames |

## Common Workflows

### "What stress does this beam experience?"
1. Read Table 8.1 (pages 195-205) — find the matching case by support type and load pattern
2. Extract the bending moment formula M(x)
3. Apply the flexure formula: sigma = M*c/I
"""


def extract_page_summaries(pages_dir: Path, sample_every: int = 5) -> list[dict]:
    """
    Read page files and extract headings + first lines for structure detection.
    Samples every Nth page for the full content, headings from all pages.
    """
    page_files = sorted(pages_dir.glob("page_*.md"))
    summaries = []

    for i, pf in enumerate(page_files):
        text = pf.read_text(encoding="utf-8")
        lines = text.strip().split("\n")

        # Always extract headings
        headings = [ln for ln in lines if ln.startswith("#")]

        # For sampled pages, include more content
        if i % sample_every == 0:
            # First 40 lines or full page if shorter
            content = "\n".join(lines[:40])
        else:
            content = None

        page_num = int(re.search(r"page_(\d+)", pf.name).group(1))
        summaries.append({
            "page": page_num,
            "headings": headings,
            "content": content,
        })

    return summaries


def build_structure_prompt(summaries: list[dict]) -> str:
    """Build a compact representation of the book's structure for the LLM."""
    parts = []
    for s in summaries:
        hdrs = "\n".join(s["headings"]) if s["headings"] else "(no headings)"
        if s["content"]:
            parts.append(f"=== Page {s['page']} ===\n{s['content']}\n")
        elif s["headings"]:
            parts.append(f"=== Page {s['page']} [headings only] ===\n{hdrs}\n")
    return "\n".join(parts)


async def generate_skill_md(
    pages_dir: Path,
    skill_name: str,
    content_subdir: str,
    description: str = "",
) -> str:
    """
    Generate a SKILL.md from converted textbook pages.

    Args:
        pages_dir: Path to the pages/ directory with page_XXXX.md files.
        skill_name: Kebab-case name for the skill (e.g. "fluid-dynamics").
        content_subdir: Name of the content subdirectory (e.g. "anderson").
        description: Optional user-provided description of the textbook/domain.

    Returns:
        The generated SKILL.md content as a string.
    """
    summaries = extract_page_summaries(pages_dir)
    structure = build_structure_prompt(summaries)
    total_pages = len(summaries)

    client = AsyncOpenAI()
    response = await client.responses.create(
        model="gpt-5.4",
        instructions=f"""You are generating a SKILL.md index file for a textbook that has been converted to markdown pages.

The SKILL.md serves as a lookup index so an AI agent can efficiently find the right pages for any problem type. Study the example below carefully and produce output in the EXACT same format.

EXAMPLE SKILL.md (for reference — match this structure):
{EXAMPLE_SKILL_SNIPPET}

RULES:
1. Start with YAML frontmatter: name, version (1.0.0), description
2. Write a one-line persona ("You are a [domain] engineer/analyst...")
3. "How to Use This Skill" section with numbered steps — pages are at `{content_subdir}/pages/page_XXXX.md`
4. "Important Notes" section with 3-5 bullets about how the book is organized
5. "Quick-Reference: Problem Type to Chapter" — this is the MOST IMPORTANT section
   - Group by chapter/topic with ### headings including chapter number and page range
   - Each group has a markdown table with columns: Problem Type | Section | Pages | Description
   - Be specific about page ranges — use the actual page numbers from the content
6. "Common Workflows" section with 3-5 practical "How do I...?" workflows
   - Each workflow is a ### heading phrased as a question
   - Numbered steps referencing specific sections and pages

Be thorough in the Quick-Reference tables. Cover ALL major topics in the book.
Use the page numbers from the content — do not make them up.""",
        input=[
            {
                "type": "message",
                "role": "user",
                "content": f"""Generate a SKILL.md for this textbook:

Skill name: {skill_name}
Content directory: {content_subdir}
Total pages: {total_pages}
User description: {description or '(none provided — infer from content)'}

Here is the book's structure (headings and sampled content from {total_pages} pages):

{structure}""",
            }
        ],
    )

    return response.output_text
