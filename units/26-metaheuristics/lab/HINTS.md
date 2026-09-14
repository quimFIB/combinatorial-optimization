# Hints — lab 26

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — Tours and neighbour lists

<details><summary>Rung 1</summary>

`sum(dist[tour[i - 1]][tour[i]] for i in range(n))` closes the tour for free, because `tour[-1]` is the
last city. Neighbour lists are one sort per city with key `(dist[a][c], c)`. That's O(n² log n) in total,
which is the cost to beat in section 1 of `then`.
</details>

<details><summary>Functional route</summary>

Nearest neighbour is an unfold over the partial tour tuple, stopping when it has n cities.
</details>

## Step 2 — 2-opt with neighbour lists and don't-look bits

<details><summary>Rung 1 — the move, in positions</summary>

Successor direction: a at position i, b = tour[i+1], c at position j, d = tour[j+1]. Reversing
positions i+1 … j turns … a b … c d … into … a c … b d …: edges ab, cd become ac, bd. Predecessor
direction: b = tour[i−1], d = tour[j−1]. Reversing positions i … j−1 turns … b a … d c … into
… b d … a c …. Both stretches are cyclic (wrap around the end).
</details>

<details><summary>Rung 2 — why stop at dist[a][c] ≥ dist[a][b]</summary>

An improving move needs d_ac + d_bd < d_ab + d_cd, so d_ac < d_ab or d_bd < d_cd. The second case is
the same move seen from d, with d's neighbour b. So scanning each city's list only while it is
shorter than the tour edge being removed misses no improving move. With sorted lists that's
usually two or three entries.
</details>

<details><summary>Rung 3 — don't-look bits as a queue</summary>

A `deque` of cities and a `queued` array. Initially everything is queued. Pop a; if it has a move,
apply it and push a, b, c and d (those not already queued). A city whose neighbourhood hasn't changed
since it last found nothing stays asleep. `_reverse` should update `pos` as it swaps.
</details>

<details><summary>Functional route</summary>

`two_opt_move` is a generator of candidate moves, and `next(..., None)` takes the first. Rebuild the
tour tuple by rotating it to start at i and reversing a prefix. For the queue version, the state is
`(tour, queue tuple)`.
</details>

## Step 3 — Or-opt

<details><summary>Rung 1 — build the reduced tour once per segment</summary>

`rest = [tour[(i + L + k) % n] for k in range(n - L)]` starts at q and ends at p. Inserting the
piece after `rest[k]` gives `rest[:k+1] + piece + rest[k+1:]`: a fresh tour, no index gymnastics. The
move costs d(c, x) + d(y, e) − d(c, e), and it's improving if that's less than the gain from removing
the segment.
</details>

<details><summary>Rung 2 — local search</summary>

After Or-opt changes the tour, new 2-opt moves can appear. `then` found an instance of this
at n = 40 (the test uses it). Loop both until the length stops decreasing.
</details>

<details><summary>Functional route</summary>

`_or_move(tour)` returns the new tour or None. Iterate until None.
</details>

## Step 4 — Simulated annealing

<details><summary>Rung 1 — the O(1) delta</summary>

Reversing tour[i..j] replaces edges (tour[i−1], tour[i]) and (tour[j], tour[j+1]) with (tour[i−1],
tour[j]) and (tour[i], tour[j+1]). With i = 0, tour[i−1] is the last city, which is right. The only
degenerate case is reversing everything, which the docstring skips.
</details>

<details><summary>Rung 2 — order of random draws</summary>

Draw `sorted(rng.sample(range(n), 2))`, then `rng.random()`, every iteration, before deciding anything.
The scripted test replays exactly that order.
</details>

<details><summary>Functional route</summary>

A `reduce` over iteration numbers with state `(current, length, best, best_length)`. Slicing a
reversed segment is O(n), which is fine at test sizes.
</details>

## Step 5 — ALNS for CVRP

<details><summary>Rung 1 — worst removal</summary>

A customer's saving is d(prev, c) + d(c, next) − d(prev, next), with the depot at both ends of each
route. Recompute after each removal, since neighbours change. Break ties toward the lower customer
number with a key like `(saving, -c)`.
</details>

<details><summary>Rung 2 — greedy insertion</summary>

For each customer: for each route with spare capacity, for each gap k in 0 … len(route) (between
`[0, *route, 0][k]` and `[k+1]`), compute the extra distance. Keep a strict `<` so earlier options win
ties. With no feasible route, append `[c]`.
</details>

<details><summary>Rung 3 — the adaptive loop</summary>

`rng.choices(range(2), weights)[0]` picks an operator in proportion to its weight. Track `scores` and
`uses` per operator and reset them each segment. The acceptance rule is "record-to-record travel":
anything within 2% of the best so far is accepted, which lets the search move sideways.
</details>

<details><summary>Functional route</summary>

A `reduce` over iterations with an eight-field state. The segment update returns fresh score and
use lists.
</details>

## Step 6 — Time to target, and a test

<details><summary>Rung 1 — TTT points</summary>

Sort the successful times. The i-th point sits at height (i + ½)/N, where N counts *all* runs, so
failures pull the curve down instead of vanishing from it.
</details>

<details><summary>Rung 2 — Mann–Whitney by hand</summary>

Rank the pooled samples, giving ties their average rank. U = R₁ − n₁(n₁+1)/2. Under the null,
mean n₁n₂/2 and variance n₁n₂/12 · ((N+1) − Σ(t³−t)/(N(N−1))). With the continuity correction,
z = (|U − μ| − ½)/σ, and p = erfc(z/√2). If z comes out negative, use 0 (p = 1).
</details>

<details><summary>Rung 3 — the verdict</summary>

"Not significant" is not "equal". The honest output of a comparison that doesn't reject is
*no winner declared*, and `verdict` returns None for exactly that.
</details>

<details><summary>Functional route</summary>

`itertools.groupby` over the sorted pooled values gives the tie groups. `accumulate` of their sizes
gives each group's starting rank.
</details>
