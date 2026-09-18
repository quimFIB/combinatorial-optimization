# Lab 15 — Matching

**Time:** about 3 hours, plus a stretch session for the blossom algorithm.
**Before:** the slides (`uv run co slides 15`).
**You write:** 6 functions and a checker in `lab.py`, 140–220 lines in all.
**Needs:** unit 14 (augmenting paths) and unit 03 (duality, complementary slackness).

Matching is where the three threads of the course meet. Hopcroft–Karp is a flow
algorithm specialised to unit capacities. König's theorem is LP duality on a
totally unimodular matrix. The Hungarian method is the primal–dual method, with
the potentials in plain sight. Then Edmonds' blossom shows what changes when the
graph stops being bipartite and the LP stops being integral. Gale–Shapley is here
for contrast: it's also called matching, but it optimises no weight at all. Its
correctness is a stability argument, not duality (though, surprisingly, stable
matchings turn out to be the vertices of a polytope too).

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| scipy, OR-Tools, networkx, HiGHS (tests and `then`) | Hopcroft–Karp |
| | König's vertex cover from a maximum matching |
| | The Hungarian method, returning its dual potentials |
| | A checker that proves an assignment optimal from the potentials |
| | Gale–Shapley and a stability check |
| | *Stretch:* Edmonds' blossom algorithm |

## Running it

```fish
uv run co test 15
uv run co test 15 --solution functional
```

## Style

Hopcroft–Karp, König and Gale–Shapley are natural unfolds and fixpoints. The
functional reference writes the Hungarian method as a fold over rows, each row an
unfold over immutable `(u, v, p, way, minv, used)`. It's longer than the loop, but
every potential update is one visible expression. Its Hopcroft–Karp augments one
shortest path per round instead of a whole phase: same answer, worse bound.

**The blossom step is the exception.** Its base relabelling is a mutable
union-find, and a persistent version hides the algorithm rather than showing it.
`solution/functional.py` just calls the imperative one, and you should feel free to
do the same.

---

## Step 1 — Hopcroft–Karp  *(35 min)*

*Shape: phases of BFS layering and DFS augmentation.* Keep `match_l` and `match_r`.
The layer array does double duty: it guides the DFS, and it marks dead ends.

**Done when** `step 1 ✓`: the greedy trap is solved, and 40 random bipartite graphs
match networkx in size, with every matched pair a real edge.

## Step 2 — König's cover  *(20 min)*

*Shape: one alternating reachability search.* The cover is read off the reached set,
and there is no optimisation to do.

**Done when** `step 2 ✓`: on 40 graphs your set covers every edge and its size equals
the matching's. Size equality is the certificate. A cover must be at least as large
as any matching, so equal sizes prove both optimal.

## Step 3 — The Hungarian method  *(50 min)*

*Shape: add one row at a time; for each, a Dijkstra over columns with the potentials
shifted in place.* Work 1-based internally, with a virtual column 0 as the root; the hint
ladder explains why this removes every special case.

**Done when** `step 3 ✓`: 40 integer instances, 10 with negative costs, 10 with
fractional costs, and one 60 × 60, all equal to `scipy.optimize.linear_sum_assignment`.

## Step 4 — The certificate  *(15 min)*

*Shape: three `all(...)`s.* It takes permutation, dual feasibility and complementary
slackness together: remove any one and a wrong answer can pass.

**Done when** `step 4 ✓`: your Hungarian's potentials certify every answer, and
`sum(u) + sum(v) == total`. The checker rejects infeasible duals, slack assigned
pairs, non-permutations, and any worse assignment paired with the optimal duals.

*Think about:* the tests never call scipy for step 4. That's the point. The
potentials are a proof that anyone can check in O(n²).

## Step 5 — Gale–Shapley  *(25 min)*

*Shape: a queue of free proposers.* Pre-compute each receiver's rank table, so a
comparison is O(1).

**Done when** `step 5 ✓`: every result is perfect and stable, proposer-optimal against
all stable matchings found by brute force, and `is_stable` agrees with the definition
on every permutation.

## Step 6 — Blossom  *(stretch; one hard session)*

*Shape: from each free root, a BFS alternating tree with base relabelling on odd
cycles.* Follow the hints closely. The algorithm is short, but each line matters.

**Done when** `step 6 ✓`: the triangle with pendants, the Petersen graph (perfect),
and 150 random graphs all match networkx's maximum cardinality.

---

## Then — against scipy, OR-Tools and networkx  *(5 min, runs ~5 s)*

```fish
uv run co then 15
```

**Assignment** (costs uniform in 0‥10⁶, seconds; all four agree on every total):

| n | yours | scipy | OR-Tools | HiGHS LP |
|---:|---:|---:|---:|---:|
| 50 | 0.002 | 0.0001 | 0.0014 | 0.051 |
| 100 | 0.012 | 0.0003 | 0.0056 | 0.046 |
| 200 | 0.085 | 0.0016 | 0.022 | 0.233 |
| 400 | 0.505 | 0.0063 | 0.089 | 1.332 |

scipy's C shortest-augmenting-path code is about 80× faster than yours at n = 400. Both
are O(n³), so the gap is all constant factor. OR-Tools' cost-scaling push–relabel sits
in between. The general LP solver is slowest, but its vertex has **zero** fractional
entries every time: unit 06's integrality, seen in practice.

**Bipartite matching** (average degree 4): your Hopcroft–Karp takes 0.004 / 0.014 /
0.070 s at 1 000 / 4 000 / 16 000 vertices a side. networkx takes 0.011 / 0.052 /
0.317 s: pure Python on both sides, and networkx pays for its graph objects.

**General matching** (average degree 3): your blossom takes 0.009 s at n = 800 and
0.068 s at 2 000. networkx's `max_weight_matching` takes 0.097 and 0.635 s. It solves
the *weighted* problem, with dual variables on every blossom, so it's no fair race.
At n = 2 000 the bipartite double cover allows a larger matching than the graph has:
odd cycles really constrained the answer.

## Checkpoint

- [ ] `uv run co test 15` shows steps 1–5 ✓ (6 if you took the stretch).
- [ ] **The curriculum's checkpoint:** you can verify your Hungarian algorithm's answer
      is optimal from its dual potentials alone, without re-running anything, and say
      which LP those potentials are feasible for.
- [ ] You can explain why König's theorem fails on a triangle, and which inequality
      (an odd-set inequality) repairs the LP.

## Reading

- Korte & Vygen, ch. 10 (maximum matchings) and ch. 11 (weighted matching).
- Schrijver, *A Course in Combinatorial Optimization*, ch. 3 and 5. Free online and
  compact.
- Edmonds, "Paths, trees, and flowers", *Canad. J. Math.* 17 (1965). Section 2 is
  the argument for polynomial time as the definition of "good algorithm".
- Gale & Shapley, "College admissions and the stability of marriage", *Amer. Math.
  Monthly* 69 (1962). Nine pages.
