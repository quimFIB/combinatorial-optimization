# Lab 22 — Hardness, and the shape of what is possible

**Time:** about 2 hours. **Before:** the slides (`uv run co slides 22`).
**You write:** 10 functions in `lab.py`, 120–170 lines in all.
**Needs:** unit 00 (the problem classes and oracle), unit 16 (the knapsack DP), unit 20 (CNF).

A reduction is a program. It maps instances one way and solutions back, and it can have bugs. This
lab mechanises the first links of the canonical NP-completeness chain: CNF → 3-CNF, 3-SAT → vertex
cover, vertex cover → set cover. Each solution map is checked both ways against brute force and exact
solvers. Then it builds the knapsack FPTAS: the best possible approximation, available only because
knapsack's hardness lives in the magnitude of its numbers (unit 16). The slides cover the rest of the
hierarchy (PTAS, APX, log-APX, poly-APX, no ratio at all) and where each of unit 00's nine problems sits.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.problems.VertexCover`, `SetCover`; `colib.oracle.brute_force` | The 3-SAT → vertex cover reduction and both solution maps |
| pysat, HiGHS (tests); CP-SAT and unit 16's DP (`then`) | CNF → 3-CNF by clause splitting, and assignment extension |
| | Vertex cover → set cover, and the composed chain |
| | Exact knapsack by value, and the FPTAS |

## Running it

```fish
uv run co test 22
uv run co test 22 --solution functional
```

## Style

Reductions are pure functions between instance types, so the functional reference is the natural
one. The clause splitter is a fold that threads the next fresh variable number.

---

## Step 1 — 3-SAT to vertex cover  *(35 min)*

*Shape: literal edges, clause triangles, links; then two solution maps.*

**Done when** `step 1 ✓`. The gadget has exactly the textbook vertices and edges. On 20 tiny formulas
(unsatisfiable ones included), a brute-force minimum cover is ≤ k exactly when the formula is
satisfiable, and never below k. On 15 larger ones, checked with HiGHS, both solution maps work. The
all-eight-clauses formula needs exactly k + 1.

*Think about:* why k + 1 for the all-eight formula, where every assignment leaves exactly one clause
unsatisfied? Is the excess over k always the fewest unsatisfied clauses? (See `then`.)

## Step 2 — Clause splitting  *(25 min)*

*Shape: four cases per clause, fresh variables threaded through.*

**Done when** `step 2 ✓`: every output clause has width 3, and 40 random CNFs are equisatisfiable with
their images. Models extend forwards and restrict backwards, clause and variable counts are exact, and
chain variables take the documented values.

## Step 3 — Vertex cover to set cover  *(15 min)*

*Shape: one comprehension.*

**Done when** `step 3 ✓`: the same vectors are feasible with the same costs on both sides, brute-force
optima agree on 20 graphs, and the composed 3-SAT → set cover chain decides satisfiability on 8 formulas.

## Step 4 — The knapsack FPTAS  *(35 min)*

*Shape: a DP over values, then the same DP on scaled values.*

**Done when** `step 4 ✓`: the value DP is exact on 30 instances, and the FPTAS stays within 1 − ε on 90
(three ε each). It includes an instance where scaling by ε·vmax (without ÷ n) fails, and one where an
item that can never fit would otherwise set the scale.

---

## Then — both sides by CP-SAT  *(10 min, runs ~20 s)*

```fish
uv run co then 22
```

**3-SAT → vertex cover:**

| n | m | satisfiable | vertices | edges | k = n + 2m | min cover | agrees |
|---:|---:|---|---:|---:|---:|---:|---|
| 20 | 60 | yes | 220 | 380 | 140 | 140 | ✓ |
| 20 | 100 | yes | 340 | 620 | 220 | 220 | ✓ |
| 40 | 170 | **no** | 590 | 1 060 | 380 | **381** | ✓ |
| 40 | 170 | yes | 590 | 1 060 | 380 | 380 | ✓ |
| 60 | 255 | **no** | 885 | 1 590 | 570 | **571** | ✓ |
| 60 | 360 | **no** | 1 200 | 2 220 | 780 | **782** | ✓ (4.3 s) |

The excess over k says *something* about how unsatisfiable the formula is, but not exactly. An
assignment leaving u clauses unsatisfied gives a cover of k + u, so the excess is at most the MaxSAT
cost. It can be smaller: covering *both* literals of one variable costs 1 and may satisfy several clause
gadgets at once. On 300 small random formulas (checked with RC2), the excess was below the fewest
unsatisfied clauses on 19. A reduction that preserves yes/no answers need not preserve the size of
gaps. Reductions that do are what hardness of approximation needs (slides).

**Vertex cover → set cover:** optima agree on G(30, 0.2) up to G(150, 0.04) (92 = 92). CP-SAT takes about
the same time on both sides (4.0 s and 4.4 s at 150 vertices): the reduction is size-preserving.

**Knapsack**, 100 items, values up to 10⁶: the exact weight DP (unit 16) takes 0.05 s, and the FPTAS
takes 0.11 s at ε = 0.5 up to 2.43 s at ε = 0.02. Its **actual loss is 0.000%** at every ε. The worst-case
guarantee is loose in practice, and with modest capacities the pseudo-polynomial exact DP is faster.
The FPTAS earns its place when both values and weights are huge: time polynomial in n and 1/ε,
whatever the numbers.

## Checkpoint

- [ ] `uv run co test 22` shows all four steps ✓.
- [ ] **The curriculum's checkpoint:** for each of unit 00's nine problems you can state the best known
      approximation ratio and hardness bound, and say where the gap is still open. The slides' table is
      the answer key; try it first.
- [ ] You can say why knapsack has an FPTAS and bin packing (also about numbers) cannot, unless P = NP.

## Reading

- Garey & Johnson, *Computers and Intractability* (1979), ch. 3: the reduction chain.
- Williamson & Shmoys, *The Design of Approximation Algorithms* (2011), ch. 3 (knapsack FPTAS) and ch. 16
  (hardness of approximation). Free online.
- Arora & Barak, *Computational Complexity* (2009), ch. 11 and 22: PCP and hardness of approximation.
- Khot, "On the Unique Games Conjecture", *CCC* 2010: a survey.
