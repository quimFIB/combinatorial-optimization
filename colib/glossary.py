"""Turn a unit's GLOSSARY.org into glossary.js, which the slides load for term popovers.

The Org file is the source; glossary.js is derived and rebuilt by `co slides` (and
`co glossary`). Slides are opened from file://, where a page cannot fetch a sibling
file, so the data travels as a script that sets `window.GLOSSARY`.

Only the subset of Org the glossaries use is understood: `* headings`, description
items `- term :: definition` with indented continuation lines, \\(math\\), /italic/,
~code~ and =verbatim=. A trailing `/Slide: Title./` becomes the entry's slide link.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ITEM = re.compile(r"^- (.+?) :: (.*)$")
MATH = re.compile(r"\\\((.+?)\\\)")
SLIDE = re.compile(r"/Slide( notes)?: (.*?)\.?/(?=\s|$)")


def key(text: str) -> str:
    """Normalised lookup key: lower case, math delimiters dropped, spaces collapsed."""
    text = text.replace("\\(", "").replace("\\)", "").replace("$", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def title_key(text: str) -> str:
    """Slide titles compared on letters and digits only, so math markup can't break a match."""
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    return re.sub(r"[^0-9a-z]", "", text.lower())


def _split_top(term: str) -> list[str]:
    """Split "a, b (c)" on commas that are outside parentheses and math."""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(term):
        if term.startswith("\\(", i):
            j = term.find("\\)", i)
            j = len(term) if j < 0 else j + 2
            cur += term[i:j]
            i = j
            continue
        ch = term[i]
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    return [p.strip() for p in parts + [cur] if p.strip()]


def aliases(term: str) -> list[str]:
    """Every key a slide may use for this term: the whole term, each comma part, and
    each part with and without its trailing parenthetical."""
    out = [key(term)]
    for part in _split_top(term):
        out.append(key(part))
        # A trailing "(alias)" outside math; "\(I(x)\)" can't match, its parens nest.
        m = re.match(r"^(.+?)\s*\(([^()]*)\)$", part)
        if m and not m.group(1).endswith("\\"):
            out += [key(m.group(1)), key(m.group(2))]
    return list(dict.fromkeys(a for a in out if a))


def inline(text: str) -> str:
    """Org inline markup to HTML, leaving \\(math\\) for KaTeX."""
    maths: list[str] = []

    def stash(m):
        maths.append(m.group(0))
        return f"\x00{len(maths) - 1}\x00"

    text = MATH.sub(stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"(?<![\w~])~([^~\n]+?)~(?![\w~])", r"<code>\1</code>", text)
    text = re.sub(r"(?<![\w=])=([^=\n]+?)=(?![\w=])", r"<code>\1</code>", text)
    text = re.sub(r"(?<![\w/])/([^/\n]+?)/(?![\w/])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<strong>\1</strong>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: html.escape(maths[int(m.group(1))], quote=False), text)


def parse(org: str) -> list[dict]:
    entries, section, cur = [], "", None
    for line in org.splitlines():
        if line.startswith("* "):
            section, cur = line[2:].strip(), None
            continue
        m = ITEM.match(line)
        if m:
            cur = {"term": m.group(1).strip(), "body": m.group(2).strip(), "section": section}
            entries.append(cur)
        elif cur is not None and line.startswith("  ") and line.strip():
            cur["body"] += " " + line.strip()
        elif not line.strip():
            cur = None
    # An entry without its own /Slide:/ comes from the same slide as the entry above it:
    # the glossaries name a slide once, on the first term it introduces.
    last = ("", "")
    for e in entries:
        body = e.pop("body")
        refs = SLIDE.findall(body)
        if e["section"] != last[0]:
            last = (e["section"], "")
        if refs:
            last = (e["section"], refs[-1][1].strip())
        e["slide"] = last[1]
        e["html"] = inline(SLIDE.sub("", body).strip())
        e["term_html"] = inline(e["term"])
        e["keys"] = aliases(e["term"])
    return entries


def slide_titles(slides_html: str) -> list[str]:
    return [re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<h2[^>]*>(.*?)</h2>", slides_html, re.S)]


def term_refs(slides_html: str) -> list[str]:
    """The terms a deck asks for: data-term="..." or the text of a class="term" span."""
    refs = []
    for m in re.finditer(r'<span class="term"(?: data-term="([^"]*)")?>(.*?)</span>', slides_html, re.S):
        refs.append(m.group(1) if m.group(1) is not None else re.sub(r"<[^>]+>", "", m.group(2)))
    return refs


def lookup(entries: list[dict], ref: str) -> dict | None:
    """Exact whole-term match first, then aliases, then a plural stripped."""
    k = key(ref)
    for e in entries:
        if e["keys"][0] == k:
            return e
    for cand in (k, re.sub(r"es$", "", k), re.sub(r"s$", "", k)):
        for e in entries:
            if cand in e["keys"]:
                return e
    return None


def build(unit: Path) -> list[str]:
    """Write unit/glossary.js from unit/GLOSSARY.org. Returns warnings: slide links that
    name no slide, and terms the deck marks that the glossary lacks."""
    org = unit / "GLOSSARY.org"
    if not org.exists():
        return []
    entries = parse(org.read_text())
    slides = unit / "slides.html"
    deck = slides.read_text() if slides.exists() else ""
    titles = {title_key(t) for t in slide_titles(deck)}
    warnings = [f"{org.name}: {e['term']!r} links to missing slide {e['slide']!r}"
                for e in entries if e["slide"] and title_key(e["slide"]) not in titles]
    warnings += [f"slides.html: term {r!r} is not in {org.name}"
                 for r in dict.fromkeys(term_refs(deck)) if lookup(entries, r) is None]
    data = [{k: e[k] for k in ("term_html", "html", "section", "slide", "keys")} for e in entries]
    js = ("// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.\n"
          f"window.GLOSSARY = {json.dumps(data, ensure_ascii=False, indent=0)};\n")
    out = unit / "glossary.js"
    if not out.exists() or out.read_text() != js:
        out.write_text(js)
    return warnings
