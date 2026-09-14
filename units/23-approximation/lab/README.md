# Lab 23 — Combinatorial approximation algorithms

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 23`).
**You write:** 16 functions in `lab.py`, 150–200 lines in all.
**Needs:** unit 13 (greedy, MST), unit 15 (matching), unit 22 (the hierarchy).

An approximation algorithm is a solution *plus a proof*. The proof always compares the solution
to a lower bound on OPT that can be computed: a dual built from prices, a matching, a set of points
far apart, a spanning tree, the total processing time. This lab makes each algorithm return that
lower bound alongside its answer, so the tests check the proof's inequalities one by one, not only
the final ratio. Every step also has a *tight instance* where the proof's slack is used up
completely.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.approx.metric_tsp` (metric closure of rounded Euclidean distances) | Greedy set cover with prices; H_k; the tight family |
| `colib.approx.min_weight_perfect_matching` (Edmonds' weighted blossom, via networkx) | Maximal-matching vertex cover; farthest-first k-center |
| Held–Karp (unit 16), HiGHS, brute force: optima for the tests | Prim, shortcutting, the double tree |
| CP-SAT (`then` only) | Odd vertices, Hierholzer's Euler circuit, Christofides |
| | List scheduling, LPT, and both tight families |

**About the matching.** Unit 15 built the *cardinality* blossom algorithm. The weighted version adds
dual variables on vertices and blossoms, and it runs to several hundred careful lines: a unit of its own. So it's
given here. Christofides only needs it as a black box: a minimum-weight perfect matching on the odd
vertices.

**About metric instances.** `TSP.random` rounds Euclidean distances to integers, which can break the
triangle inequality by one unit. Every proof in this lab needs the triangle inequality exactly, so the
tests use its shortest-path closure.

## Running it

```fish
uv run co test 23
uv run co test 23 --solution functional
```

## Style

Greedy algorithms are unfolds: a state, and a step that makes one greedy choice. The functional
reference writes each as `tz.iterate` over immutable states, and list scheduling as a fold. Hierholzer's
algorithm is the least natural fit. Its functional version threads a stack, a set of unused edges and
the partial circuit through the same kind of unfold.

---

## Step 1 — Greedy set cover  *(30 min)*

*Shape: a loop choosing the best ratio; a harmonic sum; one instance builder.*

**Done when** `step 1 ✓`. On 50 random instances the result is a cover whose element prices sum to its
cost, and every set S satisfies the **price lemma** Σ_{e∈S} price_e ≤ H_|S|·c_S. Cost stays within
H_d of the brute-force optimum. Two hand-built instances pin down the ratio and tie-breaking, and on
the tight family greedy pays exactly L·H_n against an optimum of L + 1.

## Step 2 — Lower bounds from packings  *(30 min)*

*Shape: a fold over edges; farthest-first with a nearest-distance array.*

**Done when** `step 2 ✓`. The matching is maximal, its endpoints form a cover, and
|M| ≤ OPT ≤ cover ≤ 2·OPT against HiGHS. On K_{n,n} the cover is exactly 2·OPT. For k-center, every
new centre was a farthest point when chosen, the k + 1 points (centres and witness) are pairwise at
least the radius apart, and the radius is ≤ 2·OPT by brute force. Ties go to the lowest index.

*Think about:* both proofs exhibit a set of objects no single solution element can serve twice. What is
the "packing" in each?

## Step 3 — Prim and the double tree  *(25 min)*

*Shape: O(n²) Prim with best-edge arrays; a preorder walk; first occurrences.*

**Done when** `step 3 ✓`. Prim's weight matches networkx's MST on 15 instances. The double tree visits
children in increasing order (two hand-built trees), and on 20 instances
tour ≤ 2·MST and MST ≤ OPT (Held–Karp).

## Step 4 — Christofides  *(35 min)*

*Shape: a degree count; Hierholzer with a stack; three calls composed.*

**Done when** `step 4 ✓`. Euler circuits use every edge of 25 random Eulerian multigraphs exactly once,
from the requested start. On 30 metric instances, tour ≤ MST + matching, 2·matching ≤ OPT, and so
tour ≤ 3/2·OPT, with the matching weight equal to the optimum on your tree's odd vertices.

**The checkpoint asks** you to point at the line of code for each step of the 3/2 proof. Do it in
`NOTES.md`: the MST line (MST ≤ OPT), the matching line (≤ OPT/2), the Euler line (every degree even),
and the shortcut line (triangle inequality).

## Step 5 — Scheduling  *(25 min)*

*Shape: a fold over jobs; a sort and a write-back; two list comprehensions.*

**Done when** `step 5 ✓`. On 30 brute-forced instances, list scheduling is within 2 − 1/m and LPT
within 4/3 − 1/(3m), with loads consistent with the reported makespan. Both tight families reach their
bounds exactly: 2m − 1 against m, and 4m − 1 against 3m.

---

## Then — ratios against CP-SAT optima  *(10 min, runs a few minutes)*

```fish
uv run co then 23
```

| algorithm | instances | mean ratio | worst ratio | guarantee |
|---|---|---:|---:|---:|
| greedy set cover | 20 × (120 elements, 80 sets) | 1.173 | 1.302 | H_d ≈ 3.6 |
| matching vertex cover | 20 × G(n, p), n = 50..200 | 1.53–1.59 | 1.736 | 2 |
| farthest-first k-center | 15 × 80 points, k = 3, 6, 10 | 1.64 / 1.42 / 1.28 | 1.909 | 2 |
| double tree | 30 × metric TSP, n = 20, 40, 60 | 1.30–1.37 | 1.486 | 2 |
| **Christofides** | same | **1.10–1.14** | **1.194** | 1.5 |
| list scheduling | 60 × P‖C_max, n/m = 12/3, 30/5, 60/10 | 1.11–1.14 | 1.282 | 2 − 1/m |
| **LPT** | same | **1.01–1.03** | **1.070** | 4/3 − 1/(3m) |

Things to notice:

- **Worst case and typical case are far apart** for set cover (1.3 against 3.6), Christofides and LPT.
  They are much closer for the matching cover (up to 1.74 of 2) and for k-center with small k (up to
  1.91 of 2): the simplest lower bounds leave the least room.
- **The lower bounds themselves**: MST/OPT averages 0.82–0.87 and matching/OPT about 0.33, against the
  proof's 1 and 0.5. Christofides loses less than its analysis allows at *both* steps, and shortcutting
  recovers more.
- **Tight families are exact**: 5/3, 9/5 and 19/10 for list scheduling, and 11/9, 19/15 and 39/30 for
  LPT. Greedy set cover on its family gives 3.381 at n = 16, where H₁₆ = 3.381. The guarantees are
  theorems about these instances, not about the random ones above.
- CP-SAT proves every TSP optimum here in under 2 s on average (n = 60). That's why approximation is a
  last resort for *these* sizes, and why unit 26 moves to instances where it isn't.

## Checkpoint

- [ ] `uv run co test 23` shows all five steps ✓.
- [ ] Your Christofides never exceeds 1.5× the optimum on instances you can solve exactly (step 4's tests
      and `then`). In `NOTES.md` you can point at the line of code for each step of the proof.
- [ ] You can explain why the double tree's 2 and Christofides' 3/2 both need the triangle inequality,
      and what goes wrong without it (unit 22: general TSP has no ratio at all).

## Reading

- Williamson & Shmoys, *The Design of Approximation Algorithms* (2011), ch. 1–2. Free online.
- Vazirani, *Approximation Algorithms* (2001), ch. 2–3 (set cover, Steiner tree and TSP).
- Christofides, "Worst-case analysis of a new heuristic for the travelling salesman problem", CMU report
  388 (1976). Serdyukov found the same algorithm independently (1978).
- Karlin, Klein & Oveis Gharan, "A (slightly) improved approximation algorithm for metric TSP", *STOC* 2021.
