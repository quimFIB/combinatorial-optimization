# Lab 05 — Formulations and the integrality gap

**Time:** about 2 hours. **Before:** the slides (`uv run co slides 05`).
**You write:** 5 functions in `lab.py`, 60–90 lines in all.
**Needs:** unit 03. Units 07, 08 and 27 come back to these same models, so keep them.

The first integer programming unit writes models, not algorithms. One facility
location problem, written three ways that all have the same integer solutions,
turns out to be very different to solve. You'll measure how different, and
where modern solvers hide the difference.

## Given, and what you write

| Given in `colib.mip` | Yours in `lab.py` |
|---|---|
| `MILP` (a min problem as plain tuples), `facility_names` | Aggregated big-M UFL, for any M |
| `FacilityLocation.random(F, C, seed)` | Disaggregated UFL |
| `lp_relaxation`, `highs_mip`, `scip_mip` (tests, `then`) | The optimum by enumeration |
| | Capacitated FL, weak and strong |
| | Gap closed |

## Running it

```fish
uv run co test 05
uv run co test 05 --solution functional
```

## Style

A model is data, so any style that produces the right tuples passes. The
functional reference writes each constraint family as a generator of
`(row, rhs)` pairs, and a model as the concatenation of its families. Adding a
family is then one list element. That is how modelling layers such as PuLP and
gurobipy feel.

---

## Step 1 — Aggregated big-M  *(25 min)*

*Shape: a list of rows.* One linking constraint per facility, its row with −M in
the *yᵢ* column.

**Done when** `step 1 ✓`. On 6 instances the MILP optimum matches brute force,
with HiGHS and SCIP required to agree. Fixing the open set gives the right cost,
and the LP bound with M = 10C is below the bound with M = C.

## Step 2 — Disaggregated  *(15 min)*

*Shape: the same, with one constraint per pair.*

**Done when** `step 2 ✓`: correct on the same instances, and its LP bound is at
least the aggregated one's.

*Think about:* the disaggregated model has F·C linking constraints instead of F, so it
is a much bigger LP. Why is it still the faster model to solve? (`then` part 2.)

## Step 3 — Brute force  *(15 min)*

*Shape: min over subsets.* This is a lab-00-style oracle that exploits the
structure: *y* determines *x*.

**Done when** `step 3 ✓`.

## Step 4 — Capacitated  *(35 min)*

*Shape: more families.* The capacity constraint is required. The strong version
adds the disaggregated linking constraints and one aggregate cover constraint,
and neither removes any integer solution.

**Done when** `step 4 ✓`: both variants have the same integer optimum, the
solution respects capacity, and the strong LP bound is at least the weak one.

*Think about:* with capacities, *xᵢⱼ ≤ yᵢ* is *implied* by the capacity constraint
for integer *y*. So why add it? (Slide "When a constraint is implied, and still
helps".)

## Step 5 — Gap closed  *(5 min)*

A one-liner, used by `then` to report how much of the gap each strengthening closes.

---

## Then — two solvers, three settings  *(10 min, runs ~20 s)*

```fish
uv run co then 05
```

Reference run, 20 facilities and 60 customers:

| formulation | LP gap | SCIP nodes, presolve and cuts **off** | HiGHS / SCIP nodes, default |
|---|---:|---:|---:|
| UFL aggregated, M = 10C | 46.1 % | **5 644** (5.9 s) | 7 / 1 |
| UFL aggregated, M = C | 41.3 % | 4 293 (4.2 s) | 7 / 1 |
| UFL disaggregated | 0.0 % | **1** | 1 / 1 |
| CFL capacity constraints only | 5.5 % | 102 | 11 / 27 |
| CFL + linking + cover | 1.2 % | 20 | 1 / 4 |

The ordering by LP bound predicts the ordering by nodes exactly when the solver
can't repair the model. With defaults, presolve and cutting planes rebuild most of
the missing strength, and a weak model can look fine. Unit 08 explains how.

A warning that belongs in this unit. On one 4-facility, 7-customer aggregated
instance, **HiGHS 1.14.0 returned 881 as optimal; the true optimum is 831.** Brute
force and SCIP both say 831, and so does HiGHS with presolve off. The project pins
HiGHS 1.13.1, which gets all 60 test instances right, and the tests now require
two solvers to agree. Brute force on small instances is how this was caught.

## Checkpoint

- [ ] `uv run co test 05` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** shown two formulations of one problem, you
      can predict which solves faster from their relaxation bounds alone, and be
      right more often than not. Test yourself on part 2's table before reading it.
- [ ] You can explain why a larger M gives a weaker relaxation, with a
      one-variable picture.

In `NOTES.md`: your part 2 node counts, and your prediction before you ran it.

## Reading

- Wolsey, *Integer Programming* (2nd ed.), ch. 1 and §2.1–2.2: formulations,
  relaxations, and "the ideal formulation".
- Conforti, Cornuéjols & Zambelli, §2.1–2.4 and §4.1–4.3 on extended formulations.
- Optional: Vielma, "Mixed integer linear programming formulation techniques",
  *SIAM Review* 57 (2015), §1–3. The best modern survey of big-M versus the
  alternatives.
