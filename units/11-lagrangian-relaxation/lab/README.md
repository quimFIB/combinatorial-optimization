# Lab 11 — Lagrangian relaxation and subgradient methods

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 11`).
**You write:** 8 functions in `lab.py`, 120–180 lines in all.
**Needs:** unit 03 (duality), unit 16 (the knapsack DP), unit 09 (the subtour LP, in tests and `then`).

Move the constraints that make a problem hard into the objective, priced by
multipliers. What remains is easy: a spanning tree, a set of knapsacks, one choice per
job. Every multiplier vector then gives a lower bound, and subgradient ascent looks for
the best one. The lab builds the Held–Karp bound for TSP and uses it to throw away most
edges. It then relaxes the generalised assignment problem in two ways: one that can
beat the LP and one that provably cannot. Knowing which is which before running
anything is the checkpoint.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.colgen.GAP`, `TSP.random`, unit 16's `knapsack` | The minimum 1-tree under multipliers |
| Unit 09's subtour LP and exact TSP (tests, `then`) | Generic subgradient ascent, and the Held–Karp bound |
| | Variable fixing by 1-tree reduced costs |
| | Two Lagrangian relaxations of GAP |
| | A Lagrangian repair heuristic for GAP |

## Running it

```fish
uv run co test 11
uv run co test 11 --solution functional
```

## Style

A relaxation is a function from multipliers to (bound, solution, subgradient), and the
ascent is an unfold over (multipliers, step size, best so far). That's how the functional
reference is written, with Prim's algorithm as a fold that adds one vertex at a time. The
imperative reference is the textbook loop.

---

## Step 1 — The 1-tree  *(25 min)*

*Shape: Prim's O(n²) on 1..n−1, then the two cheapest edges at 0.*

**Done when** `step 1 ✓`: the weight matches networkx's MST plus two edges on 30 instances.
Every multiplier vector gives at most the optimal tour length. On points on a circle, the
1-tree **is** the tour.

## Step 2 — Subgradient ascent  *(30 min)*

*Shape: a loop with a best-so-far, a patience counter, and the Polyak step.*

**Done when** `step 2 ✓`: it finds the maximum of a simple concave function, stops at once
on a zero subgradient, respects a projection, and halves the step on schedule. On TSP your
bound is ≤ the optimum, your returned π reproduces it, and at n = 20 and 30 it's within 1%
of the subtour LP without exceeding it.

*Think about:* why must it never exceed the subtour LP? (The Lagrangian dual of the 1-tree
relaxation *is* the subtour LP.)

## Step 3 — Edge fixing  *(25 min)*

*Shape: for each vertex, the heaviest edge on the tree path to every other vertex.*

**Done when** `step 3 ✓`: no edge of an optimal tour is ever fixed. On small instances your
fixed set matches a brute-force "cheapest 1-tree containing e" for three thresholds. At
n = 25, with the optimum as the upper bound, you fix at least 80% of the edges.

## Step 4 — Two relaxations of GAP  *(30 min)*

*Shape: m knapsacks, or n independent argmins.*

**Done when** `step 4 ✓`: both give valid bounds and correct subgradients. The capacity
relaxation never beats the LP but converges to it. The assignment relaxation beats the LP
by more than 1 on at least half of 12 instances.

## Step 5 — Lagrangian repair  *(25 min)*

*Shape: keep the cheapest copy, then place by regret.*

**Done when** `step 5 ✓`: every result is feasible and no better than the optimum. It
succeeds on at least 75% of instances and is within 5% of the optimum on at least 60%. It
keeps the cheapest duplicate, orders by regret, and returns None when stuck.

---

## Then — how close, and why  *(10 min, runs ~40 s)*

```fish
uv run co then 11
```

Put TSPLIB files (EUC_2D) in `data/tsplib/` and they're added to table 1.

**TSP bounds:**

| instance | optimum | degree LP | subtour LP | Held–Karp | gap | iterations | s | edges fixed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| random 30 | 482 | 470.5 | 480.50 | 480.50 | 0.31% | 523 | 0.1 | 89% |
| random 60 | 627 | 572.5 | 621.50 | 621.50 | 0.88% | 547 | 0.3 | 89% |
| random 100 | 776 | 744.0 | 771.50 | 771.50 | 0.58% | 589 | 1.0 | 93% |
| random 150 | 921 | 873.0 | 918.75 | 918.27 | 0.30% | 1000 | 3.6 | 96% |

Held–Karp matches the subtour LP to two decimals up to n = 100, and is 0.05% short at
n = 150 when the iteration limit stops it. **That's the unit:** the Lagrangian dual of
the 1-tree relaxation equals the LP over the subtour polytope, because the spanning-tree
polytope (plus the degree constraint at vertex 0) has the integrality property. Its
extreme points are 1-trees. So Lagrange can't beat the subtour LP, and a good ascent
reaches it without ever solving an LP. With the bound 0.3–0.9% below the optimum, 89–96%
of the edges provably can't appear in any optimal tour.

**GAP** (tightness 0.9, 300 iterations each):

| m × n | optimum | LP | bound A (knapsacks) | bound B (one agent per job) | heuristic |
|---|---:|---:|---:|---:|---:|
| 5 × 25 | 452 | 444.13 | **452.00** | 444.12 | 452 |
| 5 × 40 | 682 | 671.18 | **682.00** | 671.12 | 682 |
| 8 × 60 | 905 | 892.37 | **902.83** | 892.33 | none |
| 10 × 80 | 1084 | 1072.32 | **1083.71** | 1072.27 | 1178 |

A closes 83–100% of the LP gap, and B reaches the LP and stops. The knapsack has no
integrality property: its convex hull can be strictly smaller than its LP polytope. The one-agent
choice in B has the integrality property, so B can never do better than the LP.

**The zig-zag** (bound A on 8 × 60, iterations 31–300): with the patience rule, about half
of all steps go *down*, and it still ends at 902.83. With a fixed λ = 2 it bounces between
887 and 899 for good. With a small fixed λ = 0.1 it climbs smoothly but stalls at 895.9.
Subgradient methods aren't ascent methods. Keep the best, and shrink the step.

## Checkpoint

- [ ] `uv run co test 11` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** before writing any code, you can predict whether
      dualising a constraint set will beat the LP relaxation, using the integrality
      property. Try: in unit 05's uncapacitated facility location, dualise "every customer
      is served". Does the bound beat the strong (disaggregated) LP? (Look at one
      facility's subproblem, with x_j ≤ y and 0 ≤ y ≤ 1.)
- [ ] You can explain why edge fixing is safe, and why it needs an upper bound.

## Reading

- Geoffrion, "Lagrangean relaxation for integer programming", *Math. Programming Study* 2
  (1974). The integrality property.
- Held & Karp, "The traveling-salesman problem and minimum spanning trees", *Operations
  Research* 18 (1970), and Part II, *Math. Programming* 1 (1971).
- Held, Wolfe & Crowder, "Validation of subgradient optimization", *Math. Programming* 6
  (1974). The step rule used here.
- Fisher, "The Lagrangian relaxation method for solving integer programming problems",
  *Management Science* 27 (1981; reprinted 2004). Still the best tutorial.
