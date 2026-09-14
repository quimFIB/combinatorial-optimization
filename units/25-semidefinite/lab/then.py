"""Unit 25 — "Then": Goemans-Williamson against exact Max-Cut, the bound ladder, theta, and what SDPs cost.

  1. Random graphs with optima proved by CP-SAT: edge LP, triangle LP, SDP and OPT; the GW cut's
     expected, mean, worst and best ratio over 200 hyperplanes; GW followed by local search.
  2. Where the analysis is tight per edge: C5's vectors, and the angle that attains alpha_GW.
  3. Lovasz theta sandwiched between the independence number and the clique cover number.
  4. Seconds for the SDP as n grows, against the triangle LP and CP-SAT.

    uv run co then 25
"""

import itertools
import math
import random
import statistics
import time

import networkx as nx
import numpy as np
from ortools.sat.python import cp_model

from colib.problems import MaxCut
from colib.testing import load_lab

lab = load_lab(__file__)


def cpsat_maxcut(mc, limit=120):
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in range(mc.n)]
    terms = []
    for (u, v), w in zip(mc.edges, mc.weights):
        e = m.new_bool_var("")
        m.add(e <= x[u] + x[v])
        m.add(e <= 2 - x[u] - x[v])
        terms.append(w * e)
    m.add(x[0] == 0)
    m.maximize(sum(terms))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = limit
    status = s.solve(m)
    return round(s.objective_value), status == cp_model.OPTIMAL


def timed(f, *a):
    t = time.perf_counter()
    out = f(*a)
    return out, time.perf_counter() - t


def ladder():
    print("1. Max-Cut, weights 1..10, ratios to the CP-SAT optimum (5 graphs per row; GW over 200 hyperplanes)\n")
    print(f"  {'graph':>11} {'edge LP':>8} {'tri LP':>7} {'SDP':>6} | {'E[GW]':>6} {'mean':>6} {'worst':>6} {'best':>6}"
          f" {'GW+LS':>6} {'rand+LS':>8}")
    alpha, _ = lab.gw_constant()
    overall_worst = 1.0
    for n, p in ((12, 0.5), (20, 0.5), (30, 0.3), (40, 0.2)):
        cols = {k: [] for k in ("edge", "tri", "sdp", "exp", "mean", "worst", "best", "gwls", "rls")}
        for seed in range(5):
            mc = MaxCut.random(n, seed=seed, p=p)
            opt, proven = cpsat_maxcut(mc)
            assert proven, (n, p, seed)
            value, X = lab.maxcut_sdp(mc)
            V = lab.vectors_from_gram(X)
            rng = np.random.default_rng(seed)
            cuts = [lab.hyperplane_round(V, rng) for _ in range(200)]
            ws = [mc.objective(x) for x in cuts]
            best = cuts[int(np.argmax(ws))]
            r = random.Random(seed)
            rand = [r.randint(0, 1) for _ in range(n)]
            cols["edge"].append(lab.maxcut_edge_lp(mc) / opt)
            cols["tri"].append(lab.maxcut_triangle_lp(mc) / opt if n <= 30 else float("nan"))
            cols["sdp"].append(value / opt)
            cols["exp"].append(lab.expected_cut(mc, V) / opt)
            cols["mean"].append(statistics.mean(ws) / opt)
            cols["worst"].append(min(ws) / opt)
            cols["best"].append(max(ws) / opt)
            cols["gwls"].append(mc.objective(lab.local_search(mc, best)) / opt)
            cols["rls"].append(mc.objective(lab.local_search(mc, rand)) / opt)
        overall_worst = min(overall_worst, min(cols["worst"]))
        mean = {k: statistics.mean(v) for k, v in cols.items()}
        tri = "   n/a" if n > 30 else f"{mean['tri']:>7.3f}"
        print(f"  {f'G({n}, {p})':>11} {mean['edge']:>8.3f} {tri:>7} {mean['sdp']:>6.3f} | {mean['exp']:>6.3f}"
              f" {mean['mean']:>6.3f} {min(cols['worst']):>6.3f} {mean['best']:>6.3f} {mean['gwls']:>6.3f} {mean['rls']:>8.3f}")
    print(f"\n  alpha_GW = {alpha:.5f}; the single worst hyperplane over all 4000 rounds cut {overall_worst:.3f} of OPT")


def tight_angles():
    print("\n2. Per-edge ratio (angle/pi) / ((1 - cos)/2) of rounding to the SDP\n")
    alpha, theta = lab.gw_constant()
    for name, t in (("C5's SDP vectors, 4pi/5", 4 * math.pi / 5), ("the worst angle", theta),
                    ("orthogonal, pi/2", math.pi / 2), ("antipodal, pi", math.pi)):
        ratio = (t / math.pi) / ((1 - math.cos(t)) / 2)
        print(f"  {name:>26}: {math.degrees(t):6.2f} degrees   ratio {ratio:.4f}")
    c5 = MaxCut(5, ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4)), (1,) * 5)
    value, X = lab.maxcut_sdp(c5)
    V = lab.vectors_from_gram(X)
    print(f"  C5: SDP {value:.4f}, E[GW] {lab.expected_cut(c5, V):.4f}, OPT 4, E[GW]/SDP {lab.expected_cut(c5, V) / value:.4f}")


def alpha_and_cover(n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    alpha = max(len(c) for c in nx.find_cliques(nx.complement(g)))
    comp = lab.complement(n, edges)
    m = cp_model.CpModel()
    k = n
    col = [m.new_int_var(0, k - 1, "") for _ in range(n)]
    for u, v in comp:
        m.add(col[u] != col[v])
    top = m.new_int_var(0, k - 1, "")
    for c in col:
        m.add(c <= top)
    m.minimize(top)
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.solve(m)
    return alpha, round(s.objective_value) + 1


def theta():
    print("\n3. alpha(G) <= theta(G) <= chi(complement of G)\n")
    print(f"  {'graph':>18} {'alpha':>6} {'theta':>8} {'chi-bar':>8}")
    graphs = [("C5", 5, [(i, (i + 1) % 5) for i in range(5)]),
              ("C7", 7, [(i, (i + 1) % 7) for i in range(7)]),
              ("Petersen", 10, list(nx.petersen_graph().edges())),
              ("5-cube", 32, [tuple(e) for e in nx.convert_node_labels_to_integers(nx.hypercube_graph(5)).edges()])]
    for seed in range(3):
        r = random.Random(seed)
        graphs.append((f"G(14, 0.5) #{seed}", 14, [e for e in itertools.combinations(range(14), 2) if r.random() < 0.5]))
    for name, n, edges in graphs:
        a, chibar = alpha_and_cover(n, edges)
        print(f"  {name:>18} {a:>6} {lab.lovasz_theta(n, edges):>8.4f} {chibar:>8}")


def cost():
    print("\n4. Seconds: SDP (CLARABEL) against the triangle LP (HiGHS) and CP-SAT's proof, G(n, 0.3)\n")
    print(f"  {'n':>4} {'SDP s':>7} {'tri LP s':>9} {'CP-SAT s':>9}")
    for n in (15, 25, 35, 60, 100, 150):
        mc = MaxCut.random(n, seed=1, p=0.3)
        _, t_sdp = timed(lab.maxcut_sdp, mc)
        t_tri = timed(lab.maxcut_triangle_lp, mc)[1] if n <= 35 else float("nan")
        (opt, proven), t_cp = timed(cpsat_maxcut, mc, 60) if n <= 60 else ((None, False), float("nan"))
        cp_s = f"{t_cp:>9.2f}" if n <= 60 and proven else ("  timeout" if n <= 60 else "        -")
        tri_s = f"{t_tri:>9.2f}" if n <= 35 else "        -"
        print(f"  {n:>4} {t_sdp:>7.2f} {tri_s} {cp_s}")


if __name__ == "__main__":
    ladder()
    tight_angles()
    theta()
    cost()
