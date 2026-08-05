#!/usr/bin/env python3
"""Richard OS — book-to-skill: turn a book/document into a reusable skill.
Usage: python tools/book_to_skill.py <source.txt> <skill-name>"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "04-skills"

def extract(source: Path):
    """Pull chapters/sections from a markdown or text book."""
    text = source.read_text(errors="ignore")
    # naive section split on markdown headers
    sections, current, cur_head = [], [], None
    for line in text.splitlines():
        if line.startswith("#") and line.strip().lstrip("#").strip():
            if cur_head and current:
                sections.append((cur_head, "\n".join(current)))
            cur_head = line.strip().lstrip("#").strip()
            current = []
        else:
            current.append(line)
    if cur_head and current:
        sections.append((cur_head, "\n".join(current)))
    if not sections:
        sections = [("Overview", text[:4000])]
    return sections

def make_skill(name: str, sections):
    """Generate 04-skills/<name>/skill.md + reference.md + examples.md."""
    d = SKILLS / name
    d.mkdir(parents=True, exist_ok=True)
    skill = [
        f"# Skill: {name.replace('-', ' ').title()}",
        "",
        "## When to use",
        f"Reach for this when you need {name.replace('-', ' ')}.",
        "",
        "## Process",
    ]
    for i, (head, body) in enumerate(sections[:8]):
        skill.append(f"### {i+1}. {head}")
        skill.append(body.strip()[:600])
    (d / "skill.md").write_text("\n".join(skill))
    (d / "reference.md").write_text(f"# Reference — {name}\n\nSource: book-to-skill.\n")
    (d / "examples.md").write_text(f"# Examples — {name}\n\n(tbd)\n")
    return d

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/book_to_skill.py <source.txt> <skill-name>")
        sys.exit(1)
    src = Path(sys.argv[1])
    name = sys.argv[2]
    if not src.exists():
        print(f"❌ No such file: {src}")
        sys.exit(1)
    sections = extract(src)
    d = make_skill(name, sections)
    print(f"✓ Skill '{name}' created at {d} with {len(sections)} sections")
