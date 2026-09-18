# Lab 27 — Modelling for a real solver

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 27`).
**You write:** 9 functions in `lab.py`, 130–180 lines in all.
**Needs:** unit 05 (formulations), unit 07 (branch and bound), unit 08 (cuts), unit 10 (patterns).

A solver's speed on a model depends as much on the model as on the solver. This lab takes the
textbook bin-packing model, which is the classic slow one (one bin per item, interchangeable bins, a
weak LP), and applies one intervention at a time: link the capacity constraints, break the symmetry, bound
the bin count from both sides, offer a start, and finally reformulate. Every intervention must leave
the optimum unchanged, and the tests check that it does. Then `then` measures each one separately. The
measurements are the lesson: most single-run differences between interventions are smaller than
SCIP's run-to-run variation, and you have to find that out before writing the checkpoint table.

**About the choice of model.** The curriculum says "your worst-performing model from units 05 and 07".
Unit 05's facility-location models and unit 07's knapsacks were already small or strong. Bin packing's
assignment model is the canonical weak, symmetric one, and it's one of unit 00's nine problems.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| pyscipopt (SCIP 10) | The assignment model, unlinked and linked, integer or LP |
| Exact bin packing by DP over subsets (tests) | Symmetry-breaking constraints |
| `_quiet`, `_number` helpers | First-fit decreasing, Martello–Toth L2, the bounded model |
| | A MIP start |
| | The arc-flow model |
| | A parser for SCIP's statistics report |

## Running it

```fish
uv run co test 27
uv run co test 27 --solution functional
```

## Style

A solver model is mutable by nature: you build it by calling `addVar` and `addCons`. The functional
reference keeps those calls, but computes the constraints, the start values and the arc set as values first.
First-fit decreasing, L2 and the parser are pure. The lab sheet says so rather than pretending otherwise.

---

## Step 1 — The assignment model  *(25 min)*

*Shape: two families of variables, three families of constraints.*

**Done when** `step 1 ✓`. Both variants find the DP optimum on 10 instances. The LP bound is exactly 1
unlinked and exactly Σsizes/C linked, and the constraint counts are right.

## Step 2 — Symmetry breaking  *(15 min)*

*Shape: n − 1 constraints and a triangle of fixed variables.*

**Done when** `step 2 ✓`. The optimum is unchanged on 10 instances, two symmetric copies are cut off
(item 1 in bin 2, bin 1 used while bin 0 is empty), and a canonical packing is still allowed.

## Step 3 — Bounds from both sides  *(30 min)*

*Shape: a greedy packing; a max over α; a composition.*

**Done when** `step 3 ✓`. FFD is a valid packing within 11/9·OPT + 6/9 on 20 instances.
⌈Σ/C⌉ ≤ L2 ≤ OPT, and L2 catches six items of 51 and two hand-built cases that need α > 0 and the
boundary items. The bounded model has FFD-many bins, fixes exactly min(FFD, L2) of them, and keeps
the optimum.

## Step 4 — A MIP start  *(20 min)*

*Shape: set every variable; check; add.*

**Done when** `step 4 ✓`. The FFD packing is accepted, and with heuristics, presolve and cuts off and
a one-node limit SCIP still reports a solution at most as good. An overfull bin and a missing item are
rejected. A packing whose bins would violate the symmetry breaking is renumbered and accepted.

## Step 5 — Arc flow  *(30 min)*

*Shape: a graph on 0..C; flow conservation; demand constraints.*

**Done when** `step 5 ✓`. The optimum matches the DP on 10 instances, the LP is at least the
assignment LP and at most OPT, three items of 51 get LP value 3 (the assignment LP says 1.53), and a
hand-counted instance has exactly the right variables and constraints.

## Step 6 — Reading the log  *(20 min)*

*Shape: a line-oriented parser keyed by section and column name.*

**Done when** `step 6 ✓`. On a live 2-second solve, your nodes, bounds, gap and first LP value match
SCIP's API, and on a fixed report you get "nodes (total)" rather than "nodes", top-level separators
without the `>` family rows, and the heuristic that found the best solution. An infinite gap reads as
None.

---

## Then — one intervention at a time  *(15 min, runs about 30 minutes)*

```fish
uv run co then 27
```

Ten instances (six uniform with 40 items in 20–60 and C = 100, four "triplets" where 30 items fill
10 bins exactly), SCIP with a 20 s limit, shifted geometric mean with shift 1 s:

| configuration | solved | SGM s | median nodes | mean final gap |
|---|---:|---:|---:|---:|
| A  x ≤ y linking, n bins | 6/10 | 9.97 | 942 | 3.65% |
| B  capacity linked to y | 8/10 | 5.32 | 870 | 2.07% |
| B′ same, SCIP symmetry handling off | 8/10 | 4.00 | 601 | 1.89% |
| C  B + symmetry breaking | 9/10 | 3.80 | 598 | 0.62% |
| D  C + FFD bin count, L2 fixing | 10/10 | 3.43 | 1 380 | 0.00% |
| E  D + FFD as MIP start | 9/10 | 3.02 | 1 576 | 0.62% |
| **F  arc flow** | **10/10** | **1.40** | **1** | **0.00%** |

That looks like a tidy staircase. It isn't one. Wherever two consecutive rows disagreed about solving
an instance, `then` re-ran both with three more SCIP random seeds (seconds, 20.0 = not solved):

| instance | earlier row, 4 seeds | later row, 4 seeds |
|---|---|---|
| uniform #2, A → B | 20 20 20 20 | 16.7 20 8.8 20 |
| triplets #1, A → B | 20 13.8 12.5 20 | 6.4 1.9 3.1 2.0 |
| triplets #3, B → B′ | 20 15.3 20 1.7 | 1.6 11.3 2.8 11.4 |
| uniform #3, B′ → C | 20 2.9 7.1 8.6 | 2.9 3.2 9.6 10.7 |
| uniform #2, D → E | 15.9 19.3 1.9 20 | 20 1.7 10.0 4.9 |
| uniform #2, E → F | 20 1.7 10.1 4.9 | **0.4 0.4 0.3 0.3** |

What survives the variability:

- **A → B (linking) helps**: the weak LP bound of 1 against Σ/C shows up in the gap column and in the
  seed re-runs (triplets #1: never under 12 s unlinked, never over 6.4 s linked).
- **F (arc flow) helps, by up to 40× on the hardest uniform instance, and it's stable**: 0.3–0.4 s
  across four seeds on the instance where every assignment variant ranged from 1.7 s to the time limit.
  Its LP already proves optimality (median 1 node). On the triplets it's *slower* (3.7–5.1 s against
  1.3–3.7 s for C–E): C = 1000 makes the arc-flow graph ten times larger.
- **B → B′ → C → D → E are within noise** on this set. One run each would have produced a confident
  and wrong story: "symmetry handling off is faster", "the MIP start costs a solve". Two plausible
  reasons, which this experiment doesn't test: SCIP's own symmetry detection may already remove much of
  what explicit symmetry breaking would, and a single FFD start may matter little when SCIP's heuristics
  find packings as good early on. Each is a hypothesis for your notes, with the experiment that would
  test it.

**The time-limit effect.** An earlier run of the same script with the same seeds solved 5/10 for A and
9/10 for B, where this one solved 6/10 and 8/10. Runs that finish near the limit flip with machine
load. A solved-count difference of one, from one run, is not evidence.

The run between those two crashed with a missing node count in one statistics report, and that didn't recur.
`then` now saves any report your parser can't read to `out/unparsed_statistics.txt` and carries on.

**MIPLIB** (section 2) needs files you download yourself from miplib.zib.de into `lab/miplib/`. That
path hasn't been run here.

## Checkpoint

- [ ] `uv run co test 27` shows all six steps ✓.
- [ ] **A before/after table of your own model with one row per intervention and the time each bought,
      containing no row you cannot explain.** For rows within noise, "within noise, and here are the seed
      re-runs" *is* the explanation.
- [ ] You can read a SCIP statistics report and say where the time went: presolve, root LP, cuts by
      family, heuristics, tree.

## Reading

- Achterberg & Wunderling, "Mixed integer programming: analyzing 12 years of progress", in *Facets of
  Combinatorial Optimization* (2013).
- Lodi & Tramontani, "Performance variability in mixed-integer programming", *TutORials in OR* (2013).
- Margot, "Symmetry in integer linear programming", in *50 Years of Integer Programming* (2010).
- Valério de Carvalho, "Exact solution of bin-packing problems using column generation and branch-and-bound",
  *Annals of OR* 86 (1999).
- Delorme, Iori & Martello, "Bin packing and cutting stock problems: mathematical models and exact
  algorithms", *EJOR* 255 (2016).
