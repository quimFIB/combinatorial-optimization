"""Add the optional "explore" links to a unit's deck (authoring helper).

    uv run python slides/viz/add_links.py 02 "A walk on the example polygon=1" "Degeneracy and cycling=1"

Each argument is "<slide title>=<explore slide index>". The link is a small muted chip in
the slide's bottom-right corner, opening the unit's explore.html in a new tab at that slide.
The script also adds one sentence to the deck's "getting around" box, once. Running it
twice is harmless: slides that already have a link are left alone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def chip(index: int, label: str = "explore interactively") -> str:
    return (f'  <p class="viz-link-row"><a class="viz-link" href="explore.html#/{index}" '
            f'target="_blank" rel="noopener">{label}</a></p>\n')


def add(unit_key: str, pairs: list[tuple[str, int]]) -> list[str]:
    unit = next(p for p in sorted((ROOT / "units").iterdir()) if p.name.startswith(unit_key))
    path = unit / "slides.html"
    s = path.read_text()
    done = []
    for title, index in pairs:
        m = re.search(r"<h2>" + re.escape(title) + r"</h2>", s)
        if not m:
            raise SystemExit(f"{unit.name}: no slide titled {title!r}")
        start = s.rfind("<section", 0, m.start())
        end = s.find("</section>", m.end())
        section = s[start:end]
        if "viz-link" in section:
            continue
        notes = section.rfind("<aside")
        if notes >= 0:                       # insert before the notes' own indentation
            notes = section.rfind("\n", 0, notes) + 1
        cut = start + (notes if notes >= 0 else len(section))
        s = s[:cut] + chip(index) + s[cut:]
        done.append(title)
    box = re.search(r'(<span class="label">getting around</span>\s*<p class="small">)(.*?)(</p>)', s, re.S)
    if box and "explore.html" not in box.group(2):
        extra = (' Optional extra: <a href="explore.html" target="_blank" rel="noopener">interactive figures</a>, '
                 'linked from the slides they support by a small ▸ chip; skip them freely.')
        s = s[:box.end(2)] + extra + s[box.end(2):]
    path.write_text(s)
    return done


if __name__ == "__main__":
    key, *specs = sys.argv[1:]
    pairs = [(t, int(i)) for t, i in (spec.rsplit("=", 1) for spec in specs)]
    print(add(key, pairs))
