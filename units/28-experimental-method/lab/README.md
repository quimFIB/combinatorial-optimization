# Lab 28 — Experimental method

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 28`).
**You write:** 14 functions in `lab.py`, 150–200 lines in all.
**Needs:** unit 26 (time-to-target, Mann–Whitney), unit 27 (performance variability).

Every earlier unit ended with a "then" step that compared things and printed a table. Most of those
tables came from one run per configuration, on a handful of instances, summarised by totals or means.
This lab builds the tools that make such comparisons trustworthy: a store of individual runs that can
be resumed and re-analysed, shifted geometric means, performance profiles, the virtual best solver,
bootstrap intervals for paired ratios, and corrected paired tests. Then `then` uses them to audit two
earlier conclusions. One of them doesn't survive, and that's the unit working.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `sqlite3` (standard library), `FIELDS` | A run store: open, save, load |
| `_problems` helper (grouping runs by instance and seed) | A resumable benchmark runner with recorded timeouts |
| scipy's Wilcoxon (tests only) | Shifted geometric means, penalised times, per-solver tables |
| Units 07, 17, 19 reference solutions (`then`) | Performance profiles, the virtual best solver |
| | Percentile bootstrap, a paired geometric-ratio interval |
| | Holm–Bonferroni, the Wilcoxon signed-rank test |

## Running it

```fish
uv run co test 28
uv run co test 28 --solution functional
```

## Style

The store is SQLite, which is state by design. The functional reference still writes rows, but builds
each row and query as a value first. Everything after step 2 is pure: groupings with `toolz`,
statistics as comprehensions, Holm's step-down as an `accumulate`.

---

## Step 1 — The run store  *(20 min)*

*Shape: one table, one primary key, three functions.*

**Done when** `step 1 ✓`. Runs survive closing and reopening the file, a second save with the same key
replaces the first, experiments are kept apart, and loads come back ordered by solver, instance, seed.

## Step 2 — A resumable runner  *(25 min)*

*Shape: a triple loop that skips what's already stored.*

**Done when** `step 2 ✓`. With a fake clock, runs happen in instance → solver → seed order, measured
seconds are recorded, an overrun (by any amount) becomes a timeout at exactly the limit, other statuses
are kept, and re-running with an extra seed performs only the new runs.

## Step 3 — Shifted geometric means  *(15 min)*

*Shape: a formula; a penalty; a group-by.*

**Done when** `step 3 ✓`. Hand values match. On 10 random samples the SGM lies between the minimum and
the arithmetic mean, and tends to the mean as the shift grows. PAR-1 and PAR-10 penalties change the
table as they should.

## Step 4 — Performance profiles and the virtual best  *(30 min)*

*Shape: a ratio table per problem; cumulative fractions.*

**Done when** `step 4 ✓`. A hand-built three-solver example with seeds, ties, a failure and an
unsolved problem gives exactly the right profile. Profiles are non-decreasing, reach the fraction solved
for large τ, and share the wins at τ = 1. The virtual best breaks ties by name and reports nobody for an
unsolved problem.

## Step 5 — Bootstrap intervals  *(25 min)*

*Shape: resample, compute, sort, index.*

**Done when** `step 5 ✓`. The interval uses exactly the specified resamples and indices, replayed from the
same random stream. Its width for a normal mean is within 20% of 2 × 1.96 σ/√n, and constant data gives
a degenerate interval. The paired geometric ratio matches its formula, with the default shift of 10.

## Step 6 — Many comparisons  *(25 min)*

*Shape: a step-down adjustment; a rank test.*

**Done when** `step 6 ✓`. Holm matches a hand example, and your Wilcoxon T and p match scipy on 10 samples
with ties and zeros.

---

## Then — two audits  *(15 min, runs about 6 minutes; seconds on a re-run)*

```fish
uv run co then 28
```

Runs go to `lab/out/bench.sqlite`, so a second invocation re-analyses without re-solving.

### Audit 1 — unit 07's branching rules

Unit 07's claim came from **totals over three instances**: strong branching uses the fewest nodes
(1 271 against 1 581 for pseudocost), and pseudocost is fastest. Re-run on 24 knapsacks (18, 20, 22 items):

| rule | solved | SGM nodes | SGM seconds | fewest nodes on | fastest on |
|---|---:|---:|---:|---:|---:|
| most-fractional | 24/24 | 800 | 0.58 | 0 | 2 |
| pseudocost | 24/24 | 708 | **0.53** | 1 | **22** |
| strong | 24/24 | **543** | 1.34 | **23** | 0 |

Paired, with 95% bootstrap intervals and Holm-adjusted Wilcoxon p-values:

| ratio | nodes | seconds |
|---|---|---|
| strong / pseudocost | 0.77 [0.72, 0.82], p ≤ 0.0001 | 2.31 [2.15, 2.47], p ≤ 0.0001 |
| pseudocost / most-fractional | 0.89 [0.84, 0.93], p = 0.0001 | 0.91 [0.88, 0.95], p = 0.0001 |

**The conclusion survives, and is now quantified**: strong branching saves about 23% of nodes and costs
2.3× the time. Pseudocost is 9% faster than most-fractional, and 92% of instances (22/24) have it as the
fastest rule (`out/profile.png`).

### Audit 2 — unit 19's restarts

Unit 19's claims came from **one instance and 100 seeds**, capped at 3 000 nodes: restarts cut the mean
node count from 153.6 to 52.1, and make the **median worse** (31 → 49.5).

| strategy | capped runs | mean | 95% interval | median | 95% interval |
|---|---:|---:|---|---:|---|
| first-fail | 3 | 153.6 | [66.6, 267.5] | 31.0 | [28.5, 35.0] |
| Luby restarts | 0 | 52.1 | [45.0, 59.7] | 49.5 | [28.5, 53.5] |

- **The mean** of first-fail is an artefact of the cap. Three runs at 3 000 contribute 90 of the 153.6.
  Without them the mean is 65.6, and with a higher cap it would be higher still. The interval
  [66.6, 267.5] says the same thing. "Restarts cut the mean" is true but not a stable number.
- **"Restarts make the median worse" does not survive.** The intervals overlap, since both contain 28.5–35.
  On eight more instances of the same family, restarts raised the median on 3 and lowered or matched it
  on 5 (Wilcoxon p = 0.79).
- **"Restarts help the tail" does survive**: they lower the mean on 7 of the 8 new instances
  (p = 0.03), and on the two instances where first-fail hit the cap 6 times out of 30, restarts never did.

| instance | first-fail mean | Luby mean | first-fail median | Luby median | capped (ff / Luby) |
|---|---:|---:|---:|---:|---|
| #4 | 1 066.6 | 194.0 | 443.5 | 140.0 | 6 / 0 |
| #5 | 1 140.9 | 190.8 | 851.0 | 83.0 | 6 / 0 |
| #2 | 60.9 | 71.9 | 33.5 | 53.5 | 0 / 0 |
| #8 | 199.1 | 170.9 | 143.5 | 156.0 | 0 / 0 |

So unit 19's README has been corrected in place: the median claim is withdrawn, and the mean claim is
restated as a claim about the tail.

## Checkpoint

- [ ] `uv run co test 28` shows all six steps ✓.
- [ ] **Every performance claim in your notes regenerates from one command, and each one survives the
      regeneration, or has been corrected in place.** Start with the two audits above, then pick one
      claim of your own from units 20–27.
- [ ] You can say, for a given comparison, which of SGM, performance profile, TTT plot or paired interval
      answers the question actually being asked.

## Reading

- Dolan & Moré, "Benchmarking optimization software with performance profiles", *Math. Programming* 91
  (2002).
- Achterberg, *Constraint Integer Programming*, PhD thesis (2007), ch. 1: shifted geometric means as SCIP
  reports them.
- McGeoch, *A Guide to Experimental Algorithmics* (2012).
- Hooker, "Testing heuristics: we have it all wrong", *J. Heuristics* 1 (1995).
- Beiranvand, Hare & Lucet, "Best practices for comparing optimization algorithms", *Optimization and
  Engineering* 18 (2017).
