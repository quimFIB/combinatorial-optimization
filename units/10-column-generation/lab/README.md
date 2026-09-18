# Lab 10 — Column generation

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 10`).
**You write:** 9 functions in `lab.py`, 150–220 lines in all.
**Needs:** unit 03 (duals, reduced costs), unit 16 (the knapsack DP, used as the pricer).

Some LPs have too many columns to write down: every way to cut a roll, every
vehicle route. Column generation solves them anyway. It keeps a small restricted
master, reads its duals, and asks a pricing problem whether any missing column has
negative reduced cost. Here the pricing problems are a knapsack and a shortest path
with a capacity. The lab builds the cutting-stock method end to end, measures the
bound it gets for free, tries stabilisation, and then prices vehicle routes, where
the pricing problem becomes the hard part.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.colgen`: cutting-stock and CVRP instances, the compact Kantorovich model | The restricted master and its duals |
| `highs_lp`, `highs_mip` | Pricing by knapsack, and the Farley bound |
| Unit 16's `unbounded_knapsack` (reference, or yours with `CO_MINE=16`) | The column-generation loop |
| | Rounding and the restricted master IP |
| | Wentges dual smoothing |
| | ESPPRC labelling and the CVRP LP bound |

## Running it

```fish
uv run co test 10
uv run co test 10 --solution functional
CO_MINE=16 uv run co test 10         # price with your own unit-16 knapsack
```

## Style

The loop is an unfold. Its state is the column set (plus the centre and best bound in
step 5), and it stops at the first state where pricing finds nothing. The functional
reference writes it that way, and writes ESPPRC as a fold over path lengths that keeps
only non-dominated labels. The LP solves are calls to HiGHS, which is fine: they are
pure functions of the columns.

---

## Step 1 — The restricted master  *(25 min)*

*Shape: build A (items × patterns) and call `highs_lp`.* The demand constraints are
covering: `row_lower = demands`, `b = inf`.

**Done when** `step 1 ✓`: on the initial patterns the value is Σ dᵢ / ⌊W/wᵢ⌋. On larger
pattern sets your duals are nonnegative, dual feasible (no pattern prices above 1), and
satisfy d·y = value.

## Step 2 — Pricing and the free bound  *(20 min)*

*Shape: one call to the knapsack, and one line for the bound.*

**Done when** `step 2 ✓`: your pattern matches the best of all patterns by brute force,
and the Farley bound never exceeds the full LP.

*Think about:* why is d·y / v a lower bound for **any** y ≥ 0? (Divide y by v and check
it's dual feasible.)

## Step 3 — The loop  *(25 min)*

*Shape: master, price, record, add or stop.*

**Done when** `step 3 ✓`: on 25 instances you reach the LP over **all** patterns. The
master value never rises, the bound is a lower bound, and the two meet at the end. On a
30-item instance, no pattern with negative reduced cost remains.

## Step 4 — Integer solutions  *(15 min)*

*Shape: `ceil`, and the same matrix with integrality.*

**Done when** `step 4 ✓`: both are feasible, and ⌈LP⌉ ≤ restricted IP ≤ round-up. The
restricted IP is never better than the true optimum over all patterns.

## Step 5 — Dual smoothing  *(30 min)*

*Shape: step 3 with a centre, and a fallback when the smoothed point mis-prices.*

**Done when** `step 5 ✓`: same LP values and valid bounds, alpha = 0 reproduces step 3
exactly, and on three 30-item small-width instances the total number of iterations
drops.

## Step 6 — Routes  *(50 min)*

*Shape: labels by path length, dominance per customer, then step 3's loop with
set-partitioning constraints.*

**Done when** `step 6 ✓`: your best reduced cost matches a brute force over all customer
sets (Held–Karp per set) on 60 instances. 40 of those use high duals and roomy vehicles,
where a dominance rule that ignores visited sets gives wrong answers. The CVRP LP
matches the LP over all routes, and never exceeds the integer optimum.

---

## Then — why the technique exists  *(10 min, runs ~4 minutes)*

```fish
uv run co then 10
```

**Compact model vs column generation** (W = 1000; HiGHS gets 30 s on the Kantorovich model):

| items | rolls K | vars | Kantorovich LP | HiGHS best / bound | CG LP | patterns | CG s | restricted IP |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 117 | 1 287 | 108.5 | none / 109 | 110.71 | 24 | 0.02 | **111** |
| 20 | 129 | 2 709 | 124.1 | none / 125 | 124.21 | 75 | 0.14 | **125** |
| 40 | 309 | 12 669 | 301.0 | none / 302 | 301.07 | 178 | 0.62 | **302** |

In 30 seconds HiGHS finds **no feasible solution at all** on any of these. The
Kantorovich LP is the trivial bound Σ wᵢdᵢ / W, and the model is riddled with symmetry
among identical rolls. Column generation plus a restricted IP solves every instance to
proven optimality, since ⌈CG LP⌉ = restricted IP, in under a second. With 200 small
items and demands of 100–1000, the compact model would need **2.2 million variables**.
Column generation reaches its LP with 577 patterns (61 s, 378 iterations).

**Farley stopping:** at 20 / 40 / 80 items, ⌈bound⌉ = ⌈master⌉ after 47 / 132 / 192 of
56 / 139 / 203 iterations. It saves 5–16%. The long tail comes after the answer is
already known.

**Smoothing** (small items, iterations): 64 → 58 at 25 items and 121 → 102 at 50 items
with α = 0.8, but no faster in seconds. Each iteration now prices twice when it
mis-prices. Wentges smoothing helps most when the master's duals oscillate badly; here
it's a modest win.

**CVRP** (capacity 20):

| n | LP bound | routes | s | restricted IP | gap |
|---:|---:|---:|---:|---:|---:|
| 8 | 342.00 | 46 | 0.01 | 342 | 0.0% |
| 12 | 422.00 | 78 | 0.09 | 470 | 10.2% |
| 16 | 478.15 | 187 | 2.95 | 483 | 1.0% |
| 20 | 662.00 | 260 | 27.8 | 738 | 10.3% |

Pricing time grows roughly ×10–30 per four customers: elementary labelling is exponential, and
this is the step where column generation stops being a toy. The restricted IP gap is
not the LP gap. The routes generated at the LP optimum rarely contain a good integer
solution, and closing that needs branch-and-price with branching compatible with
pricing (see the slides). Production codes relax elementarity (ng-routes) and add
cuts (rounded capacity inequalities, subset-row cuts).

## Checkpoint

- [ ] `uv run co test 10` shows all six steps ✓.
- [ ] **The curriculum's checkpoint:** you can explain, in unit 03's vocabulary, why the
      master's dual values are exactly the objective coefficients of the pricing
      problem. (The reduced cost of column a is c(a) − yᵀa; minimising it over all
      columns is pricing.)
- [ ] You can say why branching on a master variable x_p ≤ 0 breaks the pricing
      problem, and what Ryan–Foster branching does instead.

## Reading

- Desrosiers & Lübbecke, "A primer in column generation", in *Column Generation*
  (Springer, 2005). The best 30-page introduction.
- Lübbecke & Desrosiers, "Selected topics in column generation", *Operations Research*
  53 (2005): stabilisation, branching, bounds.
- Gilmore & Gomory, "A linear programming approach to the cutting-stock problem",
  *Operations Research* 9 (1961).
- Costa, Contardo & Desaulniers, "Exact branch-price-and-cut algorithms for vehicle
  routing", *Transportation Science* 53 (2019). The state of the art that step 6 points
  towards.
