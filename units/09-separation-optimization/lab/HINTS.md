# Hints — lab 09

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — Rows and components

<details><summary>Rung 1</summary>

Row: `tuple(-1 if (i in S) != (j in S) else 0 for i, j in edges(n))`, with rhs `-2`.
Components: build adjacency from edges with `x_e > eps`, then BFS from each unseen
vertex.
</details>

<details><summary>Functional route</summary>

`subtour_row` is one comprehension over `edges(n)`. `components` is a fixpoint of label propagation: a pass
is a fold over the support edges that gives both endpoints the smaller label, `tz.iterate` repeats passes, and
`tz.sliding_window(2, ...)` finds the first pass that changes nothing. Then `tz.groupby` by label gives the
components.
</details>

## Step 2 — Minimum cut

<details><summary>Rung 1 — one phase</summary>

Keep a weight matrix `w` over "super-vertices" (groups of merged original vertices).
In a phase, start from any active vertex. Keep `attached[v]` = total weight from
`v` to the vertices already ordered, and repeatedly add the unordered vertex with
the largest `attached`. Let the last two be *s*, *t*. The "cut of the phase" is
`attached[t]` at the moment *t* was added, which is the weight between *t*'s group
and everything else.
</details>

<details><summary>Rung 2 — merging</summary>

Merge *t* into *s*: `groups[s] += groups[t]`, and `w[s][v] += w[t][v]` for every
active *v* (keep it symmetric), then remove *t*. Repeat phases until one active
vertex remains. Track the smallest cut of any phase and the group of *t* in that
phase. That group is *S*.
</details>

<details><summary>Rung 3 — why it works</summary>

Stoer–Wagner's lemma: the cut of the phase is a minimum *s–t* cut. So either the
global minimum cut separates *s* and *t*, and that phase found it, or it doesn't,
and merging them loses nothing.
</details>

<details><summary>Functional route</summary>

Stoer–Wagner is an unfold over `(groups, weights, best cut)`, one phase per step, until one group is left.
A phase is a fold that builds the maximum-adjacency order: its accumulator is `(order so far, attachment of
each vertex)`, and each step returns a new attachment dict. Merging the last two vertices renames `t` to `s`
in every edge key and sums parallel edges with `tz.merge_with(sum, ...)`. Weights keyed by `frozenset`s make
the renaming symmetric.
</details>

## Step 3 — The separation oracle

<details><summary>Functional route</summary>

No state: components first, and `min_cut` only when the support is connected. Two expressions and a
conditional.
</details>

## Step 4 — The subtour LP

<details><summary>Rung 1</summary>

`milp = degree_milp(tsp, integer=False)`; keep lists `rows`, `rhs`. In a loop:
`lp = lp_relaxation(replace(milp, A_ub=tuple(rows), b_ub=tuple(rhs)))`;
`found = separate_subtours(n, lp.x)`; if empty, return. Otherwise append a row per
set.
</details>

<details><summary>Functional route</summary>

Steps 4 and 5 share one unfold, `lazy(milp, solve, separate, n)`. Its state is `(cut rows, solve count,
last solution, done)`: solve with the rows so far, separate, and append a row per set found. The subtour LP
passes `lp_relaxation` and `separate_subtours`; the loop is the same object in both steps.
</details>

## Step 5 — The exact TSP

<details><summary>Rung 1</summary>

The same loop with `highs_mip(..., options={"mip_rel_gap": 0.0})` and
`components(n, sol.x, eps=0.5)`. When there is one component, the tour is
`tour_from_edges(n, sol.x)` and the length is `round(sol.value)`.
</details>

<details><summary>Rung 2 — why components are enough here</summary>

An integer solution of the degree equations gives every vertex exactly two chosen
edges, which makes it a disjoint union of cycles. If there is more than one cycle,
each cycle's vertex set has zero crossing weight, so its subtour row is violated.
</details>

<details><summary>Functional route</summary>

The same `lazy` unfold with an integer `solve` (`highs_mip` with a zero gap) and a separator that only
looks at components with `eps=0.5`. On an integer x, a disconnected support is the only way to violate a
subtour constraint.
</details>
