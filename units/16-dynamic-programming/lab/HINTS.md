# Hints — lab 16

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — Knapsack

<details><summary>Rung 1 — 0/1 with a 1-D table</summary>

`best = [0] * (C + 1)`. For each item i, loop c from C down to `w_i`:
`if best[c - w] + v > best[c]: best[c] = ...; take[i][c] = True`. Going down means
`best[c - w]` still excludes item i.
</details>

<details><summary>Rung 2 — reconstruction</summary>

Walk the items **backwards**, starting from `c = C`. If `take[i][c]`, take item i and
set `c -= w_i`. Backwards matters: `take[i][c]` was decided when only items ≤ i were
considered, and the later items have already been accounted for when you reach i.
</details>

<details><summary>Rung 3 — making capacity 100 000 fast</summary>

For item i, all capacities update at once:
`cand = best[:C+1-w] + v; better = cand > best[w:]`. Then store `better` in row i of a
boolean array and `best[w:] = np.where(better, cand, best[w:])`. The right-hand side
is computed from the old `best`, so the order question from rung 1 disappears.
</details>

<details><summary>Rung 4 — unbounded</summary>

Capacities increasing: `best[c] = max(best[c-1], max(best[c-w_i] + v_i))`, recording
which item (or "none", for the `best[c-1]` case) won. To reconstruct, from `c = C`:
if none won, `c -= 1`; else count that item and `c -= w`.
</details>

<details><summary>Functional route</summary>

`tz.accumulate(add_item, range(n), (0,) * (C + 1))` gives every row. Row i+1 is a
tuple comprehension over c from row i. To reconstruct, compare `rows[i][c]` with
`rows[i-1][c]`: they differ exactly when item i−1 was taken.
</details>

## Step 2 — Held–Karp

<details><summary>Rung 1 — the states</summary>

Represent S ⊆ {1..n−1} as a bitmask; city k is bit k−1. Base case:
`D[{k}][k] = dist[0][k]`. Then
`D[S][k] = min over j in S − {k} of D[S − {k}][j] + dist[j][k]`. Answer:
`min over k of D[full][k] + dist[k][0]`.
</details>

<details><summary>Rung 2 — order of computation</summary>

Iterating masks in increasing numeric order works, because S − {k} < S. Store the
minimising j in `parent[S][k]`. To rebuild: from (full, last), step to
(S − {k}, parent), collect cities, reverse, and prepend 0.
</details>

<details><summary>Rung 3 — tiny n</summary>

Handle n = 1 (length 0, order [0]) and n = 2 (dist[0][1] + dist[1][0]) directly.
</details>

<details><summary>Functional route</summary>

One dict per subset size, keyed by `(frozenset S, k)` and built from the previous
size's dict with `combinations(range(1, n), size)`. `tz.accumulate` keeps every
layer for the reconstruction.
</details>

## Step 3 — Trees

<details><summary>Rung 1</summary>

Get a DFS order with an explicit stack, recording `parent`. Then in reverse order
(children first): `inc[p] += min(inc[v], exc[v])` and `exc[p] += inc[v]`, starting
from `inc = weights` and `exc = 0`.
</details>

<details><summary>Rung 2 — choosing</summary>

In forward order (parents first): a root is in the cover if `inc ≤ exc`. A child
whose parent is *not* in the cover must be in it. Otherwise it is in if `inc ≤ exc`.
</details>

<details><summary>Functional route</summary>

Recursion would overflow on a path of a few thousand vertices, so root the forest by BFS layers (an unfold over
`(seen, parent, layers)` that starts a new tree when a layer comes up empty). The DP is then a fold over the
layers from the deepest up: each step adds `{v: (include v, exclude v)}` for one layer, computed from its
children's entries already in the dict. Reconstruction is a fold over the layers from the top: v goes in the
cover if its parent isn't in it, or if including v is no worse.
</details>

## Step 4 — Decompositions

<details><summary>Rung 1 — the checker</summary>

A graph on B nodes is a tree iff it has B − 1 edges and is connected. Test those
two, then the coverage of vertices and edges. Then, for each vertex, run a search
over tree nodes restricted to bags containing it, and compare the count reached with
the count containing it.
</details>

<details><summary>Rung 2 — elimination</summary>

Keep `nbrs` as sets. For each eliminated v: `bag = {v} | nbrs[v]`. For each
neighbour a: `nbrs[a] |= nbrs[v] - {a}` and `nbrs[a].discard(v)`. Record the
elimination position of each vertex.
</details>

<details><summary>Rung 3 — the tree edges</summary>

Bag i (for vertex v) attaches to the bag of the vertex in `bag − {v}` eliminated
earliest after v. That vertex's bag contains all of `bag − {v}`, because the fill-in
made them a clique. Bags where `bag − {v}` is empty are roots: chain them together.
</details>

<details><summary>Functional route</summary>

The checker is one conjunction of quantifiers: the tree has B − 1 edges and is connected; every vertex and
every edge sits in some bag; each vertex's bags are connected. Connectivity is a reachability fixpoint
(`tz.sliding_window(2, tz.iterate(grow, start))`). Elimination is an unfold over `(neighbour sets, step,
bags so far)`: remove v, make its neighbourhood a clique in a new dict, and record the bag. The tree edges link
each bag to the earliest-eliminated vertex left in it.
</details>

## Step 5 — The decomposition DP

<details><summary>Rung 1 — one bag</summary>

Index the bag's vertices `bag = sorted(bags[b])` and use bitmasks S over positions.
S is valid if every graph edge with both ends in the bag has an end in S. Start with
`t[S] = w(S)` for valid S, and INF otherwise.
</details>

<details><summary>Rung 2 — absorbing a child</summary>

Let `shared = bag_c ∩ bag_b`. For each valid child subset Sc, let
`key = Sc ∩ shared` and `val = table_c[Sc] − w(key)`, which avoids counting shared
vertices twice. Keep `best[key] = min val` and remember the argmin. Then for each
parent S: `t[S] += best[S ∩ shared]`.
</details>

<details><summary>Rung 3 — why every key exists</summary>

Whatever the parent decides on the shared vertices, the child can put all its other
vertices in the cover, and that's valid. So `best[key]` always exists. You don't need
an INF case there.
</details>

<details><summary>Rung 4 — reconstruction</summary>

At the root, take the S with the smallest `t[S]`. Going down, each child's subset is
the argmin you stored for `key = S_parent ∩ shared`. The cover is the union of all
chosen subsets, mapped back to vertices.
</details>

<details><summary>Functional route</summary>

A fold over the bag layers from the leaves up, whose accumulator is `{bag: {subset: best weight}}`. A bag's
table is a dict comprehension over the valid subsets of that bag. Each entry adds, per child, the best child
row that agrees on the shared vertices, minus the shared weight so it isn't counted twice. Reconstruction folds
top-down: the root takes its cheapest row, and each child takes its best row consistent with its parent's choice.
</details>
