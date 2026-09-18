# Lab 16 — Dynamic programming over combinatorial structure

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 16`).
**You write:** 8 functions in `lab.py`, 180–250 lines in all.
**Needs:** unit 09 and unit 07 appear in `then`. Unit 10 will reuse your step 1.

Every DP in this lab is a shortest path in a DAG of states. Knapsack's states are
capacities, and Held–Karp's are (subset, last city). A tree DP's states are
(vertex, in or out); a tree-decomposition DP's are (bag, subset of the bag). The
lab is about seeing what the state space *is*, since its size is the running time.
Knapsack is exponential in the number of digits of the capacity. Held–Karp is
exponential in n, but only as 2ⁿ rather than n!. The decomposition DP is
exponential in the width alone, and `then` plots it.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.graphs`: random trees, k-trees, partial k-trees | 0/1 and unbounded knapsack with reconstruction |
| Unit 07's B&B, unit 09's lazy TSP, SCIP, HiGHS (in `then`) | Held–Karp exact TSP |
| | Weighted vertex cover on a forest |
| | Tree decompositions: width, a checker, and a min-degree elimination builder |
| | Weighted vertex cover by DP over a tree decomposition |

## Running it

```fish
uv run co test 16
uv run co test 16 --solution functional
```

## Style

DP is where the functional style is at its best. A table is a dict comprehension
over states, each computed from a previous layer, so a DP is a fold over layers.
The functional reference folds over items, subset sizes and tree depths, then
reconstructs with an unfold back through the choices.

The imperative reference vectorises two DPs with numpy: knapsack (one array
operation per item) and Held–Karp (one per subset size and end city). That makes
Held–Karp at n = 20 take under a second. A plain-Python dict version (the functional
reference) takes 0.24 s at n = 14 and grows about ×2.5 per city, with memory
becoming the problem around n = 20. Either is fine for the tests.

---

## Step 1 — Knapsack  *(30 min)*

*Shape: a table over capacities, filled item by item, with a record of decisions.*
In the 0/1 version, each item may update each capacity once. That's why a 1-D table
needs the capacities in *decreasing* order, or a fresh row. In the unbounded
version, the increasing order lets an item be reused.

**Done when** `step 1 ✓`: brute force agrees on 40 instances plus 10 with fractional
values; capacity 100 000 runs within the limit. The unbounded version agrees on 30
instances plus 10 shaped like unit 10's pricing problem (float duals, roll width 100).

## Step 2 — Held–Karp  *(40 min)*

*Shape: subsets by increasing size; for each subset and each end city, the best
predecessor.* Keep the predecessor so you can rebuild the tour.

**Done when** `step 2 ✓`: brute force agrees on 25 Euclidean and 15 asymmetric
instances, the returned order starts at 0 and has the returned length, and n = 12
matches unit 09's exact solver.

## Step 3 — Vertex cover on trees  *(20 min)*

*Shape: children before parents, two numbers per vertex, then parents before
children to choose.* A child must be in the cover when its parent isn't.

**Done when** `step 3 ✓`: brute force agrees on 40 random forests, a 5 000-vertex path
runs without recursion errors, and a 300-vertex tree matches HiGHS.

## Step 4 — Tree decompositions  *(35 min)*

*Shape: a checker of four properties, then elimination.*

**Done when** `step 4 ✓`: your checker rejects each property's violation on its own.
Your elimination always yields a valid decomposition. Min-degree finds width exactly
k on k-trees, 2 on a cycle and 5 on K₆. The centre-first order on a star with six
leaves gives width 6.

*Think about:* why does eliminating the centre of a star first cost so much? What
does that say about how sensitive treewidth heuristics are to the ordering?

## Step 5 — Vertex cover over a decomposition  *(45 min)*

*Shape: bags children-first; for each bag, a table over its valid subsets; then
choices parents-first.*

**Done when** `step 5 ✓`: brute force agrees on 40 random graphs, including 10 with
random (bad) orderings. Three hand decompositions of a 4-cycle agree, as does one
rooted in the middle. Partial k-trees on 80 vertices match HiGHS.

---

## Then — three views of "exponential"  *(10 min, runs ~2 minutes)*

```fish
uv run co then 16
```

**Exact TSP**, Euclidean, seconds. `—` means dropped: over 60 s, or unit 07's B&B hit
20 000 nodes.

| n | optimum | Held–Karp | B&B (07) on MTZ | lazy DFJ (09) | SCIP on MTZ |
|---:|---:|---:|---:|---:|---:|
| 8 | 281 | 0.001 | 0.49 | 0.023 | 0.29 |
| 12 | 280 | 0.003 | 5.6 | 0.006 | 0.043 |
| 14 | 301 | 0.008 | 6.1 | 0.014 | 1.12 |
| 16 | 325 | 0.049 | — | 0.013 | 0.68 |
| 18 | 327 | 0.144 | — | 0.031 | 5.15 |
| 20 | 386 | 0.787 | — | 0.029 | 0.28 |

Held–Karp grows by ×3–6 per two cities, steady and predictable. Unit 07's B&B on the
weak MTZ formulation dies at n = 16. Lazy subtour elimination barely notices n,
because the DFJ relaxation is so strong on Euclidean instances. SCIP on MTZ is
erratic (5 s at n = 18, 0.3 s at n = 20). Held–Karp and the lazy DFJ solver cross
between n = 14 and 16. Beyond that, a strong formulation beats the DP, and the gap
only widens.

**Knapsack**, 50 items, weights scaled by 10ᵏ:

| capacity | 1 032 | 10 414 | 103 947 | 1 040 810 | 10 404 313 |
|---|---:|---:|---:|---:|---:|
| your DP (s) | 0.000 | 0.001 | 0.013 | 0.225 | 2.44 |
| HiGHS (s) | 0.027 | 0.019 | 0.020 | 0.017 | 0.019 |

Same items, same answer. Only the number of digits grew, and the DP paid 10× per digit.

**Decomposition DP** on partial k-trees, 150 vertices. The prediction is calibrated
once at k = 4, as (DP time at k = 4) / Σ2^|bag| × Σ2^|bag|:

| width | Σ 2^\|bag\| | DP (s) | predicted | HiGHS (s) |
|---:|---:|---:|---:|---:|
| 5 | 5 406 | 0.009 | 0.011 | 0.022 |
| 7 | 19 166 | 0.024 | 0.040 | 0.042 |
| 9 | 61 934 | 0.070 | 0.128 | 0.054 |
| 11 | 224 990 | 0.250 | 0.465 | 0.073 |

The prediction is within a factor of 2 at every width, which meets the checkpoint.
The time grows about ×1.8 with each unit of width. HiGHS doesn't care about width at all on
these instances, which is the caveat to "FPT is fast": the parameter must actually
be small.

## Checkpoint

- [ ] `uv run co test 16` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** given a decomposition, you can compute its width
      and predict the DP's runtime from it to within an order of magnitude (`then`
      does it within 2×).
- [ ] You can explain why an O(nC) knapsack algorithm doesn't show P = NP, in one
      sentence about input length.

## Reading

- Kleinberg & Tardos, ch. 6 (DP) and §10.4 (DP on tree decompositions).
- Cygan et al., *Parameterized Algorithms* (2015), ch. 7. Free online; the standard
  reference for treewidth DPs and "nice" decompositions.
- Held & Karp, "A dynamic programming approach to sequencing problems", *J. SIAM*
  10 (1962).
- Bodlaender, "A tourist guide through treewidth", *Acta Cybernetica* 11 (1993).
