# Lab 26 — Metaheuristics, benchmarked honestly

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 26`).
**You write:** 20 functions in `lab.py` (plus an optional helper), 250–320 lines in all.
**Needs:** unit 19 (LNS, runtime distributions), unit 23 (tours, insertion), unit 24.

Metaheuristics give up proofs for speed, so the only evidence for one is measurement. That makes two
skills equally important. The first is engineering: 2-opt that scans only near neighbours, and only
until they get too far, does a tiny fraction of the work of the textbook version that tries every
pair of edges, and a comparison against an unengineered rival says nothing. The second is judgement: comparing randomised algorithms on equal budgets, over
enough seeds, with a test that's allowed to say *no winner*. This lab builds 2-opt and Or-opt properly,
simulated annealing, ALNS for vehicle routing, and the statistics for time-to-target comparisons.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.problems.TSP`, `colib.colgen.CVRP` | Tour length, neighbour lists, nearest neighbour |
| scipy's Mann–Whitney (tests only) | The 2-opt move, 2-opt with and without don't-look bits |
| OR-Tools routing (`then` only) | Or-opt, and alternating local search |
| | Metropolis acceptance, geometric cooling, simulated annealing |
| | Random and worst removal, greedy insertion, adaptive weights, ALNS |
| | Time-to-target points, Mann–Whitney U, a verdict |

## Running it

```fish
uv run co test 26
uv run co test 26 --solution functional
```

## Style

Local search is an unfold: a state and a function returning the first improving move, or None. The
imperative reference reverses segments in place with a position array. The functional one rebuilds
tuples by slicing, O(n) per move instead of O(segment), which is fine at test sizes. Both consume random numbers in the same order, so annealing and ALNS give identical results
from the same seed.

---

## Step 1 — Tours and neighbour lists  *(15 min)*

*Shape: a sum; a sort per city; a greedy walk.*

**Done when** `step 1 ✓`: a hand-built tour length, nearest-neighbour tours from two starts with a tie,
and neighbour lists on 5 instances.

## Step 2 — 2-opt  *(45 min)*

*Shape: a move finder; a cyclic reversal; a sweep and a queue.*

**Done when** `step 2 ✓`. On 12 random tours, `two_opt_move` returns exactly the first improving
candidate (successor direction first), and reversing its stretch makes exactly that edge exchange,
with exactly that gain. On an optimised 200-city tour it looks up fewer than 40 distances per city,
so it stops scanning in time. The sweep reaches a full 2-opt optimum from 15 random starts, and a
neighbour-list optimum with k = 5. Don't-look bits stay within 10% of the sweep and do at most 70% of
its distance lookups.

## Step 3 — Or-opt  *(30 min)*

*Shape: rebuild the reduced tour per segment; try both orientations.*

**Done when** `step 3 ✓`. From 30 random starts Or-opt admits no improving segment move of length
1–3 in either orientation, and with k = 3 lists no improving candidate move. A hand-built line instance is
straightened. Local search reaches a tour that is both 2-opt and Or-opt optimal, including one
instance where a single round of each isn't enough.

## Step 4 — Simulated annealing  *(25 min)*

*Shape: two formulas and a loop.*

**Done when** `step 4 ✓`. Acceptance and cooling match their definitions. A scripted random stream
reproduces the exact move sequence, including a skipped whole-tour reversal. A run whose last move is
worsening still returns the best tour, not the last. Warm annealing cuts random 40-city tours by 40%,
and a frozen run never gets worse.

## Step 5 — ALNS for CVRP  *(45 min)*

*Shape: two destroy operators, one repair, a roulette, and a segment update.*

**Done when** `step 5 ✓`. Random removal uses the given random stream, and worst removal and greedy
insertion match hand-traced examples (ties, a forced new route). Greedy insertion picks the cheapest
feasible position on 10 instances. The weight update matches its formula. The roulette receives the
current weights (a recording random stream checks it), and ALNS returns feasible solutions that beat
greedy insertion.

## Step 6 — Time to target, and a verdict  *(20 min)*

*Shape: a sort; a rank sum; a decision.*

**Done when** `step 6 ✓`. TTT points keep failures in the denominator. Your Mann–Whitney U and p match
scipy on 12 samples with ties. The verdict declares a winner only when the test rejects, and takes the
direction from U, so it still works when both medians are the time cap.

---

## Then — equal budgets, time to target, and CVRP  *(15 min, runs about 12 minutes)*

```fish
uv run co then 26
```

Instances here use a 10 000 × 10 000 square. In `TSP.random`'s 100 × 100 square the typical edge between
near neighbours at n = 1000 is under 2 units, so rounding to integers fills the instance with ties.

**1. The engineering, n = 1000**, from the nearest-neighbour tour (278 829):

| | length | seconds |
|---|---:|---:|
| 2-opt sweep, full neighbour lists | 244 044 | 0.02 |
| 2-opt sweep, k = 10 | 246 410 | 0.02 |
| 2-opt, k = 10, don't-look bits | 245 287 | 0.01 |
| … then Or-opt (k = 10) | 239 655 | 3.2 |
| 2-opt, don't-look bits, from a *random* tour | 257 969 | 0.13 |

Building the full neighbour lists took 0.4 s, far more than 2-opt itself. The "stop scanning" rule
makes even full lists cheap. Or-opt, as written here (rebuilding the reduced tour per segment), is the
bottleneck: every candidate segment costs an O(n) list rebuild, and a version working on positions
would avoid it. That's the next thing to optimise.

**2. Equal budgets, n = 200**, 3 s each, % above the best tour any method found (10 instances):

| method | mean | worst | best on |
|---|---:|---:|---:|
| **ILS (double bridge + 2-opt + Or-opt)** | **0.06%** | **0.34%** | **8/10** |
| multi-start 2-opt + Or-opt | 0.48% | 1.51% | 2/10 |
| simulated annealing (+ polish) | 1.78% | 3.06% | 0/10 |
| OR-Tools routing, guided local search | 2.65% | 5.64% | 0/10 |

The annealing start temperature was tuned on a *separate* training instance (0.8 × mean edge, from
0.05, 0.2, 0.8, 3.2), never on the test instances. OR-Tools' routing solver is a general VRP engine
calling back into Python for every distance, so 3 s is a small budget for it. That's a statement about
this budget, not about the solver.

**3. Time to target**, n = 150, target 0.5% above the best of three 5 s ILS runs, 30 seeds, 4 s cap
(`out/ttt.png`):

| heuristic | reached | median | quartiles |
|---|---:|---:|---:|
| ILS, k = 10 | 28/30 | 0.86 s | 0.49–1.17 s |
| ILS, k = 6 | 25/30 | 0.66 s | 0.40–1.10 s |
| multi-start | 14/30 | 1.36 s | 0.58–1.77 s |
| annealing | 1/30 | — | — |

Mann–Whitney on run times with failures counted as the cap: ILS beats multi-start and annealing
(p ≤ 0.0003), and multi-start beats annealing (p = 0.0002). **ILS k = 10 vs k = 6: p = 0.76, no winner
declared.** k = 6 has the lower median and k = 10 reaches the target more often, and 30 seeds can't
separate them.

**4. CVRP, n = 60**, 5 instances, 10 s budget:

| seed | greedy insertion | your ALNS | ALNS seconds | OR-Tools GLS |
|---:|---:|---:|---:|---:|
| 0 | 2 039 | **1 059** | 6.9 | 1 067 |
| 1 | 2 368 | **1 160** | 8.6 | 1 170 |
| 2 | 2 262 | **1 237** | 9.2 | 1 261 |
| 3 | 2 326 | **1 182** | 7.6 | 1 230 |
| 4 | 2 546 | **1 266** | 9.2 | 1 304 |

ALNS used *less* than its budget (calibrated on its first 50 iterations), and still came out ahead on
all five. Before believing it, note three things. Five instances is a small sample. There's no lower bound,
so neither may be close to optimal. And OR-Tools pays for Python callbacks. Unit 28 is where claims like
this get the treatment they need.

## Checkpoint

- [ ] `uv run co test 26` shows all six steps ✓.
- [ ] You can produce a time-to-target plot comparing three of your heuristics over 30 seeds (`out/ttt.png`),
      and you correctly decline to declare a winner where the distributions overlap (ILS k = 10 vs k = 6).
- [ ] You can list what an honest comparison held fixed in section 2 (budget, instances, tuning set),
      and what it still didn't (implementation language, callback overhead).

## Reading

- Johnson & McGeoch, "The traveling salesman problem: a case study in local optimization", in *Local Search
  in Combinatorial Optimization* (1997): neighbour lists, don't-look bits, and how to report.
- Ropke & Pisinger, "An adaptive large neighborhood search heuristic for the pickup and delivery problem
  with time windows", *Transportation Science* 40 (2006).
- Lourenço, Martin & Stützle, "Iterated local search", in *Handbook of Metaheuristics* (2003).
- Aiex, Resende & Ribeiro, "TTT plots: a Perl program to create time-to-target plots", *Optimization
  Letters* 1 (2007).
- Sörensen, "Metaheuristics — the metaphor exposed", *ITOR* 22 (2015).
