# Lab 21 — Lazy clause generation, or what CP-SAT actually is

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 21`).
**You write:** the order encoding, two explaining propagators, a solver subclass and a job-shop
model, 170–230 lines in all.
**Needs:** unit 20 (your CDCL, subclassed here), unit 18 (timetable reasoning), unit 19 (the
job-shop baseline).

Unit 18's propagators remove values but forget why, so every branch rediscovers the same dead
ends. Unit 20's solver learns from every conflict, but it only sees clauses. Lazy clause generation
joins them. Integers are encoded as Booleans [x ≤ v]. Propagators run on the bounds and, for every
bound they tighten, hand the SAT solver a clause explaining it, so the solver can learn from
propagation as if the constraint had been written out in CNF. It never is: the clauses are
generated only when needed. The payoff in this lab: **ft06 proven optimal in 154 conflicts, where
unit 18's engine couldn't prove it in 100 000 nodes.**

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| Unit 20's `Solver` as `sat` (reference, or yours with `CO_MINE=20`) | The order encoding: literals and bounds |
| `Model`, `lit_true` | An explained, optionally reified precedence propagator |
| `colib.problems.JobShop`; unit 18's CP model (`then`) | An explained unary-resource timetable |
| CP-SAT (`then`) | `LCGSolver`: propagators inside CDCL's propagation loop |
| | The job-shop model and makespan minimisation |

## Running it

```fish
uv run co test 21
uv run co test 21 --solution functional
CO_MINE=20 uv run co test 21        # on your own CDCL
```

## Style

An explaining propagator is a pure function from the current bounds to a list of clauses, and the
functional reference writes both that way. The solver underneath is unit 20's CDCL, mutable by
design, so the functional reference inherits `LCGSolver` from the imperative one, the same exception
unit 20 made.

---

## Step 1 — The order encoding  *(20 min)*

*Shape: a block of variable numbers and a chain of implications.*

**Done when** `step 1 ✓`: literal numbers and chain clauses match the layout, a variable over 0..5 has
exactly 6 Boolean models, and `bounds` follows decisions correctly.

## Step 2 — Explained precedence  *(35 min)*

*Shape: two rules, each a clause.*

**Done when** `step 2 ✓`. On 40 random cases, half reified, every clause you return **holds for every
integer assignment satisfying the constraint**: the test decodes each literal back to integers and
checks. Bounds propagate both ways, a disabled precedence does nothing, and a violated one conflicts.

## Step 3 — Explained timetable  *(35 min)*

*Shape: for each compulsory part, each other task, at most one clause.*

**Done when** `step 3 ✓`: 40 random cases produce only valid clauses (checked against every
non-overlapping schedule). A compulsory part pushes a task later and pulls one earlier, but only when
bounds reasoning truly forces it. Two fixed overlapping tasks conflict.

*Think about:* the explanation mentions only i's bounds and one bound of j, not the current domains.
Why is that enough to make the clause valid forever? (Hint 3, rung 1.)

## Step 4 — The solver  *(35 min)*

*Shape: propagate, then run propagators, turn explanations into clauses, repeat.*

**Done when** `step 4 ✓`: random job-shops get valid schedules with explanations counted, learning
happens under a tight bound, and an impossible machine is proven infeasible through explained
conflicts.

## Step 5 — Minimisation  *(20 min)*

*Shape: solve, tighten a unit clause at level 0, keep everything learned.*

**Done when** `step 5 ✓`: optima match brute force on six 4×3 shops, **ft06 is proven at 55 within 5 000
conflicts**, the model has the right shape, and a conflict limit stops the search.

---

## Then — what learning buys, and CP-SAT by name  *(10 min, runs ~4 minutes)*

```fish
uv run co then 21
```

**Without and with learning** (horizon = half the total duration for the random shops):

| instance | CP (unit 18): best | proven | nodes | s | LCG: best | proven | conflicts | explanations | s |
|---|---:|---|---:|---:|---:|---|---:|---:|---:|
| ft06 | 55 | no | 100 000 | 12.7 | 55 | **yes** | **154** | 1 575 | 3.7 |
| random 6×4 | 47 | no | 100 000 | 15.5 | **44** | **yes** | 94 | 1 643 | 3.5 |
| random 8×4 | none | no | 100 000 | 17.6 | **58** | **yes** | 293 | 4 352 | 27.4 |
| random 8×5 | 53 | no | 100 000 | 48.1 | **52** | **yes** | 290 | 5 939 | 74.7 |

Propagation of the same kind and strength, plus clause learning, turns four unfinished proofs into four
optimality proofs in under 300 conflicts each. The CP engine can't even find a schedule for 8×4 within
the tight horizon. Each LCG conflict is expensive in Python (bounds are recomputed from Boolean
literals), but a proof is short.

**Ablation on ft06:** disjunctions plus the timetable take 154 conflicts (3.8 s); disjunctions only take
286 (5.2 s). Both are proven. Turning restarts off changes nothing here (154). The explained timetable
halves the search. Learning is what makes the search finite in practice.

**CP-SAT's log** on a 15×15 job-shop (5 s, 8 workers) has 352 lines. `then` prints its presolve summary; the
worker portfolio (6 full-problem CDCL/LP workers, 2 first-solution heuristics, 13 LNS workers); per-worker
search statistics with conflicts, restarts, Boolean and integer propagations; clause learning and
minimisation; clause deletion; the LP relaxation with cuts (CG, MIR and no-overlap-specific cuts); and
LNS improvement rates. **Every one of them maps to a unit of this course:** the LP and its cuts to
units 02–08, the search, learning, deletion and LNS to units 17–21, and presolve to unit 27, still ahead.

## Checkpoint

- [ ] `uv run co test 21` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** for a problem you haven't modelled before, you can say which of MIP /
      CP / SAT / CP-SAT you would reach for first, and defend it with something other than taste (the
      slides give a decision table and its reasons).
- [ ] In CP-SAT's log you can name, for every section `then` prints, the unit where you built it.

## Reading

- Ohrimenko, Stuckey & Codish, "Propagation via lazy clause generation", *Constraints* 14 (2009).
- Feydy & Stuckey, "Lazy clause generation reengineered", *CP* 2009.
- Schutt, Feydy, Stuckey & Wallace, "Solving RCPSP/max by lazy clause generation", *J. Scheduling* 16 (2013).
- Nieuwenhuis, Oliveras & Tinelli, "Solving SAT and SAT modulo theories: from an abstract DPLL procedure to
  DPLL(T)", *JACM* 53 (2006).
- Perron, Didier & Gay, "The CP-SAT-LP solver", *CP* 2023 (invited talk): CP-SAT's architecture in its
  authors' words.
