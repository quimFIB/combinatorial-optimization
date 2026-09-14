# Hints — lab 05

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — Aggregated big-M

<details><summary>Rung 1 — indices</summary>

`n = F + F*C`. Column of *yᵢ* is `i`; column of *xᵢⱼ* is `F + i*C + j`. Objective:
`list(inst.open_cost) + [inst.serve_cost[i][j] for i in range(F) for j in range(C)]`
(the comprehension order matches the column order).
</details>

<details><summary>Rung 2 — the rows</summary>

Assignment row for customer *j*: 1 in column `F + i*C + j` for every *i*, rhs 1 → `A_eq`.
Linking row for facility *i*: 1 in columns `F + i*C + j` for every *j*, `-M` in column `i`, rhs 0 → `A_ub`.
`ub = (1,)*n`, `integer = (True,)*F + (False,)*(F*C)`. Everything a tuple.
</details>

<details><summary>Functional route</summary>

`unit_row(n, {index: value})` builds one row from a dict. Each family is a
generator of `(row, rhs)`; `model(inst, families)` does `chain.from_iterable` and
splits rows from rhs. Then `ufl_aggregated = model(inst, [aggregated_rows(inst, M)])`.
</details>

## Step 2 — Disaggregated

<details><summary>Rung 1</summary>

Same as step 1 but loop over (i, j): row has 1 at `F + i*C + j` and −1 at `i`.
Factor the shared parts (objective, assignment rows, bounds, flags) into a helper
you call from both.
</details>

<details><summary>Functional route</summary>

With step 1's `model(inst, families)` in place, this is one more family: `linking_rows(inst)` is a generator of
`(unit_row(n, {x_ij: 1, y_i: −1}), 0)` over (i, j), and `ufl_disaggregated = model(inst, [linking_rows(inst)])`.
The two formulations differ only in the families they list.
</details>

## Step 3 — Brute force

<details><summary>Rung 1</summary>

`itertools.combinations(range(F), k)` for k = 1..F gives every nonempty open set.
Cost = opening costs + for each customer `min(inst.serve_cost[i][j] for i in S)`.
Keep the minimum, and the set that achieved it.
</details>

<details><summary>Functional route</summary>

`min(((cost(S), S) for S in subsets), key=lambda p: p[0])` where `subsets` is
`chain.from_iterable(combinations(range(F), k) for k in range(1, F + 1))`.
</details>

## Step 4 — Capacitated

<details><summary>Rung 1</summary>

Capacity row for facility *i*: `demand[j]` in column `F + i*C + j`, `-capacity[i]` in
column `i`, rhs 0. Strong adds step 2's rows, then one row with `-capacity[i]` in
every column `i` and rhs `-sum(demand)` (that is Σ uᵢ yᵢ ≥ D multiplied by −1).
Keep the order the docstring gives; the test counts rows.
</details>

<details><summary>Functional route</summary>

Two more families, `capacity_rows` and a one-element `cover_row`, and a list that depends on `strong`:
`model(inst, [capacity_rows(inst)] + ([linking_rows(inst), cover_row(inst)] if strong else []))`. The row
order the test counts is the order of the families in that list.
</details>

## Step 5 — Gap closed

<details><summary>Rung 1</summary>

`1.0 if optimum - weak <= 1e-9 else (strong - weak) / (optimum - weak)`.
</details>

<details><summary>Functional route</summary>

It's already one conditional expression; there's nothing to fold.
</details>
