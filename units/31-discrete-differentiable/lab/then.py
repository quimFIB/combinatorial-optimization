"""Unit 31 — "Then": Sinkhorn against the Hungarian algorithm, gradient estimators side by side, an argmin
layer checked three ways, and a learned branching rule evaluated with unit 28's method.

  1. Assignment, n = 50 to 200: exact (unit 15's Hungarian) against Sinkhorn at three temperatures,
     rounded greedily; mean cost per row and seconds.
  2. The gradient of E[f(k)] for a 10-way categorical, from one sample: REINFORCE and straight-through
     Gumbel-softmax at several temperatures; bias and spread over 2 000 draws.
  3. An argmin layer for a box-constrained QP: the implicit-function Jacobian against finite differences and
     against JAX differentiating through 500 unrolled projected-gradient steps. (cvxpylayers isn't installed.)
  4. Branching: a linear rule trained to imitate strong branching on 10 knapsacks, tested on 20 held-out
     ones against most-fractional, pseudocost and strong branching. Node counts, shifted geometric means,
     Wilcoxon with Holm, using your unit-28 functions.

    uv run co then 31
"""

import math
import time

import cvxpy as cp
import jax
import jax.numpy as jnp
import numpy as np
from scipy.optimize import linear_sum_assignment

from colib.bb import multi_knapsack
from colib.ref import unit
from colib.testing import load_lab

jax.config.update("jax_enable_x64", True)
lab = load_lab(__file__)


def timed(f, *a):
    t = time.perf_counter()
    out = f(*a)
    return out, time.perf_counter() - t


def assignment():
    print("1. Assignment: exact against Sinkhorn + greedy rounding (costs uniform in [0, 1]; mean cost per row)\n")
    hungarian = unit("15").hungarian
    print(f"  {'n':>4} {'optimal':>8} {'Hungarian s':>12}   {'eps':>6} {'iters':>6} {'rounded':>8} {'seconds':>8} {'row-sum error':>14}")
    for n in (50, 100, 200):
        C = np.random.default_rng(n).uniform(0, 1, (n, n))
        _, t_h = timed(hungarian, C.tolist())
        r, c = linear_sum_assignment(C)
        opt = float(C[r, c].mean())
        first = True
        for eps, iters in ((0.05, 300), (0.01, 1500), (0.002, 6000)):
            P, t = timed(lab.sinkhorn, C, eps, iters)
            perm = lab.round_to_permutation(P)
            err = float(np.abs(P.sum(axis=1) - 1).max())
            left = f"{n:>4} {opt:>8.4f} {t_h:>10.3f} s" if first else " " * 26
            print(f"  {left}   {eps:>6} {iters:>6} {lab.assignment_cost(C, perm) / n:>8.4f} {t:>8.2f} {err:>14.1e}")
            first = False
    print("  (a uniformly random assignment costs 0.5 per row on average)")


def estimators():
    print("\n2. One-sample gradients of E[f(k)], k ~ softmax(logits), 10 categories, 2 000 draws each\n")
    rng = np.random.default_rng(0)
    logits = rng.standard_normal(10)
    values = rng.standard_normal(10) * 2
    exact = lab.expectation_gradient(logits, values)
    p = np.exp(logits) / np.exp(logits).sum()
    samples = rng.choice(10, size=2000, p=p)
    rows = [("REINFORCE", np.array([lab.reinforce_gradient(logits, values, [k]) for k in samples]))]
    v = jnp.asarray(values)
    keys = jax.random.split(jax.random.PRNGKey(0), 2000)
    for tau in (0.1, 0.5, 1.0):
        st = jax.vmap(lambda key: jax.grad(lambda l: jnp.dot(v, lab.straight_through(l, tau, key)))(jnp.asarray(logits)))(keys)
        rows.append((f"straight-through, tau {tau}", np.asarray(st)))
    print(f"  {'estimator':>26} {'bias (norm)':>12} {'spread (norm of std)':>21}")
    for name, est in rows:
        print(f"  {name:>26} {np.linalg.norm(est.mean(axis=0) - exact):>12.3f} {np.linalg.norm(est.std(axis=0)):>21.3f}")
    noise = np.linalg.norm(rows[0][1].std(axis=0)) / math.sqrt(2000)
    print(f"  (norm of the exact gradient: {np.linalg.norm(exact):.3f}. Straight-through's gradient is the Gumbel-softmax"
          f" gradient by construction. REINFORCE's bias is sampling noise, about {noise:.3f}.)")


def argmin_layer():
    print("\n3. d argmin / dq for min 1/2 x^T Q x + q^T x, 0 <= x <= 1 (n = 30)\n")
    rng = np.random.default_rng(1)
    n = 30
    B = rng.standard_normal((n, n))
    Q = B @ B.T / n + np.eye(n)
    q = rng.standard_normal(n) * 2
    A = np.vstack([np.eye(n), -np.eye(n)])
    b = np.concatenate([np.ones(n), np.zeros(n)])

    def solve(qv):
        x = cp.Variable(n)
        con = [A @ x <= b]
        cp.Problem(cp.Minimize(0.5 * cp.quad_form(x, cp.psd_wrap(Q)) + qv @ x), con).solve(
            solver="CLARABEL", tol_gap_abs=1e-12, tol_gap_rel=1e-12, tol_feas=1e-12)
        return x.value, con[0].dual_value

    (x, lam), t_solve = timed(solve, q)
    J, t_imp = timed(lab.qp_argmin_jacobian, Q, A, b, x, lam, 1e-6)
    t = time.perf_counter()
    fd = np.zeros((n, n))
    for k in range(n):
        e = np.zeros(n)
        e[k] = 1e-5
        fd[:, k] = (solve(q + e)[0] - solve(q - e)[0]) / 2e-5
    t_fd = time.perf_counter() - t
    L = float(np.linalg.eigvalsh(Q).max())

    Qj = jnp.asarray(Q)

    def unrolled(qv):
        step = lambda z, _: (jnp.clip(z - (Qj @ z + qv) / L, 0.0, 1.0), None)
        return jax.lax.scan(step, jnp.zeros(n), None, length=500)[0]

    jac = jax.jit(jax.jacrev(unrolled))
    jac(jnp.asarray(q))
    Ju, t_un = timed(lambda: np.asarray(jac(jnp.asarray(q))))
    active = len(lab.active_constraints(A, b, x, lam, 1e-6))
    print(f"  active bounds at the solution: {active} of {n} variables")
    print(f"  {'method':>40} {'max |J - finite diff|':>22} {'seconds':>8}")
    print(f"  {'implicit function theorem on KKT (yours)':>40} {np.abs(J - fd).max():>22.1e} {t_imp:>8.4f}  (+ {t_solve:.3f} s solve)")
    print(f"  {'JAX through 500 projected-gradient steps':>40} {np.abs(Ju - fd).max():>22.1e} {t_un:>8.4f}")
    print(f"  {'finite differences (60 extra solves)':>40} {'-':>22} {t_fd:>8.3f}")


def branching():
    print("\n4. A learned branching rule, trained on 10 knapsacks (16 items, 3 constraints), tested on 20 held-out (18 items)\n")
    bb = unit("07")
    u28 = unit("28")
    train = [s for seed in range(100, 110) for s in lab.collect_strong_branching(multi_knapsack(16, 3, seed), 2000)]
    w, t_train = timed(lab.train_ranker, train, 300, 0.5)
    held = [s for seed in range(200, 205) for s in lab.collect_strong_branching(multi_knapsack(18, 3, seed), 2000)]
    print(f"  {len(train)} training decisions; weights {np.round(w, 2).tolist()} ({t_train:.1f} s)")
    print(f"  imitation accuracy: training {lab.imitation_accuracy(w, train):.2f}, held-out decisions {lab.imitation_accuracy(w, held):.2f}"
          f" (most-fractional's own agreement with strong branching: {lab.imitation_accuracy(np.array([1.0, 0, 0, 0, 0]), held):.2f})")
    rules = {"most-fractional": bb.most_fractional, "pseudocost": bb.pseudocost, "strong": bb.strong_branching,
             "learned": lab.learned_rule(w)}
    nodes = {name: [] for name in rules}
    secs = {name: [] for name in rules}
    for seed in range(300, 320):
        milp = multi_knapsack(18, 3, seed)
        values = set()
        for name, rule in rules.items():
            r, t = timed(bb.branch_and_bound, milp, rule, "best", 50_000)
            nodes[name].append(r.nodes)
            secs[name].append(t)
            values.add(round(r.value, 6))
        assert len(values) == 1, "every rule must reach the same optimum"
    print(f"\n  {'rule':>16} {'SGM nodes':>10} {'median':>7} {'SGM s':>7} {'fewest nodes on':>16}")
    for name in rules:
        wins = sum(1 for k in range(20) if nodes[name][k] == min(nodes[n][k] for n in rules))
        print(f"  {name:>16} {u28.shifted_geometric_mean(nodes[name], 10):>10.0f} {int(np.median(nodes[name])):>7}"
              f" {u28.shifted_geometric_mean(secs[name], 0.1):>7.2f} {wins:>16}")
    pairs = [("learned", "most-fractional"), ("learned", "pseudocost"), ("learned", "strong")]
    tests = [u28.wilcoxon_signed_rank(nodes[a], nodes[b]) for a, b in pairs]
    adjusted = u28.holm([p for _, p in tests])
    print("\n  paired on nodes: geometric-mean ratio [95% bootstrap interval], Wilcoxon p (Holm-adjusted)")
    import random
    for (a, b), (_, p), padj in zip(pairs, tests, adjusted):
        ratio, (lo, hi) = u28.geometric_ratio_ci(nodes[a], nodes[b], random.Random(0))
        print(f"    {a} / {b:<16} {ratio:5.2f} [{lo:.2f}, {hi:.2f}]   p = {p:.4f} ({padj:.4f})")


if __name__ == "__main__":
    assignment()
    estimators()
    argmin_layer()
    branching()
