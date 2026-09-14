"""`co` — the one command for working through a unit.

    co slides 01          open the unit's slides in a browser
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


def main(argv=None):
    ap = argparse.ArgumentParser(prog="co", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("slides", "lab"):
        sub.add_parser(name).add_argument("unit")
    for name in ("test", "then"):
        p = sub.add_parser(name)
        p.add_argument("unit")
        p.add_argument("--solution", nargs="?", const="imperative", choices=("imperative", "functional"),
                       help="use a reference solution instead of your lab (default: imperative)")
    sub.add_parser("status")
    sub.add_parser("data")
    args, rest = ap.parse_known_args(argv)
    if rest and args.cmd not in ("test", "then"):
        ap.error(f"unrecognized arguments: {' '.join(rest)}")

    env = dict(os.environ)
    if getattr(args, "solution", None):
        env["CO_SOLUTION"] = args.solution

    if args.cmd == "slides":
        _open(find_unit(args.unit) / "slides.html")
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
