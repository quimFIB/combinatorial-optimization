"""Unit 17 — "Then": your engine against OR-Tools CP-SAT on the same models.

Both solvers get the same decomposed models: pairwise != for queens and sudoku, count
constraints for magic series. Your engine reports nodes and propagations; CP-SAT
reports branches and conflicts, which are not the same thing (see the slides) but play
the same role.

    uv run co then 17
"""

import random
import time

from ortools.sat.python import cp_model

from colib.testing import load_lab

lab = load_lab(__file__)

HARD = [[int(ch) for ch in row] for row in
        ("800000000", "003600000", "070090200", "050007000", "000045700",
         "000100030", "001000068", "008500010", "090000400")]


class Counter(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        super().__init__()
        self.count = 0

    def on_solution_callback(self):
        self.count += 1


def cpsat(build, all_solutions=False, workers=8):
    m = cp_model.CpModel()
    build(m)
    s = cp_model.CpSolver()
    s.parameters.num_workers = 1 if all_solutions else workers
    s.parameters.max_time_in_seconds = 60
    if all_solutions:
        s.parameters.enumerate_all_solutions = True
        cb = Counter()
        t = time.perf_counter()
        s.solve(m, cb)
        return cb.count, time.perf_counter() - t, s.num_branches, s.num_conflicts
    t = time.perf_counter()
    status = s.solve(m)
    return int(status in (cp_model.OPTIMAL, cp_model.FEASIBLE)), time.perf_counter() - t, s.num_branches, s.num_conflicts


def queens_cpsat(n):
    def build(m):
        q = [m.new_int_var(0, n - 1, f"q{i}") for i in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                m.add(q[i] != q[j])
                m.add(q[i] != q[j] + (j - i))
                m.add(q[i] != q[j] - (j - i))
    return build


def sudoku_cpsat(grid):
    def build(m):
        x = [[m.new_int_var(1, 9, "") for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                if grid[r][c]:
                    m.add(x[r][c] == grid[r][c])
        groups = [[(r, c) for c in range(9)] for r in range(9)] + [[(r, c) for r in range(9)] for c in range(9)]
        groups += [[(br + r, bc + c) for r in range(3) for c in range(3)] for br in (0, 3, 6) for bc in (0, 3, 6)]
        pairs = {tuple(sorted((a, b))) for g in groups for a in g for b in g if a != b}
        for a, b in pairs:
            m.add(x[a[0]][a[1]] != x[b[0]][b[1]])
    return build


def magic_cpsat(n):
    def build(m):
        s = [m.new_int_var(0, n, f"s{i}") for i in range(n)]
        for i in range(n):
            eq = [m.new_bool_var("") for _ in range(n)]
            for j in range(n):
                m.add(s[j] == i).only_enforce_if(eq[j])
                m.add(s[j] != i).only_enforce_if(~eq[j])
            m.add(sum(eq) == s[i])
        m.add(sum(s) == n)
        m.add(sum(i * s[i] for i in range(n)) == n)
    return build


def colouring(n, p, seed):
    r = random.Random(seed)
    return [(u, v) for u in range(n) for v in range(u + 1, n) if r.random() < p]


def colouring_cpsat(n, edges, k):
    def build(m):
        c = [m.new_int_var(0, k - 1, "") for _ in range(n)]
        for u, v in edges:
            m.add(c[u] != c[v])
    return build


def row(name, mine, stats, theirs):
    count, t, branches, conflicts = theirs
    print(f"  {name:<26} {mine:>8} {stats.nodes:>9} {stats.propagations:>12} {stats.seconds:>8.2f} |"
          f" {count:>8} {branches:>9} {conflicts:>9} {t:>7.3f}")


if __name__ == "__main__":
    print(f"  {'model':<26} {'yours':>8} {'nodes':>9} {'propagations':>12} {'s':>8} |"
          f" {'CP-SAT':>8} {'branches':>9} {'conflicts':>9} {'s':>7}")
    for n in (8, 10, 11):
        sols, st = lab.solve(*lab.queens(n), all_solutions=True)
        row(f"queens {n}, all solutions", len(sols), st, cpsat(queens_cpsat(n), all_solutions=True))
    for n in (30, 60):
        sols, st = lab.solve(*lab.queens(n))
        row(f"queens {n}, one solution", len(sols), st, cpsat(queens_cpsat(n)))
    sols, st = lab.solve(*lab.sudoku(HARD), all_solutions=True)
    row("sudoku (Inkala), all", len(sols), st, cpsat(sudoku_cpsat(HARD), all_solutions=True))
    for n in (20, 40):
        sols, st = lab.solve(*lab.magic_series(n), all_solutions=True)
        row(f"magic series {n}, all", len(sols), st, cpsat(magic_cpsat(n), all_solutions=True))
    for n, seed in ((200, 0), (200, 1), (300, 0)):              # average degree 4.4: near the 3-colouring threshold
        edges = colouring(n, 4.4 / (n - 1), seed)
        sols, st = lab.solve(*lab.map_colouring(n, edges, 3), node_limit=300_000)
        found = len(sols) if st.extra["complete"] or sols else "limit"
        row(f"3-colour G({n}, 4.4/n) #{seed}", found, st, cpsat(colouring_cpsat(n, edges, 3)))
