"""`co` — the one command for working through a unit.

    co slides 01          open the unit's slides in a browser (rebuilds its glossary.js)
    co glossary [01]      rebuild glossary.js from GLOSSARY.org, for one unit or all
    co explore 01         open the unit's optional interactive figures (rebuilds its viz data)
    co viz [01]           rebuild viz-data.js for the interactive figures, one unit or all
    co site [--serve]     build the theory part (decks, glossaries, figures) as a static site in _site/
    co lab 01             open the lab sheet (README.md) in Emacs
    co test 01            run the lab's tests against your code
    co test 01 --solution run them against the reference solution
    co test 01 --solution functional
                          ... against the functional reference solution
    co then 01            run the solver comparison ("Then" step)
    co status             one progress line per unit
    co data               download Solomon's VRPTW instances (for the capstone)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNITS = ROOT / "units"


def find_unit(key: str) -> Path:
    key = key.zfill(2)
    hits = sorted(p for p in UNITS.iterdir() if p.is_dir() and p.name.startswith(key))
    if not hits:
        have = ", ".join(p.name for p in sorted(UNITS.iterdir()) if p.is_dir())
        sys.exit(f"no unit {key!r}; built so far: {have}")
    return hits[0]


def _open(path: Path):
    opener = shutil.which("xdg-open") or shutil.which("open")
    if not opener:
        print(path)
        return
    subprocess.Popen([opener, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"opened {path.relative_to(ROOT)}")


def _edit(path: Path):
    """Open a text file in Emacs: the running server if there is one, else a new frame.
    CO_EDITOR overrides, e.g. CO_EDITOR="code -g"."""
    rel = path.relative_to(ROOT)
    custom = os.environ.get("CO_EDITOR")
    if custom:
        subprocess.Popen([*custom.split(), str(path)])
        print(f"opened {rel}")
        return
    if shutil.which("emacsclient") and subprocess.call(
            ["emacsclient", "-n", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        print(f"opened {rel} in the running Emacs")
        return
    if shutil.which("emacs"):
        subprocess.Popen(["emacs", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
        print(f"opened {rel} in a new Emacs")
        return
    _open(path)


def _glossary(units, verbose=False) -> list[str]:
    """Rebuild each unit's glossary.js; print what doesn't resolve (a slide link that names
    no slide, a term the deck marks that the glossary lacks)."""
    from colib import glossary
    warnings = []
    for unit in units:
        found = glossary.build(unit)
        warnings += found
        for w in found:
            print(f"{unit.name}: {w}", file=sys.stderr)
        if verbose and (unit / "glossary.js").exists():
            print(f"built {(unit / 'glossary.js').relative_to(ROOT)}")
    return warnings


def _viz(units, verbose=False):
    """Rebuild each unit's viz-data.js from slides/viz/traces/uNN.py, where one exists."""
    sys.path.insert(0, str(ROOT))
    from slides.viz import traces
    for unit in units:
        out = traces.build(unit)
        if verbose and out:
            print(f"built {out.relative_to(ROOT)}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="co", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("slides", "lab", "explore"):
        sub.add_parser(name).add_argument("unit")
    for name in ("test", "then"):
        p = sub.add_parser(name)
        p.add_argument("unit")
        p.add_argument("--solution", nargs="?", const="imperative", choices=("imperative", "functional"),
                       help="use a reference solution instead of your lab (default: imperative)")
    sub.add_parser("glossary").add_argument("unit", nargs="?")
    sub.add_parser("viz").add_argument("unit", nargs="?")
    site = sub.add_parser("site")
    site.add_argument("--serve", action="store_true", help="then serve _site/ on http://localhost:8000")
    site.add_argument("--port", type=int, default=8000)
    sub.add_parser("status")
    sub.add_parser("data")
    args, rest = ap.parse_known_args(argv)
    if rest and args.cmd not in ("test", "then"):
        ap.error(f"unrecognized arguments: {' '.join(rest)}")

    env = dict(os.environ)
    if getattr(args, "solution", None):
        env["CO_SOLUTION"] = args.solution

    if args.cmd == "slides":
        unit = find_unit(args.unit)
        _glossary([unit])
        _open(unit / "slides.html")
    elif args.cmd == "explore":
        unit = find_unit(args.unit)
        page = unit / "explore.html"
        if not page.exists():
            sys.exit(f"{unit.name} has no interactive figures yet")
        _glossary([unit])
        _viz([unit])
        _open(page)
    elif args.cmd == "viz":
        units = [find_unit(args.unit)] if args.unit else sorted(p for p in UNITS.iterdir() if p.is_dir())
        _viz(units, verbose=True)
    elif args.cmd == "site":
        every = sorted(p for p in UNITS.iterdir() if p.is_dir())
        warnings = _glossary(every)
        _viz(every)
        out = ROOT / "_site"
        code = subprocess.call([sys.executable, str(ROOT / "slides" / "site" / "build.py"), str(out)], cwd=ROOT)
        if code or warnings:
            sys.exit(code or 1)
        if args.serve:
            print(f"serving {out.relative_to(ROOT)} on http://localhost:{args.port}  (Ctrl-C stops)")
            subprocess.call([sys.executable, "-m", "http.server", str(args.port), "--directory", str(out)])
    elif args.cmd == "glossary":
        units = [find_unit(args.unit)] if args.unit else sorted(p for p in UNITS.iterdir() if p.is_dir())
        sys.exit(1 if _glossary(units, verbose=True) else 0)
    elif args.cmd == "lab":
        _edit(find_unit(args.unit) / "lab" / "README.md")
    elif args.cmd == "test":
        lab = find_unit(args.unit) / "lab"
        sys.exit(subprocess.call([sys.executable, "-m", "pytest", str(lab), *rest],
                                 cwd=ROOT, env=env))
    elif args.cmd == "then":
        script = find_unit(args.unit) / "lab" / "then.py"
        sys.exit(subprocess.call([sys.executable, str(script), *rest], cwd=ROOT, env=env))
    elif args.cmd == "data":
        from colib import vrptw
        print(f"Solomon's instances in {vrptw.fetch().relative_to(ROOT)}")
    elif args.cmd == "status":
        sys.exit(subprocess.call([sys.executable, "-m", "pytest", str(UNITS), "-q", "--no-header",
                                  "-p", "no:warnings", "--tb=no", "-rN"], cwd=ROOT, env=env))


if __name__ == "__main__":
    main()
