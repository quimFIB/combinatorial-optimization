"""Unit 01 — "Then": your polyhedral tools against the real ones.

Three measurements, all using your lab.py:

  1. Fourier–Motzkin blow-up: constraints after each elimination (the
     pairwise worst case is m -> m^2/4 per step), against the true number of
     facets of the projection, which qhull computes. Most of what FM produces
     is redundant.
  2. Vertex enumeration: your C(m, n) basis walk against qhull as m grows.
     Same answer; watch the time ratio.
  3. A Farkas certificate printed as a proof you can check by hand, and
     HiGHS's verdict on the same system.

    uv run co then 01             # your lab
    uv run co then 01 --solution  # the reference
"""

import math
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull, HalfspaceIntersection

from colib.polyhedra import random_infeasible, random_polytope
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"


def fmt_row(a, b, names="xyzuvw"):
    terms = [f"{c:+d}{names[j]}" for j, c in enumerate(a) if c]
    return (" ".join(terms) if terms else "0") + f" <= {b}"


def part1_blowup():
    print("\n1 · Fourier–Motzkin blow-up   (n = 6 variables, m = 14 cuts + box)")
    print(f"{'eliminated':>11}{'constraints':>13}{'true facets':>13}{'seconds':>10}")
    system = random_polytope(6, 14, seed=7)
    n = 6
    rows_series, facet_series = [len(system)], [len(system)]
    print(f"{0:>11}{len(system):>13}{'':>13}{'':>10}")
    for k in range(n - 1):
        t = time.perf_counter()
        system = lab.eliminate(system, k)
        dt = time.perf_counter() - t
        remaining = list(range(k + 1, n))
        facets = true_facets(system, remaining)
        rows_series.append(len(system))
        facet_series.append(facets)
        print(f"{k + 1:>11}{len(system):>13}{facets:>13}{dt:>10.2f}")
        if len(system) > 20000:
            print(f"{'':>11}stopping: the next step would form ~{(len(system) // 2) ** 2:,} pairs")
            break
    return rows_series, facet_series


def true_facets(system, keep):
    """Facets of the projection onto the coordinates `keep`, via qhull."""
    if len(keep) == 1:
        return 2
    A = np.array([[a[j] for j in keep] for a, _ in system], dtype=float)
    b = np.array([b for _, b in system], dtype=float)
    pts = HalfspaceIntersection(np.c_[A, -b], np.zeros(len(keep))).intersections
    # qhull triangulates facets, so one facet can appear as several equal equations
    return len({tuple(e) for e in ConvexHull(pts).equations.round(6)})


def part2_vertices():
    print("\n2 · Vertex enumeration in R^3   (your basis walk vs qhull)")
    print(f"{'cuts m':>7}{'bases':>9}{'vertices':>10}{'agree':>7}{'yours s':>10}{'qhull s':>10}{'ratio':>8}")
    series = []
    for m in (4, 8, 16, 24, 32, 40):
        system = random_polytope(3, m, seed=m)
        t = time.perf_counter()
        mine = lab.vertices(system)
        t_mine = time.perf_counter() - t
        hs = np.array([[*a, -b] for a, b in system], dtype=float)
        t = time.perf_counter()
        ref = HalfspaceIntersection(hs, np.zeros(3)).intersections
        t_ref = time.perf_counter() - t
        agree = {tuple(np.round(np.array(v, dtype=float), 6)) for v in mine} == \
                {tuple(np.round(p, 6)) for p in ref}
        rows = len(system)
        series.append((rows, t_mine, t_ref))
        print(f"{m:>7}{math.comb(rows, 3):>9,}{len(mine):>10}{'yes' if agree else 'NO':>7}"
              f"{t_mine:>10.3f}{t_ref:>10.4f}{t_mine / max(t_ref, 1e-6):>8.0f}×")
    return series


def part3_certificate():
    print("\n3 · A Farkas certificate, as a proof")
    system = random_infeasible(3, 5, seed=4)
    for i, (a, b) in enumerate(system):
        print(f"   ({i}) {fmt_row(a, b)}")
    y = lab.farkas_certificate(system)
    if y is None:
        print("   your farkas_certificate returned None — but this system is infeasible")
        return
    print("\n   multiply and add:  " + "  +  ".join(f"{v}·({i})" for i, v in enumerate(y) if v))
    n = len(system[0][0])
    lhs = [sum(v * a[j] for v, (a, _) in zip(y, system)) for j in range(n)]
    rhs = sum(v * b for v, (_, b) in zip(y, system))
    print(f"   gives              {fmt_row(lhs, rhs)}   — false for every x, so no x exists.")
    A = np.array([a for a, _ in system], dtype=float)
    res = linprog(np.zeros(n), A_ub=A, b_ub=[b for _, b in system],
                  bounds=[(None, None)] * n, method="highs")
    print(f"   HiGHS says: {res.message}")
    print("   (HiGHS reached that verdict in floating point. Your certificate is exact integers.)")


def plot(blowup, verts):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    OUT.mkdir(exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    rows, facets = blowup
    ax1.semilogy(range(len(rows)), rows, "o-", label="FM constraints")
    ax1.semilogy(range(len(facets)), facets, "s--", label="true facets")
    ax1.set_xticks(range(len(rows)))
    ax1.set_xlabel("variables eliminated")
    ax1.set_title("Fourier–Motzkin: most constraints are redundant")
    ax1.legend()
    ax2.loglog([v[0] for v in verts], [v[1] for v in verts], "o-", label="basis enumeration")
    ax2.loglog([v[0] for v in verts], [v[2] for v in verts], "s--", label="qhull")
    ax2.set_xlabel("constraints (incl. box)")
    ax2.set_ylabel("seconds")
    ax2.set_title("Vertices in R³")
    ax2.legend()
    fig.tight_layout()
    fig.savefig(OUT / "then.png", dpi=130)
    print(f"\nplot: {(OUT / 'then.png').relative_to(Path.cwd())}")


if __name__ == "__main__":
    b = part1_blowup()
    v = part2_vertices()
    part3_certificate()
    plot(b, v)
