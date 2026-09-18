# Lab 06 — Total unimodularity: when integrality is free

**Time:** about 2 hours. **Before:** the slides (`uv run co slides 06`).
**You write:** 7 functions in `lab.py`, 70–100 lines in all.
**Needs:** unit 03. This is a branch unit, and it explains why Part III's
problems are easy.

Some integer programs need no branching at all, because their LP relaxation
already has integer vertices. This lab tests for the property two ways, builds
the matrices that have it, watches an LP return an integral assignment unasked,
and then finds the smallest structure that breaks it: an odd cycle.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.solvers.highs_lp` | TU by the definition, with exact determinants |
| networkx, scipy (tests and `then` only) | TU by Ghouila-Houri, with a witness when it fails |
| | Incidence and interval matrices |
| | The assignment problem as a plain LP |
| | An odd cycle, and the half-integral vertex on it |

## Running it

```fish
uv run co test 06
uv run co test 06 --solution functional
```

## Style

Steps 1 and 2 are quantifiers over finite sets. The functional reference writes
each as a single `all`/`any`/`next` over `combinations` and `product`. Step 5 is
BFS; the functional version is an unfold over frontiers.

---

## Step 1 — TU by definition  *(30 min)*

*Shape: `all` over pairs of row and column subsets.* The subtle part is exact
determinants. Floats would need a tolerance, and a determinant of 2 must never be
rounded to 1. Use Fractions, or Bareiss's fraction-free elimination.

**Done when** `step 1 ✓`: six known matrices (the triangle's incidence matrix is
not TU, a network matrix is), and agreement with a reference on 40 random
0/±1 matrices.

## Step 2 — Ghouila-Houri  *(25 min)*

*Shape: `next` over subsets of a failing `any` over signings.*

**Done when** `step 2 ✓`: it agrees with TU on 60 random matrices, and every
witness it returns is checked by trying all 2^|R| signings.

*Think about:* why can you fix the first row's sign to +1 without loss? (Negating
every sign negates the sum.)

## Step 3 — The matrices that are TU  *(15 min)*

*Shape: comprehensions.*

**Done when** `step 3 ✓`. The test checks that your incidence matrix is TU
**exactly** when the graph is bipartite, over 30 random graphs, and that interval
matrices are TU.

## Step 4 — Assignment as an LP  *(20 min)*

*Shape: 2n equality constraints, then one solver call.*

**Done when** `step 4 ✓`: the solution is integral on 10 random instances,
although nothing asked for integers, and it matches SciPy's assignment solver.

## Step 5 — The odd cycle  *(30 min)*

*Shape: BFS with parent pointers, then a walk up to the common ancestor.* An edge
joining two vertices on the same side of the BFS layering closes an odd cycle.

**Done when** `step 5 ✓`: valid odd cycles on 60 random graphs, None on
bipartite ones, and your half-integral point equals the LP optimum that HiGHS
finds on odd cycles of length 3, 5 and 7.

---

## Then  *(5 min, runs ~3 s)*

```fish
uv run co then 06
```

1. **Assignment LP vs `linear_sum_assignment`.** Integral every time, from n = 20 to
   150. At n = 150 the LP takes 0.73 s and the special-purpose solver 0.0007 s.
   Integrality is free, and speed isn't.
2. **Matching LP on random graphs.** On 203 bipartite graphs the LP vertex was
   never fractional. On 197 non-bipartite graphs it was fractional 42 times, and
   the only fractional value ever seen is **0.5**.
3. **Brute-force TU cost.** At 10×10 there are 184 755 square submatrices, and the
   check takes 1.4 s (22 s in the Fraction-based functional reference). A
   polynomial test exists (Seymour's decomposition), but in modelling you
   *recognize* TU structure rather than test for it.

## Checkpoint

- [ ] `uv run co test 06` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** given a constraint matrix, you can decide
      whether to expect integral LP optima, and when the answer is no, construct
      the odd cycle that breaks it.
- [ ] You can explain why a network flow LP with integer capacities has an
      integer optimal flow, using the words "totally unimodular" and "Cramer's rule".

## Reading

- Wolsey, ch. 3 (§3.1–3.3); or Conforti, Cornuéjols & Zambelli, ch. 4 (§4.1–4.3).
- Schrijver, *Combinatorial Optimization*, vol. A, ch. 5 (TU matrices and
  network matrices), consulted rather than read.
- Optional: Schrijver, *Theory of Linear and Integer Programming*, ch. 19–20, for
  Seymour's decomposition.
