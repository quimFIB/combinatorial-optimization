"""Reference implementations of earlier units, for later labs to build on.

Unit 07's branch-and-bound needs a simplex, unit 18's alldifferent filter needs
a maximum matching, unit 21 needs a CDCL solver. If later labs imported *your*
earlier code, an unfinished unit 02 would break unit 07. So they import the
tested reference solution instead:

    simplex = colib.ref.unit("02")          # units/02-*/lab/solution/lab.py
    simplex.two_phase(A, b, c)

To use your own implementation of an earlier unit in a later lab, set
CO_MINE to a comma-separated list of unit numbers, e.g. CO_MINE=02,15. Then
`unit("02")` loads units/02-*/lab/lab.py — your file — instead.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _unit_dir(key: str) -> Path:
    key = key.zfill(2)
    hits = sorted(p for p in (ROOT / "units").iterdir() if p.is_dir() and p.name.startswith(key + "-"))
    if not hits:
        raise ImportError(f"no unit {key} under {ROOT / 'units'}")
    return hits[0]


def unit(key: str):
    key = key.zfill(2)
    mine = {k.strip().zfill(2) for k in os.environ.get("CO_MINE", "").split(",") if k.strip()}
    lab = _unit_dir(key) / "lab"
    path = lab / "lab.py" if key in mine else lab / "solution" / "lab.py"
    name = f"_coref_{key}_{'mine' if key in mine else 'ref'}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
