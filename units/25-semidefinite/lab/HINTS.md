# Hints — lab 25

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — The SDP and its vectors

<details><summary>Rung 1 — cvxpy</summary>

`X = cp.Variable((n, n), PSD=True)` declares the cone. Each edge counts once in the objective, but
`cp.sum(cp.multiply(W, 1 - X))` counts it twice (W is symmetric), so divide by 4, not 2. The only
other constraint is `cp.diag(X) == 1`. Then `problem.solve(solver="CLARABEL")` and
`np.array(X.value)`.
</details>

<details><summary>Rung 2 — from Gram matrix to vectors</summary>

`vals, vecs = np.linalg.eigh(X)` gives X = Q Λ Qᵀ. Then V = Q Λ^{½} satisfies V Vᵀ = X, with row i
as v_i. The solver's X can have eigenvalues like −3e−9, so clip them to 0 before the square root.
Clipping changes the diagonal slightly, so renormalise each row. Symmetrise first with
`(X + X.T) / 2`.
</details>

<details><summary>Functional route</summary>

`np.bincount(rows * n + cols, weights=..., minlength=n*n).reshape(n, n)` builds W with no in-place
writes. The vectors are one expression.
</details>

## Step 2 — Hyperplane rounding

<details><summary>Rung 1 — a uniform direction</summary>

A vector of independent standard normals is rotation-invariant, so its direction is uniform on the
sphere. Uniform [0, 1) entries are not, and the tests can tell. Then x_i = [v_i·r ≥ 0].
</details>

<details><summary>Rung 2 — the expectation</summary>

Project onto the plane of v_u and v_v. The hyperplane separates them iff its trace in that plane, a
uniformly random line, falls inside the angle between them: probability θ_uv/π. Clip the dot product
into [−1, 1] before `math.acos`, since rounding can put it at 1.0000000002.
</details>

<details><summary>Rung 3 — α_GW</summary>

Per edge, the rounding gets θ/π while the SDP counts (1 − cos θ)/2. The worst ratio over θ ∈ (0, π]
is α ≈ 0.87856, at θ ≈ 133.6°. A grid of 10⁵ points already gets the value right to many digits (the
ratio is flat there). A golden-section refinement nails the angle.
</details>

<details><summary>Functional route</summary>

`np.einsum("ij,ij->i", V[us], V[vs])` gives all the edge dot products at once. Write golden-section
search as `tz.nth(60, tz.iterate(shrink, bracket))`.
</details>

## Step 3 — LP bounds

<details><summary>Rung 1 — the edge LP</summary>

Variables: n x's then m z's. Two rows per edge: z − x_u − x_v ≤ 0 and z + x_u + x_v ≤ 2. Call
`highs_lp(A, b, c, sense="max", upper=1.0)`. Before running it, predict the value. (x = ½ everywhere.)
</details>

<details><summary>Rung 2 — the triangle LP</summary>

One variable per pair i < j, indexed by `combinations`. For each triple i < j < k, with
a = (i,j), b = (j,k), c = (i,k), the four rows are z_a + z_b + z_c ≤ 2, z_a − z_b − z_c ≤ 0,
−z_a + z_b − z_c ≤ 0 and −z_a − z_b + z_c ≤ 0. Every cut satisfies them: a triangle is cut in 0 or 2
edges. Non-edges get objective 0, but their variables still matter.
</details>

<details><summary>Functional route</summary>

One comprehension over `(triple, pattern)` pairs produces `(row, rhs)`. `zip(*rows)` splits them.
</details>

## Step 4 — Lovász theta

<details><summary>Rung 1</summary>

`cp.Maximize(cp.sum(X))` with `cp.trace(X) == 1` and `X[u, v] == 0` per edge. Sanity checks: the
empty graph gives n, the complete graph 1, C₅ gives √5 ≈ 2.236.
</details>

<details><summary>Rung 2 — why the sandwich</summary>

For an independent set S, X = 1_S 1_Sᵀ/|S| is feasible with value |S|, so α ≤ θ. The upper bound,
χ of the complement (a clique cover), comes from the dual: an orthonormal representation built from
a colouring. That's the notes' territory. The tests check both inequalities by brute force.
</details>

<details><summary>Functional route</summary>

A cvxpy model is a value you build and then solve, so write the constraints as one list: `[trace(X) == 1] +
[X[u, v] == 0 for (u, v) in edges]`. The complement graph is a comprehension over `combinations(range(n), 2)`
minus a frozenset of sorted edges.
</details>

## Step 5 — Local search

<details><summary>Rung 1</summary>

The gain of flipping v is (weight to same-side neighbours) − (weight to other-side neighbours).
Flip the first vertex with positive gain, then restart the scan from vertex 0. Copy x first. Every
flip strictly increases an integer-valued cut, so the loop ends.
</details>

<details><summary>Rung 2 — why ½</summary>

At a local optimum every vertex has at least half its incident weight crossing the cut. Summing over
vertices counts each edge twice: cut ≥ ½·total ≥ ½·OPT.
</details>

<details><summary>Functional route</summary>

An unfold: `step(cut)` returns the flipped tuple or None. Take states while not None and keep the
last.
</details>
