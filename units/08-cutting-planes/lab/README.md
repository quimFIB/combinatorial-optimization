# Lab 08 — Cutting planes and branch-and-cut

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 08`).
**You write:** 7 functions in `lab.py`, 90–130 lines in all.
**Needs:** unit 07; unit 02's tableau (reference by default); unit 05's idea of
formulation strength.

Two kinds of cut, each at the scale where it is worth building by hand:

- **Gomory fractional cuts**, the general-purpose cut that proves any pure integer
  program can be solved by cutting alone. You'll watch it succeed, then stall.
- **Lifted knapsack cover cuts**, the problem-specific kind that does the real work
  in solvers. You'll separate them exactly and lift them, then run a root cutting
  loop with a cut pool, and measure the gap closed next to SCIP's.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| Unit 02's exact `two_phase` (tableau, basis) | A Gomory cut, in the original variables |
| `colib.mip.lp_relaxation`, `colib.bb.multi_knapsack` | The pure Gomory loop |
| `scip_mip` (tests and `then`) | Exact cover separation by DP |
| | Sequential lifting |
| | Pool aging, and the root loop |

## Running it

```fish
uv run co test 08
uv run co test 08 --solution functional
```

## Style

Separation is a DP: the functional reference folds over items with a
dict of "cheapest partial cover per capped weight" as the accumulator. Watch out:
two partial covers can reach the same weight, and a dict comprehension keeps
the *last*, not the cheapest. The functional reference had exactly that bug until
the tests caught it. Lifting is a fold over the variables outside the cover. Both
loops are unfolds.

---

## Step 1 — A Gomory cut  *(40 min)*

*Shape: fractional parts, then a substitution.* The cut is cleanest in the tableau's
space (x and slacks). The work is rewriting it in x only, by substituting
*s = b − Ax*, then clearing denominators.

**Done when** `step 1 ✓`. On 12 random IPs, every cut from every fractional tableau
row is integer, is violated by the LP vertex, and removes no feasible integer point
(checked by enumeration). The textbook example gets a cut that forces *x₂ ≤ 1*.

## Step 2 — The pure Gomory loop  *(20 min)*

*Shape: an unfold.* Cut, re-solve, repeat.

**Done when** `step 2 ✓`: the bounds never increase, never pass the integer
optimum, and the loop reaches the optimum on at least 12 of 15 instances within
60 rounds.

## Step 3 — Cover separation  *(35 min)*

*Shape: a 0/1 knapsack DP.* Minimize Σ(1 − xⱼ) over sets with weight above the
capacity. The DP table is indexed by accumulated weight, capped at capacity + 1.

**Done when** `step 3 ✓`: on 25 random knapsack constraints, when you return None
no violated cover exists (checked over all subsets), and when you return a cover it really is one
and is violated. The small example must return the *most* violated cover.

## Step 4 — Lifting  *(35 min)*

*Shape: a fold over the variables outside the cover.* Each coefficient is "how
much room is left" when that variable is set to 1.

**Done when** `step 4 ✓`: on 20 random knapsack constraints the lifted inequality
is valid for every feasible 0/1 point, and **maximal**: raising any lifted coefficient by 1
makes it invalid.

## Step 5 — The root loop  *(30 min)*

*Shape: solve, age, separate, add, repeat.*

**Done when** `step 5 ✓`: pool aging is exact on a handcrafted pool, the bound starts
at the LP value and never decreases, it never passes the integer optimum, and it
closes more than 5% of the gap on average.

---

## Then — yours against SCIP's  *(10 min, runs ~50 s)*

```fish
uv run co then 08
```

1. **Gomory.** It reached the integer optimum on 19 of 20 small IPs. Seed 7 needed
   36 cuts. Seed 16 **stalled**: after 80 cuts the bound is 24.5 against an
   optimum of 23, and the cut coefficients have grown to **13 digits**. This is why
   solvers run only a few rounds of Gomory-style cuts.
2. **Covers at the root** on 20-item knapsacks with 2 constraints. Your cuts close
   8–27% of the gap. SCIP's root cuts close 45–78% on the instances where it reports a root bound.
3. **SCIP nodes with cuts off / on** (presolve off): 45 / 34, 26 / 2, 386 / 322,
   88 / 66, 1 / 1, 209 / 184.

## Checkpoint

- [ ] `uv run co test 08` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** from a fractional simplex tableau you can
      write down a valid Gomory cut by hand, and prove it separates the current
      vertex while excluding no integer point. Do the textbook example
      (`max x₂, 3x₁ + 2x₂ ≤ 6, −3x₁ + 2x₂ ≤ 0`) on paper.
- [ ] You can explain why your cover cuts close less of the gap than SCIP's, naming
      at least two cut families SCIP runs that you didn't.

In `NOTES.md`: the Gomory cut you derived by hand, and your part 2 table.

## Reading

- Wolsey, ch. 8 (valid inequalities, Chvátal–Gomory, lifting) and ch. 9 (strong
  valid inequalities: covers, flow covers).
- Conforti, Cornuéjols & Zambelli, ch. 5–7.
- Optional: Cornuéjols, "Valid inequalities for mixed integer linear programs",
  *Mathematical Programming B* 112 (2008). The survey to read after this unit.
