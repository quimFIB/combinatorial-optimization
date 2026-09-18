# Lab 13 — Matroids and the exact reach of greedy

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 13`).
**You write:** 9 functions in `lab.py`, 90–130 lines in all.
**Needs:** only unit 00. This is the first unit of trunk B.

"When does greedy work?" has an exact answer: on matroids, and only on matroids.
This lab builds the oracles for four kinds of matroid and runs one generic greedy
on all of them. It recovers Kruskal's algorithm without writing it, and catches a
non-matroid by producing the exchange axiom's counterexample. Then it goes one step
beyond greedy (intersection of two matroids, which contains bipartite matching),
and one step beyond matroids (submodular coverage, where greedy is no longer exact
but is provably within 1 − 1/e).

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.polyhedra.rank` (exact) | Graphic, uniform, partition and linear matroid oracles |
| networkx, HiGHS (tests and `then`) | The generic greedy algorithm |
| | A brute-force matroid axiom checker that returns witnesses |
| | Matroid intersection by shortest augmenting paths |
| | Greedy maximum coverage |

## Running it

```fish
uv run co test 13
uv run co test 13 --solution functional
```

## Style

Oracles are closures, whichever style you use. Greedy is a fold over the sorted
ground set. The axiom checker is `next` over a chain of "violation" generators.
Intersection is an unfold over common independent sets.

---

## Step 1 — Oracles  *(30 min)*

*Shape: closures.* The graphic oracle is a union-find over the chosen edges, and
it fails on the first edge whose endpoints are already connected.

**Done when** `step 1 ✓`: small cases for each kind, and the graphic oracle matches
networkx's forest check on 600 random subsets.

## Step 2 — Greedy  *(15 min)*

*Shape: a fold.*

**Done when** `step 2 ✓`. With the graphic oracle, your greedy returns a
**maximum-weight spanning forest** on 25 random graphs, equal in weight to
networkx's. That makes it Kruskal's algorithm, which you never wrote.

## Step 3 — The axiom checker  *(25 min)*

*Shape: `next` over violations.*

**Done when** `step 3 ✓`: no witness for four real matroids; an exchange witness
for matchings in a path, which the test re-checks; and "empty" and "hereditary"
witnesses for two broken systems.

*Think about:* the test's path a-b-c-d has edges 0, 1, 2 = ab, bc, cd, and the
matching witness is ({1}, {0, 2}), that is A = {bc} and B = {ab, cd}: the middle
edge alone is maximal, but two disjoint edges exist. Greedy with weight 3 on the
middle edge and 2 on the others picks the middle one and stops at 3, while the
optimum is 4.

## Step 4 — Matroid intersection  *(45 min)*

*Shape: BFS in the exchange graph, then a symmetric difference.* The step to be
careful with is using **shortest** augmenting paths. A non-shortest path can break
independence.

**Done when** `step 4 ✓`: two partition matroids give maximum bipartite matching on
25 random graphs, and "forest ∩ at most one edge per colour" matches brute force
on 10.

## Step 5 — Greedy coverage  *(10 min)*

*Shape: a fold, marginal gain as the key.*

**Done when** `step 5 ✓`: the textbook order is right, and on 40 random instances
greedy covers at least (1 − 1/e) of the optimum.

---

## Then  *(5 min, runs ~5 s)*

```fish
uv run co then 13
```

1. **Greedy vs Kruskal.** Same weight every time. At 2180 edges the generic oracle
   takes 0.060 s against networkx's 0.003 s, because the oracle rebuilds a
   union-find on every call.
2. **Intersection vs Hopcroft–Karp.** Same matching size. At 118 edges it takes
   0.128 s against 0.0001 s. Generality costs three orders of magnitude.
3. **Greedy coverage, real ratio.** Over 45 instances of 40 sets and 120 elements
   (k = 3, 6, 10), the mean ratio is 0.98–0.99 and the worst 0.926, far above the
   worst-case 0.632.

## Checkpoint

- [ ] `uv run co test 13` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** shown a greedy algorithm someone proposes,
      you can either name the matroid underneath it or construct the instance where
      it fails. Try it on "schedule unit jobs with deadlines to maximise profit"
      (a matroid: which?) and "pick non-overlapping intervals of maximum total
      weight" (not: build the counterexample).
- [ ] You can explain why three-matroid intersection is NP-hard while two is
      polynomial (Hamiltonian path is an intersection of three).

## Reading

- Korte & Vygen, ch. 13 (matroids, greedy, intersection).
- Schrijver, *Combinatorial Optimization*, vol. B, ch. 39–41 (consulted).
- Krause & Golovin, "Submodular function maximization" (2014), §1–3, for 1 − 1/e.
