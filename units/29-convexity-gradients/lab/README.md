# Lab 29 — Convexity, gradients, and what continuity changes

**Time:** about 2 hours. **Before:** the slides (`uv run co slides 29`).
**You write:** 13 functions in `lab.py`, 110–150 lines in all.
**Needs:** unit 02 (the simplex method, as an oracle), unit 03 (duality and complementary slackness).

The coda starts here. Everything so far lived on vertices and integers. Continuous optimisation
lives in the interior, and it has its own algorithms: gradients, momentum, projections. It also has one
bridge back to what you know. The KKT conditions are LP duality generalised: complementary slackness
*is* the KKT complementarity condition. Frank–Wolfe goes further and puts your unit-02 simplex method
inside a continuous loop as its linear oracle. This lab builds the first-order methods, checks their
textbook rates on quadratics, projects onto the simplex, runs Frank–Wolfe over a polytope, and computes
KKT residuals for LPs and QPs.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| Unit 02's `simplex` (through `colib.ref`) | Quadratic and Rosenbrock with gradients; a central-difference gradient check |
| cvxpy, HiGHS (tests); scipy.optimize (`then`) | Gradient descent, heavy ball, Nesterov |
| | Projection onto the simplex; projected gradient |
| | A simplex-method linear oracle; Frank–Wolfe with its gap |
| | KKT residuals for LPs and QPs |

## Running it

```fish
uv run co test 29
uv run co test 29 --solution functional
```

## Style

Every iterative method returns its whole trajectory, so the functional reference writes each one as an
unfold (`tz.iterate` over a state tuple, then `take`). The imperative one appends to a list. The
projection and the KKT residuals are single numpy expressions either way.

---

## Step 1 — Functions and a gradient check  *(15 min)*

*Shape: closures; a loop over coordinates.*

**Done when** `step 1 ✓`: quadratic and Rosenbrock values and gradients at known points (including
(−1.2, 1)), gradient checks small for right gradients and large for wrong ones, and a central difference
on x³ at h = 1e−3 (a forward difference would fail).

## Step 2 — First-order methods  *(30 min)*

*Shape: three update rules.*

**Done when** `step 2 ✓`. Hand traces on f = x²/2 match all three methods exactly. On 12 random convex
quadratics, some rank-deficient, every iterate satisfies GD's L‖x0 − x*‖²/2k and Nesterov's
2L‖x0 − x*‖²/(k+1)². Nesterov is ahead of GD by iteration 30 at condition number 100. Heavy ball with the
optimal parameters reaches 1e−8 relative error in 150 iterations, where GD is still above 1e−2.

## Step 3 — Projection onto the simplex  *(25 min)*

*Shape: a sort, a prefix sum, a threshold.*

**Done when** `step 3 ✓`. Hand cases (interior, boundary, all negative) pass. On 20 random vectors the result
is in the simplex, satisfies the variational inequality against every vertex, and is idempotent.
Projected gradient matches CVXPY's optimum on 4 simplex-constrained quadratics.

## Step 4 — Frank–Wolfe  *(25 min)*

*Shape: an LP per iteration; a convex combination.*

**Done when** `step 4 ✓`. Your simplex-method oracle matches HiGHS on 10 directions. Over 300 iterations
on 4 quadratics every iterate is feasible, every gap bounds the suboptimality, and the error stays under
2LD²/(k+2). A hand-built oracle checks the step sizes and gaps exactly.

## Step 5 — KKT  *(20 min)*

*Shape: four residuals; four more.*

**Done when** `step 5 ✓`. HiGHS's primal-dual pairs on 8 random LPs have all residuals below 1e−7.
Halving x breaks complementarity, halving y breaks dual feasibility, and hand cases isolate each of
x ≥ 0, y ≥ 0 and each complementarity condition. CVXPY's QP solutions and duals have residuals below
1e−6, and hand cases do the same for the QP.

**The checkpoint** is in this step: derive the KKT conditions for the LP on paper, and show that
`lp_kkt_residuals` checks exactly unit 03's complementary slackness. Write it in `NOTES.md`.

---

## Then — against scipy and CVXPY  *(10 min, runs about 1 minute)*

```fish
uv run co then 29
```

**Quadratics, n = 100**: iterations until relative suboptimality ≤ 1e−8 (plot: `out/convergence.png`).

| κ | GD | heavy ball | Nesterov | scipy CG | L-BFGS-B | predicted GD / HB / Nesterov bound |
|---:|---:|---:|---:|---:|---:|---|
| 100 | 760 | **52** | 435 | 103 | 94 | 917 / 46 / 140 043 |
| 10 000 | > 20 000 | **542** | 12 048 | 1 329 | 749 | 92 099 / 461 / 1 328 943 |

- **Heavy ball with the right parameters** matches its predicted linear rate. It needs μ and L, which
  you rarely know.
- **Nesterov's convex schedule** is far better than its worst-case bound, and ahead of GD to 1e−8
  (435 against 760 at κ = 100). But its curve flattens while GD's stays linear, and at κ = 100 GD catches
  up around iteration 1 300, near machine precision (see the plot). The (k−1)/(k+2) momentum is designed
  for merely convex functions and doesn't exploit strong convexity. The strongly convex variant uses a
  constant momentum, like heavy ball.
- **CG and L-BFGS** use curvature information built from gradients and beat all three except
  tuned heavy ball. On quadratics CG is optimal among Krylov methods.

**Rosenbrock** from (−1.2, 1), iterations to within 1e−6 of (1, 1): GD with step 1e−3, **34 374**;
Nesterov, **5 019**; scipy BFGS, **34**.

**Least squares on the simplex**, n = 200 (CVXPY/CLARABEL: 0.25 s):

| method | 100 iterations | 1 000 | 5 000 |
|---|---:|---:|---:|
| projected gradient, f − f* | 6.9e−4 | **8.8e−11** | at CVXPY's precision |
| Frank–Wolfe, f − f* | 1.0e−1 | 3.5e−3 | 1.9e−4 |

Frank–Wolfe is much slower here: its O(1/k) rate is real, while projected gradient's error falls linearly
on this instance (from 7e−4 to 9e−11 in 900 iterations). After 1 000 iterations Frank–Wolfe had 116 nonzeros against projected gradient's 107
and CVXPY's 107. So "Frank–Wolfe iterates are sparse" didn't show up on this instance. Its real
advantage is elsewhere: a linear oracle can be cheap where a projection isn't (matroid polytopes,
flows, permutations).

**Frank–Wolfe over a polytope** (n = 30, m = 20), 200 iterations: the same iterates with your unit-02
simplex as the oracle (2.1 ms per call) and with HiGHS (1.2 ms per call), f − f* = 5.8e−4.

**KKT at an LP optimum** (m = 30, n = 50): HiGHS's pair has residuals 3.6e−13, 0, 3.3e−13 and 1.8e−13,
and a duality gap of −1.3e−13. **Unit 03's exact certificate rejects the same pair** rounded to 9
decimals ("primal constraint 12 violated"): an exact check on floating-point data fails at the 1e−9 level.
Tolerances are part of the definition of "optimal" in floating point.

## Checkpoint

- [ ] `uv run co test 29` shows all five steps ✓.
- [ ] **You can derive the KKT conditions for a linear program and show they reduce exactly to
      complementary slackness from unit 03** (`NOTES.md`).
- [ ] You can say which of GD, heavy ball, Nesterov, CG and L-BFGS you'd use on a smooth problem of
      unknown conditioning, and why tuned heavy ball's 52 iterations isn't a fair comparison.

## Reading

- Boyd & Vandenberghe, *Convex Optimization* (2004), ch. 5 (duality, KKT) and ch. 9. Free online.
- Nesterov, *Lectures on Convex Optimization* (2018), ch. 2.
- Bubeck, "Convex optimization: algorithms and complexity", *Foundations and Trends in ML* 8 (2015).
- Jaggi, "Revisiting Frank–Wolfe: projection-free sparse convex optimization", *ICML* 2013.
- Duchi, Shalev-Shwartz, Singer & Chandra, "Efficient projections onto the ℓ1-ball for learning in high
  dimensions", *ICML* 2008.
