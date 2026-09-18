"""Unit 04 — "Then": the central path, where floating point ends it, and IPM vs simplex.

  1. The central path of a 2-variable LP (unit 01's polygon), plotted.
  2. The pure barrier method as t grows: the duality gap should be m/t, and
     floating point stops that somewhere past t = 1e6.
  3. HiGHS: dual simplex against interior point on random sparse LPs of growing
     size (cold solves). Add --big for n = 10 000 and 20 000 (about 4 minutes).
  4. HiGHS: re-solve after adding one constraint. Simplex warm-starts; IPM restarts.
  5. The ellipsoid method: iterations used against the volume bound, n = 2..8.

    uv run co then 04 [--big]
"""

import math
import sys
import time
from pathlib import Path

import numpy as np

from colib.polyhedra import inscribed_radius, random_polytope, shifted_polytope
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"


def part1():
    print("\n1 · Central path: max 2x + y over x, y >= 0, x + y <= 4, x - y <= 1   (optimum 6.5 at (2.5, 1.5))")
    A = np.array([[-1.0, 0], [0, -1.0], [1, 1], [1, -1]])
    b = np.array([0.0, 0, 4, 1])
    c = np.array([2.0, 1.0])
    path = lab.central_path(A, b, c, np.array([0.5, 0.5]), t0=0.01, mu=3.0, eps=1e-4)
    print(f"   {'t':>9}{'x':>24}{'c.x':>10}{'gap m/t':>10}")
    for t, x, y in [path[i] for i in sorted(set(range(0, len(path), 2)) | {len(path) - 1})]:
        print(f"   {t:>9.3g}   ({x[0]:9.5f}, {x[1]:9.5f}){c @ x:>10.5f}{len(b) / t:>10.2e}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        OUT.mkdir(exist_ok=True)
        fig, ax = plt.subplots(figsize=(5, 5))
        poly = np.array([[0, 0], [1, 0], [2.5, 1.5], [0, 4], [0, 0]])
        ax.fill(poly[:, 0], poly[:, 1], alpha=0.15)
        ax.plot(poly[:, 0], poly[:, 1], lw=1.5)
        xs = np.array([p[1] for p in path])
        ax.plot(xs[:, 0], xs[:, 1], "o-", ms=3, label="central path x(t)")
        ax.annotate("analytic centre\n(t small)", xs[0], textcoords="offset points", xytext=(10, 10))
        ax.plot([2.5], [1.5], "k*", ms=12, label="optimum")
        ax.set_aspect("equal")
        ax.legend(loc="upper right")
        fig.tight_layout()
        fig.savefig(OUT / "central_path.png", dpi=130)
        print(f"   plot: {(OUT / 'central_path.png').relative_to(Path.cwd())}")
    except ImportError:
        pass


def part2():
    print("\n2 · Where floating point ends the pure barrier method (3 variables, 14 constraints)")
    rows = random_polytope(3, 8, seed=0)
    A = np.array([a for a, _ in rows], float)
    b = np.array([bb for _, bb in rows], float)
    c = np.array([4.0, 2.0, 0.0])
    m = len(b)
    x = np.zeros(3)
    print(f"   {'t':>8}{'m/t':>11}{'b.y - c.x':>12}{'Newton steps':>14}{'min slack':>11}")
    for k in range(10):
        t = 10.0 ** k
        x, steps = lab.newton_center(A, b, c, x, t)
        s = b - A @ x
        y = 1 / (t * s)
        print(f"   {t:>8.0e}{m / t:>11.2e}{b @ y - c @ x:>12.2e}{steps:>14}{s.min():>11.1e}")
    print("   The gap tracks m/t until t ~ 1e6; past that the Hessian (condition ~ 1/min slack^2)\n   is too ill-conditioned and the results turn erratic (look at t = 1e7).")
    print("   Production IPMs solve the primal-dual system instead, which stays usable far longer.")


def sparse_lp(n, seed, per_col=4):
    import scipy.sparse as sp
    rng = np.random.default_rng(seed)
    m = n // 2
    rows = rng.integers(0, m, size=n * per_col)
    cols = np.repeat(np.arange(n), per_col)
    A = sp.csr_matrix((rng.uniform(0.1, 1.0, n * per_col), (rows, cols)), shape=(m, n))
    x0 = rng.uniform(0, 1, n)
    return A, A @ x0 + rng.uniform(0.1, 1.0, m), rng.uniform(0, 1, n)


def highs(A, b, c, solver):
    import highspy
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("presolve", "off")
    h.setOptionValue("solver", solver)
    if solver == "ipm":
        h.setOptionValue("run_crossover", "off")
    m, n = A.shape
    inf = highspy.kHighsInf
    h.addVars(n, np.zeros(n), np.full(n, inf))
    h.changeColsCost(n, np.arange(n, dtype=np.int32), -c)
    h.addRows(m, np.full(m, -inf), b, A.nnz, A.indptr[:-1].astype(np.int32),
              A.indices.astype(np.int32), A.data)
    t = time.perf_counter()
    h.run()
    return h, time.perf_counter() - t


def part3(big):
    print("\n3 · HiGHS cold solves: dual simplex vs interior point (random sparse, 4 nonzeros/column, presolve off)")
    print(f"   {'n':>7}{'simplex s':>11}{'iters':>8}{'IPM s':>9}{'iters':>7}")
    sizes = [100, 300, 1000, 3000] + ([10000, 20000] if big else [])
    for n in sizes:
        A, b, c = sparse_lp(n, 1)
        hs, ts = highs(A, b, c, "simplex")
        hi, ti = highs(A, b, c, "ipm")
        print(f"   {n:>7}{ts:>11.3f}{hs.getInfo().simplex_iteration_count:>8}"
              f"{ti:>9.3f}{hi.getInfo().ipm_iteration_count:>7}", flush=True)
    print("   IPM iterations barely grow with n; simplex iterations grow faster than n.")


def part4():
    import highspy
    print("\n4 · Re-solve after adding one constraint (n = 3000)")
    A, b, c = sparse_lp(3000, 2)
    rng = np.random.default_rng(7)
    idx = rng.choice(3000, 20, replace=False).astype(np.int32)
    vals = rng.uniform(0.5, 1, 20)
    for solver in ("simplex", "ipm"):
        h, cold = highs(A, b, c, solver)
        x = np.array(h.getSolution().col_value)
        h.addRow(-highspy.kHighsInf, float(vals @ x[idx]) * 0.9, 20, idx, vals)
        t = time.perf_counter()
        h.run()
        warm = time.perf_counter() - t
        info = h.getInfo()
        its = info.simplex_iteration_count if solver == "simplex" else info.ipm_iteration_count
        print(f"   {solver:<8} cold {cold:6.3f} s    re-solve {warm:6.3f} s  ({its} iterations)")
    print("   The simplex basis survives the change; the interior point starts over.")


def part5():
    print("\n5 · Ellipsoid method: iterations used vs the volume bound (R = 100, shifted polytopes)")
    print(f"   {'n':>3}{'mean iters':>12}{'max iters':>11}{'mean bound':>12}")
    for n in range(2, 9):
        used, bounds = [], []
        for seed in range(10):
            A, b, p = shifted_polytope(n, 3 * n, seed=seed)
            bound = lab.iteration_bound(n, 100, inscribed_radius(A, b, p))
            x, k = lab.ellipsoid_feasible(A, b, R=100, max_iter=bound)
            used.append(k if x is not None else math.inf)
            bounds.append(bound)
        print(f"   {n:>3}{np.mean(used):>12.1f}{max(used):>11}{np.mean(bounds):>12.0f}")
    print("   The bound is what makes LP polynomial in theory; nobody solves LPs this way.")


if __name__ == "__main__":
    part1()
    part2()
    part3("--big" in sys.argv)
    part4()
    part5()
