# Hints — lab 07

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — Most fractional, and children

<details><summary>Rung 1</summary>

Loop over `enumerate(zip(milp.integer, lp.x))`; keep the best fractionality seen,
replacing only on **strictly** greater, so the lowest index wins ties. Start the
"best so far" at `INT_TOL` so near-integers never qualify.
</details>

<details><summary>Rung 2 — children</summary>

Copy `ub` to a list, set index `j` to `math.floor(value)`, tuple it; same for `lb`
with `math.ceil`. The down child keeps the original `lb`, the up child the
original `ub`.
</details>

<details><summary>Functional route</summary>

A rule is a `max` over `(fractionality, −j, j)` for the fractional integer variables, which encodes "most
fractional, ties to the lowest index" in the tuple order. `children` returns two new `(lb, ub)` pairs, each
with one bound replaced by a comprehension. Nothing is copied and then mutated.
</details>

## Step 2 — The tree

<details><summary>Rung 1 — the frontier</summary>

Best-first: `heapq` with entries `(lp.value, counter, node)`. The counter breaks
ties so Python never compares two NodeLPs. DFS: a list with `append`/`pop`.
Push the root, then `while frontier:`.
</details>

<details><summary>Rung 2 — what to do with a popped node</summary>

In this order: prune if `lp.value >= incumbent - 1e-9`; if `is_integral(milp,
lp.x)`, set the incumbent and continue; otherwise branch. Pruning again at pop
time matters: the incumbent may have improved since the node was pushed.
</details>

<details><summary>Rung 3 — the children</summary>

For each of `("down", "up")` zipped with `children(...)`: check the node limit,
`solve_node`, increment `nodes` and `stats["lp_solves"]`. If feasible, record the
per-unit gain in `stats["pseudo"].setdefault((j, dir), [])`, then push if
`child.value < incumbent - 1e-9`.
</details>

<details><summary>Functional route</summary>

A frozen `Search(frontier, incumbent, best_x, nodes, stats, serial, stopped)`.
`step` pops (first element for best, last for DFS), prunes or accepts, or folds
`one_child` over the two children. `bisect` on `(bound, serial)` keys keeps the
tuple sorted. The run is `first(dropwhile(lambda s: s.stopped is None, iterate(step, start)))`.
</details>

## Step 3 — The product score

<details><summary>Functional route</summary>

One expression. The ε floor is what stops a zero gain on one side from wiping out the other.
</details>

## Step 4 — Pseudocosts

<details><summary>Rung 1</summary>

`seen = [sum(g)/len(g) for g in stats["pseudo"].values() if g]`,
`default = mean(seen) if seen else 1.0`. For each fractional integer j:
`f = x_j - floor(x_j)`, `down = f * avg(j, "down")`, `up = (1 - f) * avg(j, "up")`,
score with `product_score`. Keep strictly better scores (lowest index wins ties).
</details>

<details><summary>Functional route</summary>

The rule reads unit 07's pseudocost history from `stats` without changing it. The default is the mean of all
observed gains, and a per-(variable, direction) average falls back to it through a lambda. The score list is one
comprehension using `for f in [v − floor(v)]` to name the fractional part inline. The tree (step 2) records gains
with `tz.assoc`, so the history is a persistent map that grows by rebinding.
</details>

## Step 5 — Strong branching

<details><summary>Rung 1</summary>

`sorted(((fractionality, j) ...), reverse=True)` puts the most fractional first,
but on ties it puts the *higher* index first. The tests don't depend on the tie
order among candidates. For each candidate, `solve_node` both children, add 2 to
`stats["lp_solves"]`, and take gains `child.value - lp.value` (or `1e9` if
infeasible).
</details>

<details><summary>Rung 2 — why 1e9 for infeasible</summary>

An infeasible child is the best possible outcome of a branch: that side needs no
further search. A huge gain makes the product score favour it, provided the other
side also improves.
</details>

<details><summary>Functional route</summary>

Probe both children of each candidate in a dict comprehension, then take the `max` over product scores. The
one mutation is the shared LP-solve counter in `stats`, which the tree reads back. It's marked in the reference
as a deliberate exception rather than hidden.
</details>
