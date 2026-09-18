# Lab 12 — Benders decomposition

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 12`).
**You write:** 6 functions in `lab.py`, 130–180 lines in all.
**Needs:** unit 03 (LP duality), unit 10 (column generation, which this unit mirrors).

Some MIPs are a small hard decision followed by a large easy one. You open facilities,
and then, for each of many demand scenarios, you route goods. Fix the hard variables
and the rest splits into independent LPs. Their duals tell you, as a linear inequality
in the hard variables, how much each choice will cost. Benders adds those inequalities
to a small master problem until its bound meets the best solution found. It is row
generation, the formal dual of unit 10's column generation, and two-stage stochastic
programming is its natural home.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.colgen.StochasticFacility`, including a sparse extensive-form solve | The recourse LP and its duals |
| `highs_lp`, `MILP`, `highs_mip` | Optimality and feasibility cuts |
| scipy, used independently in the tests | The master and the Benders loop (multi- and single-cut) |
| | Magnanti–Wong Pareto-optimal cuts |
| | LP-first warm start (McDaniel & Devine) |

## Running it

```fish
uv run co test 12
uv run co test 12 --solution functional
```

## Style

The loop is an unfold over an immutable record: cut sets, incumbent, phase and history.
Each step maps scenarios to recourse results and derives cuts from them. The functional
reference is written that way. A master that is re-solved from scratch each iteration
suits that style; production codes keep the model and add cuts, which is where mutation
pays.

---

## Step 1 — The recourse LP  *(25 min)*

*Shape: build the C demand and F capacity constraints, call `highs_lp`, and read the signs
of the duals.*

**Done when** `step 1 ✓`: your values match scipy's on every scenario of 20 instances, and
your duals are nonnegative, dual feasible and satisfy strong duality. A fractional y works,
and an infeasible scenario returns `(INF, None, None)`.

## Step 2 — Cuts  *(25 min)*

*Shape: two one-liners, and one phase-one LP.*

**Done when** `step 2 ✓`: every optimality cut is tight where it was generated and valid at
every other y (checked over all 2^F). Every feasibility cut cuts off its y and keeps every
feasible y.

*Think about:* why is an optimality cut valid at a y it was never computed at? (The dual
feasible region doesn't depend on y. Only the objective does.)

## Step 3 — The loop  *(40 min)*

*Shape: master, scenarios, cuts, bounds, stop.*

**Done when** `step 3 ✓`. Multi- and single-cut both reach the brute-force optimum, with
unequal scenario probabilities too, and the reported y costs what you report. Lower bounds
never decrease, and every lower bound stays below the optimum. Feasibility cuts work when
all demand must be met. An 8×20×15 instance matches the extensive form, and multi-cut takes
fewer iterations than single-cut.

## Step 4 — Pareto-optimal cuts  *(25 min)*

*Shape: one more LP, over the dual variables directly.*

**Done when** `step 4 ✓`: your cut is tight at y, valid everywhere, and exactly the strongest
at the core point (checked against scipy). On a hand-built degenerate instance it finds the
cut worth 15 at the core, where a plain dual gives 10.

## Step 5 — LP first  *(15 min)*

*Shape: a phase flag in the loop.*

**Done when** `step 5 ✓`: still optimal, and over three loose instances it needs fewer integer
masters than plain Benders.

---

## Then — the crossover  *(10 min, runs ~6 minutes)*

```fish
uv run co then 12
```

10 facilities, 30 customers, S scenarios. The extensive form has 330 S variables. Seconds,
with Benders iterations in brackets:

**Tight capacities** (1.6× mean demand):

| S | DE (HiGHS) | multi-cut | single-cut | LP-first |
|---:|---:|---:|---:|---:|
| 5 | 0.55 | **0.17** (7) | 0.29 (8) | 0.25 (2) |
| 25 | 2.36 | 1.12 (10) | 1.67 (17) | **1.10** (2) |
| 100 | 6.33 | 8.46 (14) | **3.18** (14) | 6.78 (5) |
| 200 | 12.40 | **1.92** (5) | 2.51 (7) | 4.75 (2) |
| 400 | 31.38 | 16.20 (9) | **10.77** (14) | 40.44 (6) |

**Loose capacities** (3× mean demand):

| S | DE (HiGHS) | multi-cut | single-cut | LP-first |
|---:|---:|---:|---:|---:|
| 5 | **0.40** | 2.42 (29) | 3.30 (35) | 2.96 (20) |
| 25 | **2.31** | 4.61 (21) | 3.68 (30) | 5.21 (13) |
| 50 | **3.18** | 45.87 (48) | 11.22 (57) | 42.15 (33) |
| 100 | 8.47 | 20.15 (24) | **6.13** (27) | 30.19 (15) |

There is no single crossover. With tight capacities, Benders wins from the smallest instance,
because a few cuts pin down which facilities must open. With loose capacities, many facility
sets are nearly equivalent, Benders needs 20–60 iterations, and the extensive form wins until
single-cut overtakes it between 50 and 100 scenarios. Multi-cut never needs more iterations,
but its master carries S times as many cuts and gets slow to re-solve. LP-first cuts the
integer iterations by a third or more but spends that saving on LP iterations in this implementation. Pareto
cuts (S = 25, loose) gave the same 21 iterations and took longer: the duals of this capacitated
recourse are rarely degenerate. Magnanti–Wong pays off on uncapacitated problems.

Iteration times are dominated by rebuilding and re-solving the master from scratch. That's
why the numbers are noisy (S = 100 multi-cut, tight). A solver callback that adds cuts inside
one branch-and-bound tree removes that cost, and it's the modern form of the method (slides).

## Checkpoint

- [ ] `uv run co test 12` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** you can draw Dantzig–Wolfe and Benders on one page as duals
      of each other (rows vs columns, master vs subproblem) and point at where unit 03 sits
      in both.
- [ ] You can explain why the extensive form wins on the loose instances, in terms of the
      number of iterations and what each costs.

## Reading

- Benders, "Partitioning procedures for solving mixed-variables programming problems",
  *Numerische Mathematik* 4 (1962).
- Rahmaniani, Crainic, Gendreau & Rei, "The Benders decomposition algorithm: a literature
  review", *EJOR* 259 (2017).
- Magnanti & Wong, "Accelerating Benders decomposition", *Operations Research* 29 (1981).
- Birge & Louveaux, *Introduction to Stochastic Programming* (2nd ed., 2011), ch. 5: the L-shaped
  method.
- Fischetti, Ljubić & Sinnl, "Redesigning Benders decomposition for large-scale facility
  location", *Management Science* 63 (2017). Benders inside branch-and-cut, done right.
