# Lab 07 — Branch and bound

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 07`).
**You write:** 6 functions in `lab.py`, 90–130 lines in all.
**Needs:** unit 05, whose facility-location models this lab solves. The LPs are
solved for you by HiGHS through `colib.bb.solve_node`, so the lab is about the
tree.

You build the search tree every MILP solver is built on, with pluggable branching
rules, and instrument it. `then` compares all six rule/selection combinations
with SCIP and HiGHS on the same instances, and the ratio in node count is
your **factor of shame**. Unit 08 then explains a large part of that factor.

## Given, and what you write

| Given in `colib.bb` / `colib.mip` | Yours in `lab.py` |
|---|---|
| `solve_node(milp, lb, ub)` → `NodeLP` | Most-fractional branching, and the two children |
| `BBResult`, `is_integral`, `INT_TOL` | The tree: bounding, pruning, incumbents, best-first and DFS |
| `multi_knapsack`, unit 05's `ufl_aggregated` | The product score |
| `scip_mip`, `highs_mip` (tests, `then`) | Pseudocost branching, from the history the tree records |
| | Strong branching, with its probe LPs counted |

## Running it

```fish
uv run co test 07          # ~8 s: many small trees
uv run co test 07 --solution functional
```

## Style

The tree is a loop over a frontier, whichever style you use. The functional
reference keeps the frontier as a sorted tuple (best-first) or a tuple used as a
stack (DFS) inside a frozen `Search` state, and unfolds it with
`toolz.iterate`. It produces exactly the same node counts as the imperative one.
Don't recurse: trees here reach thousands of nodes.

---

## Step 1 — Most fractional, and children  *(15 min)*

*Shape: argmax with a tie-break; two tuple rebuilds.*

**Done when** `step 1 ✓`: continuous variables are ignored, ties go to the lowest
index, None is returned for an integral point, and children tighten exactly one
bound.

## Step 2 — The tree  *(60 min)*

*Shape: a loop over a frontier.* Pop, prune by bound, accept an integral point,
or branch and push the surviving children. Record per-unit gains as you go, since
step 4 needs them.

**Done when** `step 2 ✓`. On 9 instances, with both selections, you find the
optimum (checked against SCIP), the solution is feasible, and there is one LP per
node. Best-first uses no more nodes than DFS overall, and branches in
nondecreasing bound order, never above the optimum. Infeasible MILPs (including
one whose LP is feasible) and the node limit are handled.

*Think about:* why does best-first never branch on a node whose bound is above
the optimum, and why can DFS?

## Step 3 — The product score  *(5 min)*

A one-liner, but it is the part real solvers agree on: it rewards variables that
improve **both** children.

## Step 4 — Pseudocosts  *(30 min)*

*Shape: averages from a dict, then argmax.* Estimate each child's gain from past
gains per unit of fractionality.

**Done when** `step 4 ✓`: the choice from a handcrafted history is right, the
recorded gain on a tiny problem is exactly 1.0 per unit, the weighting by
fractionality flips a choice when it should, and results are optimal on all 9
instances.

## Step 5 — Strong branching  *(30 min)*

*Shape: probe, score, argmax.* Solve both children of each candidate, for real.

**Done when** `step 5 ✓`: optimal on all 9 instances, probes are counted, and
across the instances strong branching uses **fewer nodes but more LP solves** than
most-fractional.

---

## Then — the factor of shame  *(10 min, runs ~25 s)*

```fish
uv run co then 07
```

Totals over two 22×3 knapsacks and the 8×20 weak facility-location model:

| rule | selection | nodes | LP solves | seconds |
|---|---|---:|---:|---:|
| most-fractional | dfs | 5 141 | 5 141 | 3.2 |
| most-fractional | best | 1 923 | 1 923 | 1.3 |
| pseudocost | best | 1 581 | 1 581 | 1.1 |
| strong | best | **1 271** | 4 641 | 3.2 |

On knapsack #1, strong branching took 1 039 nodes, SCIP with presolve and cuts off
took 203, SCIP default 161, and HiGHS default 208. On the facility-location model
SCIP and HiGHS solved it at the root node; you need 75–89 nodes.

Read the SCIP and HiGHS logs (`scip_mip`/`highs_mip` accept settings) and write
down which of their features you believe explains the gap. Unit 08 tests the
hypothesis about cuts, and unit 27 the one about presolve.

## Checkpoint

- [ ] `uv run co test 07` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** your strong-branching variant beats your
      most-fractional variant on node count while losing on wall time, and you can
      explain that trade-off in terms of LP solves per node.
- [ ] You can say what reliability branching is and why it exists, given your
      pseudocost numbers.

In `NOTES.md`: your totals table, and your written hypotheses about SCIP's advantage.

## Reading

- Wolsey, ch. 7 (branch and bound).
- Achterberg, Koch & Martin, "Branching rules revisited", *Operations Research
  Letters* 33 (2005). Most-fractional, pseudocost, strong and reliability
  branching, measured.
- Optional: Achterberg's thesis *Constraint Integer Programming* (2007), ch. 5–6,
  for how SCIP does it.
