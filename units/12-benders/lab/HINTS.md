# Hints — lab 12

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — The recourse LP

<details><summary>Rung 1 — the matrix</summary>

Columns: x_ij row-major (`i * C + j`), then z_j when the penalty is set. Rows: C demand rows
(`A[j, i*C + j] = 1` and `A[j, F*C + j] = 1`), then F capacity rows (`A[C + i, i*C : i*C + C] = 1`).
Pass `row_lower = demand + [-inf]*F` and `b = [inf]*C + [u_i y_i]`.
</details>

<details><summary>Rung 2 — the duals</summary>

`info.row_duals[:C]` are ≥ 0, so they're v. `info.row_duals[C:]` are ≤ 0, so alpha is their
negation. Clip tiny wrong-signed values like −1e-17 with `max(0.0, ...)`.
</details>

<details><summary>Functional route</summary>

Nothing to thread: build the recourse LP's rows and bounds as comprehensions, make one `highs_lp` call, and
split the row duals by sign into (v, α) with two comprehensions. An infeasible LP returns `(inf, None,
None)`. A HiGHS call is a pure function of its data, so it's fine in functional code.
</details>

## Step 2 — Cuts

<details><summary>Rung 1 — optimality</summary>

`const = Σ_j d_sj v_j` and `coef_i = −u_i α_i`. The dual objective is linear in y, and (v, α)
stays dual feasible for every y, so the cut bounds Q_s everywhere by weak duality.
</details>

<details><summary>Rung 2 — feasibility</summary>

The phase-one LP has objective 0 on x and 1 on z, and it's always feasible. Its dual has
v_j ≤ 1. If the value is positive, the same formula gives const + coef·y = value > 0 at this
y. At a feasible y the phase-one value is 0, and weak duality makes the cut ≤ 0 there.
</details>

<details><summary>Functional route</summary>

Both cuts are expressions. The optimality cut is `(Σ d·v, [−u_i α_i])`. The feasibility cut solves the
phase-one LP (the same rows, cost 1 on the shortage variables), and reuses `optimality_cut` on its duals when
the shortage is positive.
</details>

## Step 3 — The loop

<details><summary>Rung 1 — the master's rows</summary>

A cut θ_s ≥ const + coef·y becomes `coef·y − θ_s ≤ −const`: a row with coef in the y columns
and −1 in θ_s's column. A feasibility cut is `coef·y ≤ −const`, with zeros for θ. Variables
are y (binary, 0..1) then θ (continuous, ≥ 0, no upper bound).
</details>

<details><summary>Rung 2 — one iteration</summary>

```
lower, y, theta = solve_master(...)
for s: q, v, a = second_stage(...)
       if q is INF: feasibility cut, mark infeasible
       else: keep q and the cut
if all feasible:
    ub = f.y + Σ p_s q_s ; best = min(best, ub)
    add cuts where theta is too small
history.append((lower, best)); stop if best < inf and best − lower is small
```
</details>

<details><summary>Rung 3 — the single cut</summary>

θ ≥ Σ_s p_s (const_s + coef_s·y): weight both const and coef by the probabilities. The test
with unequal probabilities catches a plain average.
</details>

<details><summary>Functional route</summary>

`solve_master` builds an immutable `MILP` from the two cut lists with comprehensions. `benders` is an unfold
over a state dict (optimality and feasibility cuts, core point, relax flag, incumbent, history, done). A step
solves the master, maps `second_stage` over the scenarios, derives cuts as one list, and returns a new dict
with `dict(st, ...)`. Stop with a generator that yields states up to the first `done`, capped by
`tz.take(max_iter, ...)`, and keep the last with `tz.last`.
</details>

## Step 4 — Pareto cuts

<details><summary>Rung 1</summary>

The variables are (v_0..v_{C−1}, α_0..α_{F−1}). Add F·C rows `v_j − α_i ≤ c_ij` and one row
"value at y ≥ q − ε". Bounds: 0 ≤ v ≤ penalty and α ≥ 0. Objective: maximise
Σ d_j v_j − Σ u_i core_i α_i with `highs_lp(..., sense="max", lower=0, upper=..., row_lower=...)`.
</details>

<details><summary>Rung 2 — the degenerate example</summary>

One customer with demand 10, two facilities of capacity 10 and costs 1 and 2, only the first
open. The first runs at capacity, so v isn't pinned down: any v ∈ [1, 50] with α_0 = v − 1 is
optimal. At the core (0.5, 0.5) the cut is worth 10v − 5(v − 1) − 5α_1, maximised at 15
once v ≥ 2 and α_1 = max(0, v − 2).
</details>

<details><summary>Functional route</summary>

One LP, built in one pass: a row per (facility, customer) pair, one row pinning the recourse value to its
optimum, and an objective evaluated at the core point. The core point itself lives in the step-3 state and is
updated as the midpoint of the old core and the new y, a pure average.
</details>

## Step 5 — LP first

<details><summary>Rung 1</summary>

Keep a `relax` flag, starting at `lp_first`. While relaxed, pass `relax=True` to the master,
add cuts as usual, and don't touch `best` or `history`. When the relaxed iteration's
ub − lower is within tolerance, set `relax = False`. Every cut stays: cuts from fractional y
are valid for integer y.
</details>

<details><summary>Functional route</summary>

No new loop: `relax` is a field of the step-3 state. While it's true the master is solved as an LP, and the
flag flips to false once that LP's bounds close. Every cut found so far stays in the state and carries over to
the integer phase.
</details>
