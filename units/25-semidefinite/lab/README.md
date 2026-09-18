# Lab 25 — Semidefinite relaxations

**Time:** about 2¼ hours. **Before:** the slides (`uv run co slides 25`).
**You write:** 13 functions in `lab.py`, 120–160 lines in all.
**Needs:** unit 24 (rounding against a relaxation), unit 04 (interior-point methods), unit 00 (MaxCut).

An LP relaxation gives each vertex a number. An SDP gives it a *vector*, and constrains the vectors
only through their inner products. For Max-Cut that's the difference between a useless bound (the
edge LP says every edge can be cut) and Goemans–Williamson's 0.878. This lab builds the SDP, turns its
solution back into vectors, rounds them with random hyperplanes, and computes the rounding's exact
expectation and the constant α_GW. Then it puts the SDP on a ladder of LP bounds, computes the Lovász
theta function, and adds the local search that turns a rounded cut into a locally optimal one.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| cvxpy with the CLARABEL interior-point solver | The weight matrix, the Max-Cut SDP, vectors from a Gram matrix |
| `colib.solvers.highs_lp` | Hyperplane rounding, its exact expectation, α_GW |
| Brute force, networkx graphs (tests); CP-SAT (`then`) | The edge LP and the triangle (metric) LP |
| | Lovász theta, graph complement |
| | One-flip local search; Goemans–Williamson end to end |

## Running it

```fish
uv run co test 25
uv run co test 25 --solution functional
```

The whole suite takes a few seconds, though most tests solve an SDP.

## Style

Most of this unit is linear algebra, and numpy already expresses it without mutation. The functional
reference differs from the imperative one mainly in step 3 (LP constraints as comprehensions) and step 5
(local search as an unfold over cuts).

---

## Step 1 — The SDP and its vectors  *(30 min)*

*Shape: a cvxpy model; an eigendecomposition.*

**Done when** `step 1 ✓`. On 12 random graphs the SDP solution has unit diagonal, is PSD, and its
value is between the brute-force optimum and the total weight. C₅ gives 5(1 − cos 4π/5)/2 ≈ 4.5225,
C₆ gives exactly 6, and the triangle 2.25. Your vectors reproduce random Gram matrices, a
rank-deficient one, and the PSD projection of an indefinite one, all with unit rows.

## Step 2 — Hyperplane rounding  *(35 min)*

*Shape: a Gaussian vector and signs; a sum of arccosines; a one-dimensional minimisation.*

**Done when** `step 2 ✓`. On 6 graphs the mean of 3 000 rounded cuts matches your exact expectation
within 5 standard errors. Three vectors 120° apart are separated with probability ⅔, and a dot product
of exactly 0 goes to side 1. α_GW = 0.8785672 at θ = 2.33112 rad, and the expected cut is ≥ α·SDP on
10 graphs.

*Think about:* the tests draw 3 000 samples to check an expectation you computed exactly. When is the
exact value worth having, and when would sampling be the only option?

## Step 3 — LP bounds  *(30 min)*

*Shape: build the constraints, call the LP.*

**Done when** `step 3 ✓`. The edge LP always returns the total weight. The triangle LP gives 4 on C₅,
6 on C₇, 4 on K₄ and 20/3 on K₅, and sits between OPT and the edge LP on 10 graphs. On three
negative-weight triangles, each of the three rotated inequalities is the one that binds.

## Step 4 — The Lovász theta function  *(20 min)*

*Shape: another cvxpy model.*

**Done when** `step 4 ✓`. θ(C₅) = √5, θ(Petersen) = 4, θ of the empty graph on 4 vertices is 4 and of
K₄ is 1. On 10 random graphs α(G) ≤ θ(G) ≤ χ(Ḡ), all computed by brute force.

## Step 5 — Local search and GW end to end  *(20 min)*

*Shape: a loop flipping the first improving vertex; a composition.*

**Done when** `step 5 ✓`. Local optima admit no improving flip and cut at least half the weight. The scan
restarts after every flip (two hand-traced graphs) and doesn't modify its input. GW's best of 30 rounds
is ≥ α·OPT on 6 graphs.

---

## Then — against exact Max-Cut  *(10 min, runs about 6 minutes)*

```fish
uv run co then 25
```

Ratios to the optimum proved by CP-SAT, mean of 5 graphs per row, 200 hyperplanes each:

| graph | edge LP | triangle LP | SDP | E[GW] | worst hyperplane | best of 200 | GW + local search |
|---|---:|---:|---:|---:|---:|---:|---:|
| G(12, 0.5) | 1.259 | 1.000 | 1.013 | 0.962 | 0.752 | 1.000 | 1.000 |
| G(20, 0.5) | 1.392 | 1.000 | 1.025 | 0.959 | 0.785 | 1.000 | 1.000 |
| G(30, 0.3) | 1.357 | 1.000 | 1.039 | 0.956 | 0.862 | 1.000 | 1.000 |
| G(40, 0.2) | 1.318 | — | 1.038 | 0.956 | 0.832 | 0.998 | 0.998 |

Things to notice:

- **GW's expected cut is 0.956–0.962 of the optimum**, well above 0.878, and the best of 200
  hyperplanes averaged 1.000 (to three decimals) for n ≤ 30. This is the checkpoint's first half.
- **Single hyperplanes can be bad.** The worst of the 4 000 cut 0.752 of OPT, below α. The guarantee is
  about the *expectation*.
- **On these small graphs the triangle LP was tighter than the SDP**, and matched the optimum to three
  decimals wherever it was run (n ≤ 30). The SDP's advantage is asymptotic and in the worst case. Setting
  every z to ⅔ satisfies all the triangle inequalities, so on dense random graphs the triangle LP stays
  at ⅔ or more of the total weight while the optimum tends to ½. It also has Θ(n³) constraints.
- **Why 0.878 is nonetheless tight** (the checkpoint's second half): C₅'s SDP vectors sit 144° apart,
  where rounding recovers 0.8845 of each edge's SDP value. Graphs whose vectors all sit near 133.6°
  push the ratio of expected GW to SDP down to α. Feige & Schechtman (2002) built graphs where the SDP is
  also 1/α times OPT, so no rounding of this SDP can do better. Under the Unique Games Conjecture no
  polynomial algorithm can (unit 22).

**θ sandwiched** between α(G) and χ(Ḡ): C₅ 2 < 2.236 < 3, C₇ 3 < 3.318 < 4, Petersen 4 = 4 < 5, and the
5-cube 16 = 16 = 16. On three random G(14, ½) graphs, θ was integral twice and 5.109 once.

**Cost:** the SDP took 0.26 s at n = 35, 3.1 s at 60, 18.8 s at 100 and 150 s at 150: growing like
n^3.5 to n^5 over this range. CP-SAT's proof took 0.01, 0.14 and 1.38 s at n = 15, 25 and 35, and timed
out (60 s) at n = 60. The triangle LP took 1.9 s at n = 35.

## Checkpoint

- [ ] `uv run co test 25` shows all five steps ✓.
- [ ] You can show empirically that your GW cuts average well above 0.878 of optimum (`then`), and explain
      why the guarantee is nonetheless tight in all three senses: the per-edge angle, gap instances for
      the SDP, and UGC hardness.
- [ ] You can say why SDPs stay a theoretical tool at scale, with the numbers from `then`.

## Reading

- Goemans & Williamson, "Improved approximation algorithms for maximum cut and satisfiability problems
  using semidefinite programming", *JACM* 42 (1995).
- Williamson & Shmoys (2011), ch. 6. Free online.
- Lovász, "On the Shannon capacity of a graph", *IEEE Trans. Inf. Theory* 25 (1979).
- Laurent & Rendl, "Semidefinite programming and integer programming", in *Handbook on Discrete
  Optimization* (2005): the hierarchy of relaxations.
