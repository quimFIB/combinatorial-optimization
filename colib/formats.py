"""Readers and writers for the formats the field trades instances in.

DIMACS CNF and TSPLIB (EUC_2D and explicit full matrices) for now. MPS arrives
with unit 05, which is the first unit that reads MIPLIB models.
"""

from __future__ import annotations

import math
from pathlib import Path

from colib.problems import TSP


# --------------------------- DIMACS CNF ------------------------------------

def read_cnf(path) -> tuple[int, list[list[int]]]:
    """Return (number of variables, clauses as lists of nonzero ints)."""
    nvars, clauses, cur = 0, [], []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line[0] in "c%":
            continue
        if line.startswith("p"):
            _, fmt, nv, _nc = line.split()
            assert fmt == "cnf", f"not a cnf file: {line}"
            nvars = int(nv)
            continue
        for tok in line.split():
            lit = int(tok)
            if lit == 0:
                clauses.append(cur)
                cur = []
            else:
                cur.append(lit)
    if cur:
        clauses.append(cur)
    return nvars, clauses


def write_cnf(path, nvars: int, clauses, comment: str = "") -> None:
    lines = [f"c {c}" for c in comment.splitlines()]
    lines.append(f"p cnf {nvars} {len(clauses)}")
    lines += [" ".join(map(str, cl)) + " 0" for cl in clauses]
    Path(path).write_text("\n".join(lines) + "\n")


# --------------------------- TSPLIB ----------------------------------------

_TSPLIB_KEYS = {"NAME", "TYPE", "COMMENT", "DIMENSION", "CAPACITY",
                "EDGE_WEIGHT_TYPE", "EDGE_WEIGHT_FORMAT", "DISPLAY_DATA_TYPE"}

def read_tsplib(path) -> TSP:
    spec, section, coords, weights = {}, None, [], []
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line == "EOF":
            continue
        if ":" in line and line.split(":")[0].strip() in _TSPLIB_KEYS:
            k, v = line.split(":", 1)
            spec[k.strip()] = v.strip()
            section = None
            continue
        if line.endswith("_SECTION"):
            section = line
            continue
        if section == "NODE_COORD_SECTION":
            _, x, y = line.split()[:3]
            coords.append((float(x), float(y)))
        elif section == "EDGE_WEIGHT_SECTION":
            weights += [int(float(t)) for t in line.split()]

    n = int(spec["DIMENSION"])
    kind = spec.get("EDGE_WEIGHT_TYPE")
    if kind == "EUC_2D":
        d = [[int(math.dist(a, b) + 0.5) for b in coords] for a in coords]
    elif kind == "EXPLICIT" and spec.get("EDGE_WEIGHT_FORMAT") == "FULL_MATRIX":
        d = [weights[i * n:(i + 1) * n] for i in range(n)]
    else:
        raise NotImplementedError(f"TSPLIB {kind}/{spec.get('EDGE_WEIGHT_FORMAT')}")
    return TSP(tuple(tuple(r) for r in d))


def write_tsplib(path, tsp: TSP, name: str = "instance") -> None:
    n = tsp.n
    lines = [f"NAME : {name}", "TYPE : TSP", f"DIMENSION : {n}",
             "EDGE_WEIGHT_TYPE : EXPLICIT", "EDGE_WEIGHT_FORMAT : FULL_MATRIX",
             "EDGE_WEIGHT_SECTION"]
    lines += [" ".join(map(str, row)) for row in tsp.dist]
    lines.append("EOF")
    Path(path).write_text("\n".join(lines) + "\n")
