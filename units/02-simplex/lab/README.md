# Lab 02 — Simplex, honestly

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 02`).
**You write:** 7 functions in `lab.py`, 90–130 lines in all.
**Needs:** unit 01 (vertices are bases; this lab walks between them).

Lab 01 listed every basis to find the vertices. This lab walks from one basis
to a better neighbour instead, and shows three honest facts about doing so:

- a textbook pivoting rule can loop forever on a degenerate LP;
- a well-designed LP can make it take exponentially many pivots;
- floating point can give a wrong point that still looks optimal.

## Given, and what you write

| Given in `colib.lp` | Yours in `lab.py` |
|---|---|
| `LPResult`, `Cycling` | The tableau, and a pivot on it |
| `random_lp`, `beale()`, `fractions(...)` | Dantzig's and Bland's pricing, and the ratio test |
| `colib.solvers.highs_lp` (used by tests and `then` only) | The simplex loop, with cycle detection |
| | The two-phase method for any right-hand side |
| | The Klee–Minty cube |

## Running it

```fish
uv run co test 02
uv run co test 02 -k step4 --tb=short
```

## Style

Any style passes. The imperative reference updates a list-of-lists tableau in
place. The functional one never mutates: `pivot` returns a new tuple of tuples,
and the pivoting loop is `iterate(step, state)` read until the first finished
state. Pivoting loops run for thousands of iterations here, so **don't write the
loop as recursion** (see the recursion note in `FUNCTIONAL.md`). The iterator
version is the functional way.

```fish
uv run co test 02 --solution              # solution/lab.py
uv run co test 02 --solution functional   # solution/functional.py
```

---

## Step 1 — Tableau and pivot  *(25 min)*

*Shape: row operations.* Building the tableau is two comprehensions. A pivot
scales one row and subtracts multiples of it from all the others.

**Done when** `step 1 ✓`: the tableau layout is exact, a pivot produces a unit
column, and pivoting preserves the solution set of the equality rows.

## Step 2 — Pricing and the ratio test  *(25 min)*

*Shape: argmin with a tie-break.* Both functions filter candidates, then take a
minimum. The rules differ only in how they break ties, and that difference is
the whole of Bland's theorem.

**Done when** `step 2 ✓`. The tests are small hand tableaux with deliberate ties.

*Think about:* the ratio test uses only rows with a **positive** entry in the
entering column. What would pivoting on a negative entry do to feasibility?

## Step 3 — The simplex loop  *(30 min)*

*Shape: an unfold.* Price, then ratio test, then pivot, until pricing finds
nothing or the ratio test finds no row.

**Done when** `step 3 ✓`. It must agree with HiGHS on 25 random LPs under both
rules, cycle on Beale's example under Dantzig's rule (raise `Cycling`), and
finish it under Bland's rule with optimum 5/4.

*Think about:* why is "the basis repeated" a correct test for cycling? (The
objective never decreases, and it only stays level on degenerate pivots. So a
repeated basis means a closed loop of zero-progress pivots.)

## Step 4 — Two phases  *(60 min)*

*Shape: the same loop, run twice on two objectives.* This is the fiddliest step,
and the time estimate reflects that. The bookkeeping is: which constraints get
artificials, pricing out the phase-1 objective, driving zero-level artificials
out of the basis, and restoring the real objective consistently with the basis.

**Done when** `step 4 ✓`: agreement with HiGHS on 60 random LPs of every outcome,
an LP with a redundant equality row, and a detected infeasible LP.

## Step 5 — Klee–Minty  *(15 min)*

*Shape: a comprehension.* Write the generator. The test then checks that your
Dantzig simplex takes exactly 2ⁿ − 1 pivots for *n* = 1…7.

**Done when** `step 5 ✓`.

---

## Then — against HiGHS  *(10 min, runs ~6 s)*

```fish
uv run co then 02
```

1. **Agreement.** The reference run agreed with HiGHS on **1000/1000** random LPs
   (498 optimal, 236 infeasible, 266 unbounded). Exact Fractions took 0.35 ms per
   LP against HiGHS's 0.21 ms, so at this size speed is not the gap. You'll also
   meet a solver quirk: HiGHS's presolve labels some unbounded LPs "infeasible",
   and `colib` re-solves without presolve to get the truth.
2. **Klee–Minty.** Dantzig's rule takes exactly 2ⁿ − 1 pivots (4095 at *n* = 12).
   Bland's rule grows more slowly: 3, 5, 9, 15, 25, 41, 67, …, where each term is
   the previous two plus one. That is still exponential. HiGHS's primal simplex
   takes **1** iteration up to *n* = 6 and **9** after that.
3. **Numerics.** On *Hx = H1*, with *H* the Hilbert matrix, the only solution is
   *x* = 1. Exact arithmetic always finds it. From *n* = 7 (HiGHS) and *n* = 8
   (floats in your code) the returned point is wrong by more than 1, yet the
   objective still reads ≈ *n*. The condition number of *H* is 5 × 10⁸ at *n* = 7
   and 1.5 × 10¹⁰ at *n* = 8.

## Checkpoint

- [ ] `uv run co test 02` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** your simplex agrees with HiGHS on 1000
      random LPs (`then`, part 1), and you can exhibit an instance where it
      cycles without Bland's rule (Beale).
- [ ] You can say in one sentence what steepest-edge pricing buys over Dantzig's
      rule. (Dantzig's rule ranks columns by improvement per unit of one
      variable, so rescaling a variable changes its choice; steepest edge ranks
      them by improvement per unit of distance moved along the edge, which is
      much less sensitive to scaling and typically needs far fewer pivots, at
      the cost of keeping edge norms up to date.)

In `NOTES.md`: your part-1 agreement count, your Bland pivot counts, and the *n*
at which your float version first returns a wrong *x*.

## Reading

- Bertsimas & Tsitsiklis, ch. 3 (§3.1–3.7): the simplex method, anticycling,
  phase I, and the revised simplex.
- Chvátal, *Linear Programming*, ch. 3–4 and 8, for Beale's example and
  Klee–Minty in exactly the form used here.
- Optional: Koberstein's thesis *The dual simplex method, techniques for a fast
  and stable implementation* (2005), ch. 1–3, for what HiGHS actually does.
