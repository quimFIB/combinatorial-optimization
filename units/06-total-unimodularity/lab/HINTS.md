# Hints — lab 06

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — TU by definition

<details><summary>Rung 1</summary>

For k = 1..min(m, n): for every `rows` in `combinations(range(m), k)` and `cols` in
`combinations(range(n), k)`, take the submatrix and check its determinant.
Checking k = 1 separately (every entry in {−1, 0, 1}) is a cheap early exit.
</details>

<details><summary>Rung 2 — exact determinants</summary>

Gaussian elimination over `fractions.Fraction`: pick a nonzero pivot in the
column (swap rows, flip the sign), divide, eliminate below, and multiply the
pivots. Or Bareiss: integer-only, `M[i][j] = (M[i][j]*M[k][k] - M[i][k]*M[k][j]) // prev`,
where the division is always exact.
</details>

<details><summary>Functional route</summary>

TU is a universal quantifier over square submatrices, so write it as one: `all(det in (−1, 0, 1) for
(rows, cols) in squares)`, with `squares` a generator over sizes and `combinations` of rows and columns.
`all` stops at the first bad minor. The exact determinant is a fold over pivot columns whose accumulator is
`(rows as a tuple, determinant so far)`: swap in a nonzero pivot, multiply the determinant, and rebuild the
rows below as new tuples.
</details>

## Step 2 — Ghouila-Houri

<details><summary>Rung 1</summary>

For each nonempty subset `rows`, try every signing `(1,) + signs` for `signs` in
`product((1, -1), repeat=len(rows) - 1)`. It is equitable if, for every column
*j*, `abs(sum(s * A[r][j] for s, r in zip(sigma, rows))) <= 1`. Return the first
subset with no equitable signing.
</details>

<details><summary>Functional route</summary>

`next((rows for rows in subsets if not any(equitable(rows, sigma) for sigma in signings(rows))), None)`.
</details>

## Step 3 — The matrices

<details><summary>Rung 1</summary>

Incidence: `[[int(v in e) for e in edges] for v in range(n)]`. Interval:
`[[int(a <= j < b) for j in range(n)] for a, b in intervals]`.
</details>

<details><summary>Functional route</summary>

Both matrices are a single nested comprehension over a membership test: `int(v in e)` for incidence and
`int(a <= j < b)` for intervals.
</details>

## Step 4 — Assignment as an LP

<details><summary>Rung 1</summary>

Variable `k = i*n + j`. Row for worker *i*: 1 where `k // n == i`. Row for job *j*:
1 where `k % n == j`. Stack both families, `b = [1]*(2n)`, then
`highs_lp(A, b, c, sense="min", row_lower=b)` makes every row an equality (upper and
lower bound both 1). The default variable lower bound is 0.
</details>

<details><summary>Functional route</summary>

Build the two families of equality rows as generators (`k // n == i` for rows, `k % n == j` for columns),
`chain` them, and make one `highs_lp` call. The reshape to n × n is the only step after it.
</details>

## Step 5 — The odd cycle

<details><summary>Rung 1 — where the cycle is</summary>

BFS from each unvisited vertex, recording `parent` and `depth`. An edge (u, w)
with `depth[u] % 2 == depth[w] % 2` joins two vertices of the same colour, so the
graph isn't bipartite. The two tree paths from u and w up to their lowest common
ancestor, plus the edge (u, w), form an odd cycle.
</details>

<details><summary>Rung 2 — building the list</summary>

Walk the deeper endpoint up until the depths are equal, then walk both up together
until they meet. With `left = [u, …, lca]` and `right = [w, …, lca]`, the cycle is
`left + right[-2::-1]`: u … lca … w, and w is adjacent to u.
</details>

<details><summary>Rung 3 — the half-integral point</summary>

`{frozenset((cycle[i], cycle[(i + 1) % k])): 0.5 for i in range(k)}`. It is optimal
because every vertex constraint is tight, and on an odd cycle that system has a
unique solution.
</details>

<details><summary>Functional route</summary>

BFS is an unfold over `(parent, depth, frontier)`, cut off by `takewhile` when the frontier empties. The forest
is a fold over start vertices that skips those already reached. The clash is `next` over the edges whose
endpoints have equal depth parity. Each walk to the root is `tz.iterate` over parents with `takewhile(not
None)`. The meeting point is the first vertex of one walk that's in the other, and the cycle is two slices
joined.
</details>
