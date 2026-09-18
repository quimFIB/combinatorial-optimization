# Capstone — One problem, four traditions

**Time:** 12–15 hours over several sessions. **Before:** the slides (`uv run co slides capstone`), and
`uv run co data` once to download Solomon's instances.
**You write:** 22 functions in `lab.py`, about 530 lines in all: a checker, four solvers and a referee.
**Needs:** unit 07 (branch and bound), 08 (cuts), 10 (column generation), 17–21 (CP), 26 (ALNS), 28 (method).

The curriculum's brief: pick one problem, solve it four ways, run all four through your unit-28 harness on
a shared instance set under a shared time budget, and write the report that says which wins where. The
deliverable isn't a winner. It's a defensible account of which instance characteristics favour which
method, with the evidence attached, and with the cases where the answer is "they are indistinguishable"
reported as such.

The problem is **vehicle routing with time windows** (VRPTW) on Solomon's 56 instances. The objective is
total distance with an unlimited fleet, and distances are truncated to tenths: the conventions of the exact
literature (the slide "Two objectives, and why the numbers are in tenths"). The four methods:

| | tradition | what you build | solver underneath |
|---|---|---|---|
| (a) | polyhedral | an arc MIP whose capacity lives in your rounded capacity cuts | SCIP |
| (b) | decomposition | branch-and-price with a labelling pricer | HiGHS for the master LPs |
| (c) | constraint programming | a circuit model, a hint and a search strategy | CP-SAT |
| (d) | local search | ALNS with constant-time feasible insertion | none |

Two deviations from the curriculum's brief, both deliberate. **SCIP replaces a commercial solver**, as
everywhere in the course. The brief's **"cover and subtour cuts"** become rounded capacity inequalities,
which contain subtour elimination as the case ⌈q(S)/Q⌉ = 1, while VRPTW has no knapsack constraints for classical
covers to act on.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.vrptw`: the instance type, Solomon's files, a brute-force oracle | Schedules, latest starts, a violation checker, routes from arcs |
| `colib.vrptw.lazy_cut_handler`: SCIP's constraint-handler plumbing | Rounded capacity separation and the SCIP model |
| HiGHS (`highspy`, `colib.mip.highs_mip`) | ESPPRC labelling, column generation, the restricted master IP, arc branching |
| OR-Tools CP-SAT | The circuit model, a hint, a nearest-arc strategy |
| Unit 26's `update_weights`, unit 28's store and statistics (`colib.ref`) | Feasible insertion, Shaw removal, regret repair, ALNS |
| `then.py`: the parallel, resumable benchmark and its report | The adapter that trusts nothing, primal gaps, contradictions, head-to-head verdicts |

## Running it

```fish
uv run co data                                  # once: Solomon's instances into data/solomon
uv run co test capstone
uv run co test capstone --solution functional
uv run co then capstone                         # the full benchmark: see below before starting it
```

The tests never need Solomon's files. Every exact method is checked against brute force on random
instances of 7 to 10 customers, and the whole suite takes under ten seconds against the reference.

## Style

The checker and the referee are pure: scans, set algebra and groupings. The three model builders are
imperative at the edges because SCIP's, CP-SAT's and HiGHS's APIs add to a live model. The functional
reference keeps that mutation local and says so. Branch-and-price is an unfold over (open nodes, columns,
incumbent), and the pricer a fixpoint over immutable label buckets. Repair and removal are folds.

---

## Step 1 — Schedules and a certificate  *(1 h)*

*Shape: a forward scan; a backward scan; set algebra; a walk.*

**Done when** `step 1 ✓`. `schedule` agrees with enumeration of every route of up to four customers on six
instances and with a hand-computed timetable (including a wait). `latest_starts` is exactly tight: starting
one unit later breaks the route. `violations` names every kind of error on hand-built bad solutions and
accepts brute force's optima. `routes_from_arcs` rejects subtours and a vertex left twice.

## Step 2 — (a) Branch-and-cut on SCIP  *(2 h)*

*Shape: components of a support graph; a model of four families of constraints; a callback.*

**Done when** `step 2 ✓`. Separation finds the hand-built fractional and integer violations, and never cuts
off any of 180 random feasible solutions. `solve_mip` proves brute force's optimum on eight instances, with
`cuts=True` and with `cuts=False`, including four instances where capacity is the binding constraint.
In the second case your cuts are the only thing enforcing capacity.

## Step 3 — (b) Branch-and-price  *(4 h)*

*Shape: a label-setting loop with dominance; a column-generation loop; a best-first tree.*

**Done when** `step 3 ✓`. On eight instances with random duals, `price` finds exactly the most negative
route that enumeration finds, and with forbidden arcs it returns only genuine routes, in order.
Column generation reaches the full set-partitioning LP's value over all routes (to 1e−6), and
reports an infeasible node. The restricted master IP finds the optimum when given the optimal routes,
and nothing when they can't cover. Branch-and-price proves the optimum on eight instances, branches
correctly on instances whose root LP is fractional, and claims nothing it can't prove when time runs out.

## Step 4 — (c) CP-SAT  *(1.5 h)*

*Shape: one global constraint and two families of enforced inequalities; a hint; a strategy.*

**Done when** `step 4 ✓`. The model's optimum equals brute force's on four instances, and its arc literals
decode to routes of that cost. A hinted solution, fixed, has exactly its own cost. The strategy branches on
arcs in distance order. `solve_cpsat` proves the optimum under four configurations, and reports a time-out
honestly.

## Step 5 — (d) ALNS  *(2.5 h)*

*Shape: an O(1) test; a sort-and-pick loop; a regret fold; an annealing loop.*

**Done when** `step 5 ✓`. `insertion_delta` agrees with a full reschedule at every position of 40 routes on
each of six instances. Shaw removal replays a scripted rng exactly. Regret repair is feasible, prefers an
existing route on a tie and opens a route when none has room. ALNS is valid, reproducible from its seed,
stops at its time limit, and reaches the optimum on at least six of ten small instances in 300 iterations.

## Step 6 — The referee  *(1 h)*

*Shape: a wrapper; three small functions; paired tests with a correction.*

**Done when** `step 6 ✓`. The adapter rejects a lying cost, a late route and a missing customer. Primal gaps
match Berthold's definition. References and contradictions come out right on a hand-built run table.
`head_to_head` finds the planted winner, and declares "indistinguishable" for a planted tie.

---

## Then — the benchmark  *(runs about 1.5 hours; then the report is yours)*

```fish
uv run co then capstone                 # ~1.5 h on 8 cores; resumable, results in out/capstone.sqlite
uv run co then capstone --report        # the report again, without running anything
```

672 runs: 4 methods × 56 instances × 25, 50 and 100 customers, 60 s each, one thread each, six at a
time on eight cores. The reference run's full report is `out/then.txt`. **Integrity first**: no invalid
solution, no crash, no kill, no "optimal" refuted by another method's better solution, and no instance
where two methods proved different optima.

**1. Proven optimal, of 56** (and the mean primal gap at 60 s against the best value any method found):

| n | (a) SCIP B&C | (b) B&P | (c) CP-SAT | (d) ALNS | proven by some method |
|---:|---:|---:|---:|---:|---:|
| 25 | 33 (1.6%) | **49** (9.2%) | 36 (0.08%) | – (0.43%) | 51 |
| 50 | 16 (11.2%) | 16 (53.9%) | 14 (6.2%) | – (**0.20%**) | 21 |
| 100 | 11 (28.9%) | 0 (96.5%) | 6 (18.9%) | – (**0.15%**) | 11 |

Branch-and-price's large gaps are runs with **no solution at all** (gap 1): 3 at n = 25, 26 at 50, 49 at 100.
When it finishes, it proves. When exact pricing stalls, its only incumbent (the root's restricted master IP)
never gets computed. Ten of its runs overran the limit by more than the 5 s grace, because one exact
pricing call can't be interrupted, and were recorded as timeouts.

**2. Who wins which instances**: the smallest gap, then the fastest proof.

| series | window / horizon | n = 25 | n = 50 | n = 100 |
|---|---:|---|---|---|
| C1 | 0.25 | B&C 8, B&P 1 | B&C 6, ALNS 2, B&P 1 | ALNS 5, B&C 4 |
| C2 | 0.27 | B&C 4, CP-SAT 4 | B&C 5, ALNS 2, CP-SAT 1 | B&C 6, ALNS 2 |
| R1 | 0.38 | **B&P 11**, B&C 1 | B&P 5, ALNS 5, B&C 1, CP-SAT 1 | ALNS 11, B&C 1 |
| R2 | 0.45 | B&P 5, CP-SAT 4, B&C 1, ALNS 1 | **ALNS 9**, B&C 1, CP-SAT 1 | ALNS 10, CP-SAT 1 |
| RC1 | 0.36 | B&P 5, B&C 2, CP-SAT 1 | ALNS 7, CP-SAT 1 | ALNS 8 |
| RC2 | 0.38 | B&P 4, CP-SAT 3, B&C 1 | ALNS 6, B&C 1, CP-SAT 1 | ALNS 8 |

**3. The paired tests** (Wilcoxon over the 56 instances, Holm over all pairs in a block):

| n | solution quality (primal gap), 6 pairs | time to proof (PAR1), 3 exact pairs |
|---:|---|---|
| 25 | CP-SAT and ALNS beat B&C (Holm p ≤ 0.01). **B&P–B&C, B&P–CP-SAT, B&P–ALNS and CP-SAT–ALNS: indistinguishable** | **B&P fastest**: beats B&C (p = 0.02) and CP-SAT (p = 0.014); B&C–CP-SAT indistinguishable |
| 50 | ALNS beats all three; CP-SAT beats B&C and B&P; B&C beats B&P (all Holm p ≤ 6·10⁻⁶) | B&C beats CP-SAT (p = 0.01); **B&C–B&P and B&P–CP-SAT indistinguishable** |
| 100 | the same order: ALNS, CP-SAT, B&C, B&P (all Holm p ≤ 3·10⁻⁶) | B&C beats both (p = 0.012); CP-SAT beats B&P (p = 0.036) |

**4. ALNS against proven optima**, which is the fairer measure of it. The "best found" reference is often
ALNS's own value, so its near-zero gaps above are partly by construction. It reached the proven optimum on
47 of 51 instances at n = 25 (misses up to 4.3%, on RC207), 20 of 21 at n = 50, and 9 of 11 at n = 100. It
was 7.7% above on C205.100, where SCIP proved the optimum, and 1.1% above on R101.100. As a sanity check at
n = 100, the best distance found is a median 0.996 of SINTEF's best-known distance (range 0.84–1.06). The
objectives differ, so that's a check of scale, not a score.

**The account the numbers support**, as a reference for your own `NOTES.md`:

- **Tight windows, random customers (R1, RC1), 25 customers: branch-and-price.** It proves all 20, and is
  fastest on 16. That fits the usual explanation: short routes keep labelling cheap, and the
  set-partitioning LP is tight. This run didn't measure either directly.
- **Clustered customers (C1, C2): the compact MIP makes most of the proofs.** It wins 12 of 17 at n = 25
  (C2 splits 4–4 with CP-SAT) and 11 of 17 at n = 50. All 11 proofs at n = 100 are clustered or R1, and SCIP
  made each of them.
- **Wide windows (R2, RC2): no exact method is reliable past 25 customers.** Labelling has long routes and
  little dominance, and big-M time constraints are weak. At n = 25 B&P still proves 15 of 19, and ends two (RC204,
  RC208) with no usable solution.
- **Beyond 25 customers, for solution quality: ALNS**, on every series, with every paired test decisive. CP-SAT
  with one worker is a clear second, and the compact MIP third.
- **Indistinguishable at n = 25 on solution quality**: CP-SAT against ALNS, and B&P against each of the others.
  That's four of six pairs.

**What this run can't tell you.** One seed per run: SCIP's and CP-SAT's run times vary a lot with the seed
(unit 27). Six jobs shared eight cores. C104.25 took branch-and-price 39.5 s in a lighter prototype run,
and here it found no solution in 60 s. So near-limit results can flip. Pure Python (labelling, ALNS)
competed against C++ (SCIP, CP-SAT) in one budget, which makes B&P's result an implementation finding as
much as an algorithmic one. The extra experiments that would address these are five seeds per run, one job
at a time, and CP-SAT with eight workers.

## Checkpoint

- [ ] `uv run co test capstone` shows all six steps ✓.
- [ ] `uv run co then capstone` reports no invalid solution and no refuted optimality claim.
- [ ] **`NOTES.md` holds the report the brief asks for:** for each series and size, which method wins on
      solution quality and which on proof time, with the paired test behind each claim. Say where the
      answer is "indistinguishable". Tie each finding to an instance characteristic (clustering, window
      width, route length) rather than to an instance name.
- [ ] The report states its limitations: one seed per run, one machine, pure Python against C++ solvers,
      and what extra experiment would remove each.

## Reading

- Solomon, "Algorithms for the vehicle routing and scheduling problems with time window constraints",
  *Operations Research* 35 (1987).
- Kallehauge, Larsen, Madsen & Solomon, "Vehicle routing problem with time windows", in *Column Generation*
  (Springer, 2005).
- Feillet, Dejax, Gendreau & Gueguen, "An exact algorithm for the elementary shortest path problem with
  resource constraints", *Networks* 44 (2004).
- Baldacci, Mingozzi & Roberti, "New route relaxation and pricing strategies for the vehicle routing
  problem", *Operations Research* 59 (2011).
- Savelsbergh, "The vehicle routing problem with time windows: minimizing route duration", *ORSA Journal
  on Computing* 4 (1992).
- Ropke & Pisinger, "An adaptive large neighborhood search heuristic for the pickup and delivery problem
  with time windows", *Transportation Science* 40 (2006).
- Berthold, "Measuring the impact of primal heuristics", *Operations Research Letters* 41 (2013).
