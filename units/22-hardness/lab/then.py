"""Unit 22 — "Then": both sides of each reduction, solved by CP-SAT, and the FPTAS measured.

  1. 3-SAT -> vertex cover: CP-SAT on the formula and on the cover instance; satisfiable exactly
     when the minimum cover is n + 2m, and the size blow-up.
  2. Vertex cover -> set cover: the two optima agree, instance by instance.
  3. The knapsack FPTAS: seconds and the actual loss against the guaranteed 1 - eps, next to the
     exact weight DP (unit 16) and CP-SAT.

    uv run co then 22
"""

import random
import time

from ortools.sat.python import cp_model

from colib.problems import VertexCover
from colib.ref import unit
from colib.testing import load_lab

lab = load_lab(__file__)


def timed(f, *args):
    t = time.perf_counter()
    out = f(*args)
    return out, time.perf_counter() - t


def cpsat_sat(nvars, clauses):
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in range(nvars)]
    for c in clauses:
        m.add_bool_or([x[abs(l) - 1] if l > 0 else ~x[abs(l) - 1] for l in c])
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    return s.solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def cpsat_vc(vc):
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in range(vc.n)]
    for a, b in vc.edges:
        m.add_bool_or([x[a], x[b]])
    m.minimize(sum(x))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = 60
    status = s.solve(m)
    return round(s.objective_value), status == cp_model.OPTIMAL


def cpsat_sc(sc):
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in range(sc.n)]
    for e in range(sc.universe):
        m.add_bool_or([x[i] for i, s in enumerate(sc.sets) if e in s])
    m.minimize(sum(c * xi for c, xi in zip(sc.costs, x)))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = 60
    status = s.solve(m)
    return round(s.objective_value), status == cp_model.OPTIMAL


def rand3cnf(n, m, seed):
    r = random.Random(seed)
    return [[v if r.random() < 0.5 else -v for v in r.sample(range(1, n + 1), 3)] for _ in range(m)]


def sat_vs_vc():
    print("1. 3-SAT -> vertex cover, both sides by CP-SAT\n")
    print(f"  {'n':>3} {'m':>4} {'SAT?':>5} {'s':>6} | {'vertices':>8} {'edges':>6} {'k = n+2m':>9} {'min cover':>9} {'s':>6}  agrees")
    for n, ratio, seed in ((20, 3.0, 1), (20, 5.0, 2), (40, 4.26, 3), (40, 4.26, 4), (60, 4.26, 5), (60, 6.0, 6)):
        clauses = rand3cnf(n, int(ratio * n), seed)
        satisfiable, t1 = timed(cpsat_sat, n, clauses)
        vc, k = lab.sat_to_vertex_cover(n, clauses)
        (value, optimal), t2 = timed(cpsat_vc, vc)
        agree = optimal and ((value == k) == satisfiable) and value >= k
        print(f"  {n:>3} {len(clauses):>4} {str(satisfiable):>5} {t1:>6.3f} | {vc.n:>8} {len(vc.edges):>6} {k:>9} "
              f"{value:>9} {t2:>6.2f}  {agree}")


def vc_vs_sc():
    print("\n2. Vertex cover -> set cover, optima by CP-SAT\n")
    print(f"  {'graph':>14} {'VC opt':>7} {'s':>6} | {'SC opt':>7} {'s':>6}  equal")
    for n, p in ((30, 0.2), (60, 0.1), (100, 0.05), (150, 0.04)):
        vc = VertexCover.random(n, seed=n, p=p)
        (v1, o1), t1 = timed(cpsat_vc, vc)
        (v2, o2), t2 = timed(cpsat_sc, lab.vertex_cover_to_set_cover(vc))
        print(f"  {f'G({n}, {p})':>14} {v1:>7} {t1:>6.2f} | {v2:>7} {t2:>6.2f}  {o1 and o2 and v1 == v2}")


def fptas():
    print("\n3. Knapsack: FPTAS vs exact (100 items, values up to 10^6, weights up to 10^4)\n")
    r = random.Random(7)
    n = 100
    values = [r.randint(1, 10 ** 6) for _ in range(n)]
    weights = [r.randint(1, 10 ** 4) for _ in range(n)]
    C = sum(weights) // 3
    (opt, _), t_exact = timed(unit("16").knapsack, values, weights, C)
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in range(n)]
    m.add(sum(w * xi for w, xi in zip(weights, x)) <= C)
    m.maximize(sum(v * xi for v, xi in zip(values, x)))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    _, t_cpsat = timed(s.solve, m)
    print(f"  exact weight DP (unit 16): {t_exact:.2f} s, optimum {opt};  CP-SAT: {t_cpsat:.3f} s, {s.objective_value:.0f}\n")
    print(f"  {'eps':>5} {'value':>10} {'loss':>9} {'allowed':>8} {'s':>7}")
    for eps in (0.5, 0.2, 0.1, 0.05, 0.02):
        (value, _), t = timed(lab.knapsack_fptas, values, weights, C, eps)
        print(f"  {eps:>5} {value:>10} {100 * (opt - value) / opt:>8.3f}% {100 * eps:>7.0f}% {t:>7.2f}")


if __name__ == "__main__":
    sat_vs_vc()
    vc_vs_sc()
    fptas()
