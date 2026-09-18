# Lab 18 — Global constraints and their filtering algorithms

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 18`).
**You write:** 9 functions and 2 propagators in `lab.py`, 170–230 lines in all.
**Needs:** unit 17 (the engine) and unit 15 (Hopcroft–Karp), both loaded through `colib.ref`.

A constraint over n variables can see things that n(n−1)/2 pairwise constraints cannot.
Two cells that can only be 1 or 2 use up both values between them. A task that must run
during [3, 5) blocks its machine then. This lab builds the two most important global
constraints. **Alldifferent** uses Régin's matching-based filter, where unit 15 does
load-bearing work in a different tradition. **Cumulative** uses timetable reasoning.
Then you plug both into your unit-17 engine and watch the node counts collapse.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| Unit 17's engine as `cp` (Store, fixpoint, solve, LinearLe, Binary, NotEqual) | The value graph and its maximum matching |
| Unit 15's `hopcroft_karp` | AllDifferent with Régin's filtering, and the Hall set behind a removal |
| `colib.problems.JobShop` (with `ft06()`), `colib.oracle.brute_force` | Cumulative with timetable filtering |
| | Global and decomposed models, and minimisation by repeated search |

## Running it

```fish
uv run co test 18
uv run co test 18 --solution functional
CO_MINE=15,17 uv run co test 18       # on your own matching and engine
```

## Style

Régin's filter is reachability plus strongly connected components. The imperative reference
uses iterative Tarjan. The functional one computes each reachability as a set fixpoint and gets
SCCs as "reachable both ways". That's quadratic, but three lines instead of forty. Timetable
filtering is a pure function either way.

---

## Step 1 — The value graph  *(15 min)*

*Shape: a comprehension over variables and their domains.*

**Done when** `step 1 ✓`: the shifted values and edges are right, and your matching is perfect
exactly when brute force finds distinct values (Hall's theorem, 30 instances).

## Step 2 — Régin's alldifferent  *(60 min)*

*Shape: matching, orient, SCCs, reachability to free values, keep or remove each edge.*

**Done when** `step 2 ✓`: on 80 random instances, half with offsets, you keep **exactly** the
values with a support (brute force), and fail when no perfect matching exists. Every removal
comes with a valid Hall set (40 instances). On one example, pairwise ≠ prunes nothing while
yours fixes two variables.

*Think about:* why are "matched", "same SCC" and "can reach a free value" exactly the three
ways an edge can belong to some maximum matching? (Berge, unit 15: an edge is in some maximum
matching iff it's matched, or on an even alternating cycle, or on an even alternating path from a
free value.)

## Step 3 — Cumulative  *(35 min)*

*Shape: build a profile, fail on overload, then filter each task's starts.*

**Done when** `step 3 ✓`: your filter equals the timetable definition on 60 random instances
and never cuts a feasible schedule. A compulsory part pushes another task out, and an overload
fails.

## Step 4 — Models and minimisation  *(40 min)*

*Shape: model builders, and a loop that tightens an objective bound.*

**Done when** `step 4 ✓`. Global queens counts are right, with no more nodes than pairwise.
Inkala's sudoku needs **more than 5× fewer** nodes. Pigeonhole fails **at the root** with alldifferent,
and takes at least (n−1)! nodes pairwise. Job-shop minimisation matches brute force with both
machine models, and the node limit and the infeasible case behave.

---

## Then — the collapse, and a Hall set by name  *(10 min, runs ~80 s)*

```fish
uv run co then 18
```

**Your engine:**

| model | formulation | nodes | propagations | s |
|---|---|---:|---:|---:|
| queens 10, all | pairwise / global | 11 430 / 9 326 | 973 550 / 45 382 | 1.44 / 2.56 |
| sudoku (Inkala), all | pairwise / global | 3 598 / **102** | 823 458 / 3 272 | 1.14 / **0.18** |
| pigeonhole 10 into 9 | pairwise / global | 725 758 / **0** | 16 638 624 / 1 | 25.9 / **0.00** |
| ft06, 100 000 nodes | pairwise / cumulative | 55 found at node 588 / **116** | 2.4 M / 1.0 M | 19.0 / 12.9 |

On queens, alldifferent saves only 18% of the nodes and is slower: pairwise ≠ is already
nearly as strong there, and each Régin call costs a matching. On sudoku it cuts the tree 35×.
On pigeonhole it proves infeasibility with one propagation, where pairwise ≠ enumerates
permutations (725 758 nodes at 10 into 9). On ft06 both models find the optimum 55, the
cumulative model 5× sooner. **Neither proves it** in 100 000 nodes: timetable filtering is too
weak to bound the makespan. That needs edge-finding (slides), or the learning of units 20–21.

**The Hall set:** two decisions down the path to the solution, after pairwise ≠ has reached its
fixpoint, alldifferent on row 7 removes 2, 4 and 7 from r7c1 (domain {2, 4, 5, 7}), leaving 5. Cells
r7c2, r7c4, r7c5 and r7c6 hold only {2, 4, 7, 9} between them.

**CP-SAT:** all 2 680 solutions of queens 11 take 8.1 s pairwise and **2.1 s** with
`AddAllDifferent`. ft06 is solved to proven optimality (55) in 0.035 s with disjunctions and
0.018 s with `AddNoOverlap`. Pigeonhole disappears in presolve with either model.

## Checkpoint

- [ ] `uv run co test 18` shows all four steps ✓.
- [ ] **The curriculum's checkpoint:** on one instance your decomposed and global models give the
      same answer and differ by orders of magnitude in node count (pigeonhole: 725 758 vs 0),
      and you can name the Hall set responsible (`then` prints one on sudoku).
- [ ] You can explain why alldifferent is slower on queens and 6× faster on sudoku.

## Reading

- Régin, "A filtering algorithm for constraints of difference in CSPs", *AAAI* 1994.
- van Hoeve, "The alldifferent constraint: a survey", arXiv:cs/0105015 (2001).
- Baptiste, Le Pape & Nuijten, *Constraint-Based Scheduling* (2001), ch. 2–3: timetable,
  edge-finding, not-first/not-last.
- Beldiceanu, Carlsson & Rampon, *Global Constraint Catalog*
  (sofdem.github.io/gccat): 400+ global constraints, each with its filtering.
