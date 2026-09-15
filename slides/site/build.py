"""Build the theory part of the course as a static site: decks, glossaries, figures, index.

    python slides/site/build.py [OUT]        # default OUT: _site/   (standard library only)
    uv run co site [--serve]                 # rebuild glossaries and figure data first, then this

What goes in: every unit's slides.html, explore.html, glossary.js and viz-data.js, the
shared slides/deck.* and slides/viz/ scripts and styles, CURRICULUM.html, and a generated
index.html. What never goes in: labs, reference solutions, tests, colib, data. The copy is
an allow-list, so a new file appears on the site only if this script names its kind.

The generated files (glossary.js, viz-data.js) are committed, so this script needs no
solver and no third-party package: a CI runner with plain Python can build the site.
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UNIT_FILES = ("slides.html", "explore.html", "glossary.js", "viz-data.js")
SHARED = ("slides/deck.css", "slides/deck.js")
SHARED_GLOBS = ("slides/viz/viz.js", "slides/viz/viz.css", "slides/viz/widgets/*.js", "slides/viz/widgets/*.css")


def _text(fragment: str) -> str:
    """Tag-free, unescaped text of an HTML fragment, with math delimiters left as they are."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def unit_info(unit: Path) -> dict:
    deck = (unit / "slides.html").read_text()
    title = re.search(r'<section class="title-slide">(.*?)</section>', deck, re.S).group(1)
    grab = lambda pat: (m.group(1) if (m := re.search(pat, title, re.S)) else "")
    meta = [_text(s) for s in re.findall(r"<span>(.*?)</span>", grab(r'<p class="meta">(.*?)</p>'))]
    eyebrow = _text(grab(r'<p class="eyebrow">(.*?)</p>'))
    parts = [p.strip() for p in eyebrow.split("·")]
    return {
        "dir": unit.name,
        "no": _text(grab(r'<div class="unit-no">(.*?)</div>')),
        "title": _text(grab(r"<h1>(.*?)</h1>")),
        "lede": _text(grab(r'<p class="lede">(.*?)</p>')),
        "part": parts[0] if parts else "",
        "where": " · ".join(parts[1:]),
        "kind": "branch" if "branch" in parts else "spine" if "spine" in parts else "",
        "needs": next((m for m in meta if m.startswith("needs")), ""),
        "time": next((m.split("+")[0].replace("slides", "").strip() for m in meta if m.startswith("~")), ""),
        "trunk": (m.group(1) if (m := re.search(r'<body data-trunk="([^"]*)"', deck)) else "root"),
        "explore": (unit / "explore.html").exists(),
    }


def index_html(units: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for u in units:
        groups.setdefault(u["part"], []).append(u)
    cards = []
    for part, members in groups.items():
        where = members[0]["where"].replace(" · spine", "").replace(" · branch", "").replace(" · deep theory", "")
        items = []
        for u in members:
            links = [f'<a href="units/{u["dir"]}/slides.html">slides</a>',
                     f'<a href="units/{u["dir"]}/slides.html?view=read">reading mode</a>']
            if u["explore"]:
                links.append(f'<a class="soft" href="units/{u["dir"]}/explore.html">interactive figures</a>')
            facts = " · ".join(x for x in (u["kind"], u["needs"], u["time"]) if x)
            items.append(f'''      <li class="unit" data-trunk="{u["trunk"]}">
        <span class="no">{html.escape(u["no"])}</span>
        <div>
          <a class="title" href="units/{u["dir"]}/slides.html">{html.escape(u["title"])}</a>
          <p class="lede">{html.escape(u["lede"])}</p>
          <p class="links">{" · ".join(links)}<span class="facts">{html.escape(facts)}</span></p>
        </div>
      </li>''')
        cards.append(f'''  <section class="part">
    <h2>{html.escape(part)} <span>{html.escape(where)}</span></h2>
    <ul>
{chr(10).join(items)}
    </ul>
  </section>''')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Combinatorial optimization · the theory</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>
  :root {{
    --ground: #f3f5f6; --surface: #fff; --ink: #151a1d; --ink-soft: #59646a; --ink-faint: #8a949a;
    --rule: #d9dfe1; --accent: #1f4a54;
    --c-root: #151a1d; --c-lp: #1f4a54; --c-ip: #8c5e12; --c-comb: #1f6b3f;
    --c-cp: #63397a; --c-apx: #8a3a3a; --c-prac: #5d686e; --c-coda: #2a4a80;
    --f-display: "Zilla Slab", Georgia, serif; --f-body: "IBM Plex Sans", system-ui, sans-serif;
    --f-mono: "IBM Plex Mono", Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --ground: #111517; --surface: #1a2023; --ink: #e6eaec; --ink-soft: #a3adb2; --ink-faint: #75808a;
      --rule: #2d3538; --accent: #8cc2cc; --c-root: #e6eaec; --c-lp: #8cc2cc; --c-ip: #d9a95a;
      --c-comb: #7cc59a; --c-cp: #c29ad8; --c-apx: #e09393; --c-prac: #a3adb2; --c-coda: #9db6e8; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--ground); color: var(--ink); font: 17px/1.5 var(--f-body); }}
  main {{ max-width: 980px; margin: 0 auto; padding: 48px 20px 80px; }}
  h1 {{ font: 700 2.4rem/1.1 var(--f-display); margin: 0 0 .3em; }}
  .intro {{ color: var(--ink-soft); max-width: 44em; }}
  .intro code {{ font: .9em var(--f-mono); }}
  .intro a, footer a {{ color: var(--accent); }}
  .part {{ margin-top: 42px; }}
  .part h2 {{ font: 600 1.35rem var(--f-display); border-bottom: 2px solid var(--ink); padding-bottom: 6px; margin: 0 0 8px; }}
  .part h2 span {{ font: 13px var(--f-mono); color: var(--ink-soft); letter-spacing: .06em; margin-left: 8px; }}
  ul {{ list-style: none; margin: 0; padding: 0; }}
  .unit {{ display: grid; grid-template-columns: 52px 1fr; gap: 14px; padding: 14px 0; border-bottom: 1px solid var(--rule); }}
  .no {{ font: 700 1.5rem var(--f-display); color: var(--trunk); text-align: right; line-height: 1.2; }}
  .unit .title {{ font: 600 1.12rem var(--f-display); color: var(--ink); text-decoration: none; }}
  .unit .title:hover {{ color: var(--accent); }}
  .unit .lede {{ margin: 2px 0 4px; color: var(--ink-soft); font-size: .95rem; }}
  .links {{ margin: 0; font: 14px var(--f-mono); display: flex; flex-wrap: wrap; gap: 4px 8px; align-items: baseline; }}
  .links a {{ color: var(--accent); }}
  .links a.soft {{ color: var(--ink-soft); }}
  .facts {{ color: var(--ink-faint); margin-left: auto; font-size: 13px; }}
  [data-trunk="root"] {{ --trunk: var(--c-root); }} [data-trunk="lp"] {{ --trunk: var(--c-lp); }}
  [data-trunk="ip"] {{ --trunk: var(--c-ip); }} [data-trunk="comb"] {{ --trunk: var(--c-comb); }}
  [data-trunk="cp"] {{ --trunk: var(--c-cp); }} [data-trunk="apx"] {{ --trunk: var(--c-apx); }}
  [data-trunk="prac"] {{ --trunk: var(--c-prac); }} [data-trunk="coda"] {{ --trunk: var(--c-coda); }}
  footer {{ margin-top: 48px; font-size: 14px; color: var(--ink-faint); }}
  @media (max-width: 600px) {{ .unit {{ grid-template-columns: 36px 1fr; }} .facts {{ margin-left: 0; width: 100%; }} }}
</style>
</head>
<body>
<main>
  <h1>Combinatorial optimization</h1>
  <p class="intro">The theory part of a self-study course: {len(units)} slide decks with speaker notes,
  clickable glossary terms (press <b>G</b> in a deck), a reading mode (<b>R</b>) and <b>M</b> to come back here, plus optional interactive
  figures. The labs, their tests and the reference solutions are not part of this site; commands such as
  <code>uv run co lab 07</code> in the decks refer to the course repository. See also the
  <a href="curriculum.html">curriculum</a>.</p>
{chr(10).join(cards)}
  <footer>Decks need a network connection for reveal.js, KaTeX and fonts. Built from the course sources by
  <code>slides/site/build.py</code>.</footer>
</main>
</body>
</html>
'''


def build(out: Path) -> list[str]:
    units = sorted(p for p in (ROOT / "units").iterdir() if (p / "slides.html").exists())
    if out.exists():
        shutil.rmtree(out)
    copied = []
    for u in units:
        for name in UNIT_FILES:
            src = u / name
            if src.exists():
                dst = out / "units" / u.name / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied.append(str(dst.relative_to(out)))
    for rel in SHARED:
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
        copied.append(rel)
    for pattern in SHARED_GLOBS:
        for src in sorted(ROOT.glob(pattern)):
            rel = src.relative_to(ROOT)
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(str(rel))
    if (ROOT / "CURRICULUM.html").exists():
        shutil.copy2(ROOT / "CURRICULUM.html", out / "curriculum.html")
        copied.append("curriculum.html")
    (out / "index.html").write_text(index_html([unit_info(u) for u in units]))
    (out / ".nojekyll").write_text("")          # serve files as they are; no Jekyll processing
    copied += ["index.html", ".nojekyll"]
    return copied


def check_links(out: Path) -> list[str]:
    """Every local src/href in the built pages must exist in the build."""
    missing = []
    for page in out.rglob("*.html"):
        for ref in re.findall(r'(?:src|href)="([^"#?]+)', page.read_text()):
            if re.match(r"^[a-z]+:|^//", ref):
                continue
            if not (page.parent / ref).resolve().exists():
                missing.append(f"{page.relative_to(out)} -> {ref}")
    # glossary.js is loaded by deck.js from the page's own folder
    for deck in out.glob("units/*/slides.html"):
        if not (deck.parent / "glossary.js").exists():
            missing.append(f"{deck.relative_to(out)} -> glossary.js (loaded by deck.js)")
    return missing


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
    files = build(out)
    missing = check_links(out)
    print(f"built {out} with {len(files)} files")
    for m in missing:
        print(f"missing: {m}", file=sys.stderr)
    sys.exit(1 if missing else 0)
