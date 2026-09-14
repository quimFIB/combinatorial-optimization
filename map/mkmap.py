#!/usr/bin/env python3
"""Emit the dependency map for CURRICULUM.html.

The map is hand-laid-out: coordinates below are chosen, not computed by a
layout engine, because the *shape* is the argument — three trunks descending
from one root, converging into the parts that need all three.

Run:  python3 map/mkmap.py
It rewrites the region between <!--MAP:BEGIN--> and <!--MAP:END--> in
CURRICULUM.html, in place.
"""

import pathlib
import re

W, H = 196, 44          # trunk node
SW, SH = 175, 40        # satellite node

# --------------------------------------------------------------------------
# nodes: id -> (centre x, top y, width, height, label, colour token)
# --------------------------------------------------------------------------

A, SAT, B, C = 150, 352, 540, 915   # column centres

NODES = {
    "u0":  (540, 24, 260, 44, "00  Models & an oracle", "root"),

    # trunk A — the polyhedral line
    "u1":  (A, 110, W, H, "01  Polyhedra · Farkas", "lp"),
    "u2":  (A, 180, W, H, "02  Simplex", "lp"),
    "u3":  (A, 250, W, H, "03  Duality", "lp"),
    "u5":  (A, 320, W, H, "05  Formulations & gaps", "ip"),
    "u7":  (A, 390, W, H, "07  Branch & bound", "ip"),
    "u8":  (A, 460, W, H, "08  Cutting planes", "ip"),
    "u10": (A, 530, W, H, "10  Column generation", "ip"),
    "u11": (A, 600, W, H, "11  Lagrangian relaxation", "ip"),
    # satellites off trunk A
    "u4":  (SAT, 180, SW, SH, "04  Ellipsoid & IPM", "lp"),
    "u6":  (SAT, 320, SW, SH, "06  Unimodularity", "ip"),
    "u9":  (SAT, 460, SW, SH, "09  Separation ⇔ opt.", "ip"),
    "u12": (SAT, 530, SW, SH, "12  Benders", "ip"),

    # trunk B — the combinatorial line
    "u13": (B, 110, W, H, "13  Matroids & greedy", "comb"),
    "u14": (B, 180, W, H, "14  Network flows", "comb"),
    "u15": (B, 250, W, H, "15  Matching", "comb"),
    "u16": (B, 320, W, H, "16  DP & treewidth", "comb"),

    # trunk C — the constraint line
    "u17": (C, 110, W, H, "17  CSP & propagation", "cp"),
    "u18": (C, 180, W, H, "18  Global constraints", "cp"),
    "u19": (C, 250, W, H, "19  CP search & LNS", "cp"),
    "u20": (C, 320, W, H, "20  SAT & CDCL", "cp"),
    "u21": (C, 390, W, H, "21  Lazy clause generation", "cp"),

    # part V — where they converge
    "u22": (150, 745, 190, H, "22  Hardness & gaps", "apx"),
    "u23": (410, 745, 190, H, "23  Approximation algs", "apx"),
    "u24": (670, 745, 190, H, "24  Rounding · primal–dual", "apx"),
    "u25": (930, 745, 190, H, "25  SDP · Goemans–W.", "apx"),
    "u26": (540, 820, 230, H, "26  Metaheuristics", "apx"),

    # part VI
    "u27": (410, 920, 200, H, "27  Solver practice", "prac"),
    "u28": (670, 920, 200, H, "28  Experimental method", "prac"),

    # part VII — coda
    "u29": (290, 1015, 200, H, "29  Convexity & gradients", "coda"),
    "u30": (540, 1015, 200, H, "30  Autodiff", "coda"),
    "u31": (790, 1015, 210, H, "31  Discrete ↔ differentiable", "coda"),

    "cap": (540, 1105, 300, 48, "CAPSTONE   one problem, four ways", "root"),
}

# --------------------------------------------------------------------------
# edges: (src, src side, dst, dst side, dashed?)
# --------------------------------------------------------------------------

EDGES = [
    ("u0", "b", "u1", "t", 0), ("u0", "b", "u13", "t", 0), ("u0", "b", "u17", "t", 0),

    # trunk A
    ("u1", "b", "u2", "t", 0), ("u2", "b", "u3", "t", 0), ("u3", "b", "u5", "t", 0),
    ("u5", "b", "u7", "t", 0), ("u7", "b", "u8", "t", 0), ("u8", "b", "u10", "t", 0),
    ("u10", "b", "u11", "t", 0),
    ("u1", "r", "u4", "l", 0), ("u3", "r", "u6", "l", 0),
    ("u8", "r", "u9", "l", 0), ("u10", "r", "u12", "l", 0),
    ("u4", "b", "u9", "t", 1),

    # trunk B
    ("u13", "b", "u14", "t", 0), ("u14", "b", "u15", "t", 0), ("u15", "b", "u16", "t", 0),

    # trunk C
    ("u17", "b", "u18", "t", 0), ("u18", "b", "u19", "t", 0),
    ("u17", "r", "u20", "r", 0), ("u20", "b", "u21", "t", 0), ("u19", "l", "u21", "l", 0),

    # cross-trunk (dashed): the places one tradition needs another
    ("u15", "r", "u18", "l", 1),     # Regin's alldifferent is a matching filter
    ("u16", "l", "u11", "r", 1),     # Held-Karp bound reuses the DP
    ("u19", "b", "u26", "t", 1),     # LNS is where CP meets local search
    ("u15", "b", "u23", "t", 1),     # Christofides needs perfect matching

    # converge into part V
    ("u11", "b", "u22", "t", 0),
    ("u16", "b", "u23", "t", 0),
    ("u21", "b", "u25", "t", 0),
    ("u22", "r", "u23", "l", 0), ("u23", "r", "u24", "l", 0), ("u24", "r", "u25", "l", 0),
    ("u24", "b", "u26", "t", 0),

    # part VI, VII, capstone
    ("u26", "b", "u27", "t", 0), ("u26", "b", "u28", "t", 0), ("u27", "r", "u28", "l", 0),
    ("u28", "b", "u30", "t", 0),
    ("u29", "r", "u30", "l", 0), ("u30", "r", "u31", "l", 0),
    ("u31", "b", "cap", "t", 0), ("u28", "b", "cap", "t", 0),
]

# hand-routed: learning-to-branch closes the loop from part II to the coda,
# down the left gutter so it crosses nothing.
GUTTER = ("M 52 412 C 22 412 22 424 22 440 L 22 1071 C 22 1085 32 1085 46 1085 "
          "L 776 1085 C 786 1085 790 1081 790 1071 L 790 1059")

BANDS = [
    (715, "PART V — when exact is hopeless"),
    (890, "PART VI — making it real"),
    (985, "PART VII — coda: the continuous cousin"),
]


def port(node, side):
    cx, y, w, h, _, _ = NODES[node]
    if side == "t":
        return cx, y, 0, -1
    if side == "b":
        return cx, y + h, 0, 1
    if side == "l":
        return cx - w / 2, y + h / 2, -1, 0
    return cx + w / 2, y + h / 2, 1, 0


def path(src, ss, dst, ds):
    x1, y1, dx1, dy1 = port(src, ss)
    x2, y2, dx2, dy2 = port(dst, ds)
    d = min(200.0, max(28.0, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2.6))
    c1 = (x1 + dx1 * d, y1 + dy1 * d)
    c2 = (x2 + dx2 * d, y2 + dy2 * d)
    return (f"M {x1:.1f} {y1:.1f} C {c1[0]:.1f} {c1[1]:.1f} "
            f"{c2[0]:.1f} {c2[1]:.1f} {x2:.1f} {y2:.1f}")


def build():
    out = []
    out.append('<svg class="map" viewBox="0 0 1080 1190" role="img" '
               'aria-label="Dependency map of the 32 units: three trunks '
               'descending from unit 00, converging into parts V, VI and VII.">')
    out.append("""  <defs>
    <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
            markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 9 5 L 0 9 z" fill="var(--rule-strong)"/>
    </marker>
  </defs>""")

    # band rules first, so edges sit above them
    for y, label in BANDS:
        out.append(f'  <line class="band" x1="8" y1="{y}" x2="1072" y2="{y}"/>')
        out.append(f'  <text class="bandlabel" x="8" y="{y - 8}">{label}</text>')

    for src, ss, dst, ds, dashed in EDGES:
        cls = "edge dashed" if dashed else "edge"
        out.append(f'  <path class="{cls}" d="{path(src, ss, dst, ds)}" '
                   'marker-end="url(#ar)"/>')
    out.append(f'  <path class="edge dashed" d="{GUTTER}" marker-end="url(#ar)"/>')
    out.append('  <text class="gutlabel" x="30" y="560" '
               'transform="rotate(-90 30 560)">learning to branch</text>')

    for nid, (cx, y, w, h, label, tone) in NODES.items():
        x = cx - w / 2
        out.append(f'  <g class="n n-{tone}">')
        out.append(f'    <rect x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="4"/>')
        out.append(f'    <rect class="bar" x="{x:.1f}" y="{y}" width="4" height="{h}"/>')
        fs = 11 if w <= SW else 11.5
        out.append(f'    <text x="{x + 14:.1f}" y="{y + h / 2 + 4:.1f}" '
                   f'font-size="{fs}">{label}</text>')
        out.append("  </g>")

    out.append("</svg>")
    return "\n".join(out)


def main():
    here = pathlib.Path(__file__).resolve().parent.parent
    target = here / "CURRICULUM.html"
    html = target.read_text(encoding="utf-8")
    new = re.sub(
        r"(<!--MAP:BEGIN-->).*?(<!--MAP:END-->)",
        lambda m: m.group(1) + "\n" + build() + "\n" + m.group(2),
        html,
        flags=re.S,
    )
    if new == html:
        raise SystemExit("map markers not found (or map unchanged)")
    target.write_text(new, encoding="utf-8")
    print(f"map spliced into {target}")


if __name__ == "__main__":
    main()
