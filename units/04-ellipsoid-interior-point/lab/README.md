# Lab 04 — Polynomial-time LP: interior point and ellipsoid

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 04`).
**You write:** 6 functions in `lab.py`, 60–90 lines in all.
**Needs:** unit 02. This is a branch unit, so skip it on the express route.
Unit 09 uses the ellipsoid idea.

Simplex walks the boundary. This lab builds the two methods that go through the
middle instead:

- **the barrier method**, the ancestor of every production interior-point solver;
- **the ellipsoid method**, which proved LP is in P and is never used to solve one.

`then` compares both ideas with HiGHS, where interior point wins cold solves and
loses warm ones.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| numpy; `colib.polyhedra.shifted_polytope`, `inscribed_radius` | The log-barrier function, gradient and Hessian |
| `colib.solvers.highs_lp` (tests only) | Damped Newton centering with backtracking |
| | Path-following, with the dual point on the path |
| | The ellipsoid update, and the feasibility search |
| | The iteration bound from the volume argument |

## Running it

```fish
uv run co test 04
uv run co test 04 --solution functional
```

## Style

Any style passes. numpy expressions are already pure. The three iterative methods
(Newton, path-following, ellipsoid) are natural `iterate(step, state)` unfolds in
the functional reference. Don't use recursion; the ellipsoid method can take
hundreds of steps.

---

## Step 1 — The barrier  *(20 min)*

*Shape: vector expressions.* With slack *s = b − Ax*, you need
*f = −t c·x − Σ log sᵢ*, *∇f = −t c + Aᵀ(1/s)*, and
*∇²f = Aᵀ diag(1/s²) A*.

**Done when** `step 1 ✓`: the gradient and Hessian match finite differences, the
Hessian is symmetric positive definite, and points on or outside the boundary
return infinity.

## Step 2 — Newton centering  *(30 min)*

*Shape: an unfold with an inner search.* A Newton direction, then backtrack until
there is sufficient decrease.

**Done when** `step 2 ✓`: from the origin, for *t* ∈ {0.1, 1, 50} on 8 polytopes,
the result is strictly feasible, has a small gradient, takes fewer than 60 steps,
and is at least as good as a derivative-free minimizer's answer.

*Think about:* why doesn't the line search need an explicit feasibility check?

## Step 3 — The central path  *(30 min)*

*Shape: an unfold over t.* Centre, record, multiply *t* by μ.

**Done when** `step 3 ✓`: the final objective matches HiGHS to 10⁻⁴, *t* grows
by exactly μ, the objective improves along the path, and at every point up to
*t* = 10⁵ the point is centred, *y > 0*, *Aᵀy ≈ c*, and the duality gap equals
*m/t*.

*Think about:* why is *y = 1/(t s)* dual feasible at a centre? Set the gradient
to zero and read it off.

## Step 4 — The ellipsoid method  *(35 min)*

*Shape: a formula, then an unfold.* The update formula is in the docstring, and
the slides derive it for the unit ball.

**Done when** `step 4 ✓`: the new ellipsoid contains the kept half, since 400
random points of the half are checked; the volume shrinks by more than
exp(−1/(2(n+1))); a feasible point is found in 10 polytopes that don't contain the
origin; and an empty system is given up on.

## Step 5 — The bound  *(10 min)*

*Shape: one line.* Volume shrinks by a factor exp(−1/(2(n+1))) per step. Start at
vol(ball *R*), and stop once the volume drops below vol(ball *r*).

**Done when** `step 5 ✓`: the formula is exact, and your method never exceeds your
bound on 10 polytopes.

---

## Then — against HiGHS  *(10 min, runs ~4 s; `--big` adds ~4 min)*

```fish
uv run co then 04
```

1. **The central path**, plotted on unit 01's polygon. The path starts near the
   analytic centre, which is (0.77, 2.13) at *t* = 0.01, and bends into the
   optimal vertex (2.5, 1.5).
2. **Floating point.** The gap equals *m/t* exactly up to *t* = 10⁶. At *t* = 10⁷
   Newton hits its 100-step cap and the gap is 1.3 × 10⁻³ instead of 1.4 × 10⁻⁶.
   The pure barrier method ends there, and production codes solve the primal–dual
   system instead.
3. **Cold solves** on random sparse LPs, presolve off. At *n* = 300 the two tie
   (6 ms). At *n* = 3000, IPM takes **0.14 s / 18 iterations** and simplex
   **0.95 s / 5268 iterations**. With `--big`, at *n* = 20 000: IPM 12 s (25 iterations),
   simplex 199 s (66 941 iterations).
4. **Warm solves.** Add one constraint at *n* = 3000. Simplex re-solves in **0.033 s**
   (22 iterations), while IPM re-solves in 0.136 s, which is slower than its own
   cold solve, because it starts over.
5. **Ellipsoid.** Mean iterations against the volume bound grow from 7.8 vs 61
   (*n* = 2) to 74 vs 882 (*n* = 8). The bound is loose but polynomial.

## Checkpoint

- [ ] `uv run co test 04` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** you can choose between simplex and barrier
      for a given LP and defend the choice (size, sparsity, whether a warm start is
      available), and explain why branch-and-bound still wants simplex at every node.
- [ ] You can say in one sentence why the ellipsoid method matters (unit 09) even
      though nobody solves LPs with it.

In `NOTES.md`: the crossover *n* from part 3 on your machine, and the part 4 timings.

## Reading

- Bertsimas & Tsitsiklis, ch. 8 (ellipsoid, §8.1–8.3) and ch. 9 (interior point,
  §9.1–9.5).
- Boyd & Vandenberghe, *Convex Optimization*, §11.1–11.3 (the barrier method
  exactly as built here). Free PDF from the authors.
- Optional: Wright, *Primal-Dual Interior-Point Methods*, ch. 1, for what HiGHS's
  IPM actually does.
