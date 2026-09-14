# Hints — lab 08

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — A Gomory cut

<details><summary>Rung 1 — why the cut is valid</summary>

Row *i* of the tableau reads Σⱼ tᵢⱼ zⱼ = tᵢ₀ over *z* = (x, s). Every *z* is a
nonnegative integer at an integer solution: *x* by assumption, and *s = b − Ax*
because *A*, *b* are integers. Replace each tᵢⱼ by ⌊tᵢⱼ⌋: the left side can only
shrink, so Σ⌊tᵢⱼ⌋zⱼ ≤ tᵢ₀. The left side is an integer, so it is ≤ ⌊tᵢ₀⌋.
Subtract that from the original row: Σ f(tᵢⱼ) zⱼ ≥ f(tᵢ₀).
</details>

<details><summary>Rung 2 — substituting the slacks</summary>

With *f* = fractional parts of row *i* over the n + m columns:
Σⱼ fⱼ xⱼ + Σₖ f₍ₙ₊ₖ₎ (bₖ − Aₖ·x) ≥ f₀. Collect terms and flip the sign to get *a·x ≤ β*:
aⱼ = Σₖ f₍ₙ₊ₖ₎ Aₖⱼ − fⱼ and β = Σₖ f₍ₙ₊ₖ₎ bₖ − f₀. Then multiply by
`math.lcm` of all the denominators and convert to `int`.
</details>

<details><summary>Rung 3 — after adding cuts</summary>

In `gomory_loop`, pass the *current* A and b (including earlier cuts) to
`gomory_cut`. The tableau has one slack per current row. Earlier cuts were scaled to
integers, so their slacks are integers too, and the derivation still holds.
</details>

<details><summary>Functional route</summary>

`gomory_cut` has no state to thread: the fractional parts are a comprehension over the row, the coefficients
and right-hand side are two sums, and the scaling is `math.lcm(*denominators)`. `fractional_row` scores each
basic structural row as `(distance to the nearest integer, -row, row)` and takes `max(..., default=...)`, so
"no fractional row" falls out of the default instead of a special case.
</details>

## Step 2 — The pure Gomory loop

<details><summary>Functional route</summary>

An unfold. The state is `(A, b, bounds, cuts, result, done)`, and `step` either marks it done (no
fractional row) or appends one cut and re-solves. `tz.iterate(step, start)` produces the states; take the
first with `done` or at index `rounds`, with `next(s for k, s in enumerate(states) if ...)`.
</details>

## Step 3 — Cover separation

<details><summary>Rung 1</summary>

`need = capacity + 1`. `dp[t]` = cheapest cost of a set whose weight reaches at
least *t*, with weights capped at `need`. Start `dp[0] = 0`. For each item, update
from high *t* to low (0/1 knapsack): `u = min(need, t + w_j)`,
`dp[u] = min(dp[u], dp[t] + 1 - x_j)`. Track the chosen set next to each entry.
</details>

<details><summary>Rung 2 — functional pitfall</summary>

If you build the next table with a dict comprehension keyed by `min(need, t + w)`,
several `t` map to the same key and the comprehension keeps only the last. Group
by key and take the cheapest (`toolz.groupby`), then merge with the old table the
same way.
</details>

<details><summary>Functional route</summary>

A fold over the items: `reduce(add_item, range(len(weights)), {0: (0.0, ())})`, where the accumulator maps
each capped weight to (cost, chosen items). `add_item` builds the candidates, groups them by key with
`tz.groupby`, keeps the cheapest in each group, and merges with the old table by
`tz.merge_with(min-by-cost, ...)`. That grouping is the pitfall of Rung 2 handled explicitly.
</details>

## Step 4 — Lifting

<details><summary>Rung 1</summary>

`lifted = list(cover)`. For each *j* outside the cover in order:
`room = capacity - w[j]`; if `room < 0`, set `alpha[j] = rhs`, since *xⱼ* can never
be 1. Otherwise `best` is the max over subsets S of `lifted` with weight ≤ room of
Σ alpha, and `alpha[j] = rhs - best`. Then append *j* to `lifted`.
</details>

<details><summary>Rung 2 — why it's maximal</summary>

With *xⱼ* = 1, the other lifted variables can contribute at most `best` within the
remaining capacity, so αⱼ + best ≤ rhs is exactly the most you can give αⱼ. The
subset achieving `best`, plus *j*, is the point that makes αⱼ + 1 invalid.
</details>

<details><summary>Functional route</summary>

A fold over the variables outside the cover. The accumulator is `(alpha as a tuple, lifted so far)`, and
each step returns a new alpha with one coefficient replaced. `best` is a `max(..., default=None)` over the
subsets from `chain.from_iterable(combinations(lifted, k) for k ...)` that fit in the room.
</details>

## Step 5 — The root loop

<details><summary>Rung 1</summary>

Keep the pool as a list of `(alpha, rhs, age)`. Each round:
`lp_relaxation(replace(milp, A_ub=milp.A_ub + cuts, b_ub=milp.b_ub + rhss))`.
Record the value and `len(pool)` first, then `age_pool`, then separate.
Deduplicate with a set of `(tuple(alpha), rhs)`, including cuts found in this round.
</details>

<details><summary>Functional route</summary>

`age_pool` is one generator that re-ages every cut, then a filter. `root_cut_loop` is an unfold over
`(pool, bounds, sizes, added, done)`: solve with the pool appended (via `dataclasses.replace`), age, separate
with a comprehension over the rows, and deduplicate against the aged pool with `tz.unique`. Stop at the first
state with no new cuts, or after `rounds + 1` states.
</details>
