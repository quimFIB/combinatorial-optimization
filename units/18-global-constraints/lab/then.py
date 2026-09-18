"""Unit 18 — "Then": what global constraints buy, and what CP-SAT does with the same models.

  1. Decomposed vs global models in your unit-17 engine: nodes, propagations, seconds.
  2. A Hall set named: on Inkala's sudoku, after pairwise != has done all it can, the
     first cell that alldifferent narrows, the values it removes there, and the cells whose
     domains force it.
  3. CP-SAT with AddAllDifferent / pairwise != and AddNoOverlap / pairwise disjunctions.

    uv run co then 18
"""

import time

from ortools.sat.python import cp_model

from colib.problems import JobShop
from colib.ref import unit
from colib.testing import load_lab

lab = load_lab(__file__)
cp = unit("17")

HARD = [[int(ch) for ch in row] for row in
        ("800000000", "003600000", "070090200", "050007000", "000045700",
         "000100030", "001000068", "008500010", "090000400")]


def compare():
    print("1. Your engine: decomposed vs global\n")
    print(f"  {'model':<28} {'':>10} {'nodes':>9} {'propagations':>12} {'s':>7}")

    def show(name, kind, stats, note=""):
        print(f"  {name:<28} {kind:>10} {stats.nodes:>9} {stats.propagations:>12} {stats.seconds:>7.2f} {note}")

    for n in (8, 10):
        _, a = cp.solve(*cp.queens(n), all_solutions=True)
        _, b = cp.solve(*lab.queens_global(n), all_solutions=True)
        show(f"queens {n}, all solutions", "pairwise", a)
        show("", "global", b)
    _, a = cp.solve(*cp.sudoku(HARD), all_solutions=True)
    _, b = cp.solve(*lab.sudoku_global(HARD), all_solutions=True)
    show("sudoku (Inkala), all", "pairwise", a)
    show("", "global", b)
    for n in (7, 8, 9):
        _, a = cp.solve(*lab.pigeonhole(n, False))
        _, b = cp.solve(*lab.pigeonhole(n, True))
        show(f"pigeonhole {n + 1} into {n}", "pairwise", a)
        show("", "global", b)
    shop = JobShop.ft06()
    for use_global, kind in ((False, "pairwise"), (True, "cumulative")):
        best, _, stats, trace = lab.minimise(*lab.jobshop(shop, 60, use_global), node_limit=100_000)
        at55 = next((nodes for v, nodes in trace if v == 55), None)
        note = f"best {best}; found 55 at node {at55}; proof {'complete' if stats.extra['complete'] else 'not finished'}"
        show("ft06 makespan (opt 55)" if not use_global else "", kind, stats, note)


def hall_example():
    print("\n2. A Hall set on Inkala's sudoku\n")
    doms, pairwise = cp.sudoku(HARD)
    _, groups = lab.sudoku_global(HARD)
    solution = cp.solve(*lab.sudoku_global(HARD))[0][0]
    store = cp.Store(doms)
    watch = cp.watches(81, pairwise)
    cp.fixpoint(store, pairwise, watch, cp.Stats())
    name = lambda c: f"r{c // 9 + 1}c{c % 9 + 1}"
    for depth in range(81):                                   # follow first-fail down the solution's branch
        for g in groups:
            out = g.prune(store.dom) or {}
            removed = [(x, a) for x, d in out.items() for a in sorted(store.dom[x] - d)]
            if removed:
                x, a = removed[0]
                S = lab.hall_set(store.dom, g.xs, g.offsets, g.xs.index(x), a)
                cells = [g.xs[i] for i in S]
                union = sorted(set().union(*(store.dom[c] for c in cells)))
                kind = "row" if len({c // 9 for c in g.xs}) == 1 else "column" if len({c % 9 for c in g.xs}) == 1 else "box"
                print(f"  {depth} decisions down the path to the solution, pairwise != has reached its fixpoint.")
                print(f"  alldifferent on the {kind} containing {name(x)} removes "
                      f"{', '.join(str(b) for y, b in removed if y == x)} from {name(x)}, "
                      f"whose domain is {sorted(store.dom[x])}, leaving {sorted(out[x])}.")
                print(f"  Hall set: {', '.join(name(c) for c in cells)}: {len(cells)} cells whose domains hold only "
                      f"{union} between them, so no other cell of the {kind} can take those values.")
                print(f"  (alldifferent removes {len(removed)} value(s) from this {kind} at this point.)")
                return
        v = cp.first_fail(store)
        store.assign(v, solution[v])
        cp.fixpoint(store, pairwise, watch, cp.Stats(), dirty=[v])


def cpsat_models():
    print("\n3. CP-SAT (8 workers for single solutions, 1 for enumeration)\n")
    print(f"  {'model':<30} {'formulation':>14} {'s':>7} {'branches':>9} {'conflicts':>9}")

    def run(name, kind, build, enumerate_all=False, objective=False):
        m = cp_model.CpModel()
        build(m)
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 60
        s.parameters.num_workers = 1 if enumerate_all else 8
        if enumerate_all:
            s.parameters.enumerate_all_solutions = True
        t = time.perf_counter()
        status = s.solve(m)
        extra = f"  makespan {s.objective_value:.0f}" if objective and status == cp_model.OPTIMAL else ""
        print(f"  {name:<30} {kind:>14} {time.perf_counter() - t:>7.3f} {s.num_branches:>9} {s.num_conflicts:>9}{extra}")

    def queens(n, glob):
        def build(m):
            q = [m.new_int_var(0, n - 1, "") for _ in range(n)]
            if glob:
                m.add_all_different(q)
                m.add_all_different(q[i] + i for i in range(n))
                m.add_all_different(q[i] - i for i in range(n))
            else:
                for i in range(n):
                    for j in range(i + 1, n):
                        m.add(q[i] != q[j])
                        m.add(q[i] + i != q[j] + j)
                        m.add(q[i] - i != q[j] - j)
        return build

    def php(n, glob):
        def build(m):
            x = [m.new_int_var(0, n - 1, "") for _ in range(n + 1)]
            if glob:
                m.add_all_different(x)
            else:
                for i in range(n + 1):
                    for j in range(i + 1, n + 1):
                        m.add(x[i] != x[j])
        return build

    def jobshop(shop, glob):
        def build(m):
            H = sum(d for job in shop.jobs for _, d in job)
            per = {k: [] for k in range(shop.machines)}
            ends = []
            for job in shop.jobs:
                prev = None
                for mach, d in job:
                    s = m.new_int_var(0, H, "")
                    per[mach].append((s, d))
                    if prev is not None:
                        m.add(s >= prev)
                    prev = s + d
                ends.append(prev)
            for ops in per.values():
                if glob:
                    m.add_no_overlap([m.new_interval_var(s, d, s + d, "") for s, d in ops])
                else:
                    for i in range(len(ops)):
                        for j in range(i + 1, len(ops)):
                            (a, da), (b, db) = ops[i], ops[j]
                            before = m.new_bool_var("")
                            m.add(a + da <= b).only_enforce_if(before)
                            m.add(b + db <= a).only_enforce_if(~before)
            mk = m.new_int_var(0, H, "")
            m.add_max_equality(mk, ends)
            m.minimize(mk)
        return build

    for glob in (False, True):
        run("queens 11, all solutions" if not glob else "", "alldifferent" if glob else "pairwise", queens(11, glob), True)
    for glob in (False, True):
        run("pigeonhole 11 into 10" if not glob else "", "alldifferent" if glob else "pairwise", php(10, glob))
    for glob in (False, True):
        run("ft06 makespan" if not glob else "", "no_overlap" if glob else "disjunctions", jobshop(JobShop.ft06(), glob),
            objective=True)


if __name__ == "__main__":
    compare()
    hall_example()
    cpsat_models()
