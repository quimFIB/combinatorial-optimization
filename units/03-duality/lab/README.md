# Lab 03 — Duality

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 03`).
**You write:** 7 functions in `lab.py`, 80–110 lines in all.
**Needs:** unit 02. Steps 2–5 run on the tableaux `two_phase` returns. By default
that is the reference solution; `CO_MINE=02 uv run co test 03` uses yours.

Every later unit on the LP trunk reads a dual somewhere. This lab builds the four
things about duality that get used most:

- writing the dual down mechanically;
- reading it off a final tableau;
- using the pair (x, y) as a proof of optimality;
- the two things duals do in practice: warm-starting a re-solve, and predicting
  what a change in the data costs.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.lp.GeneralLP`: constraints ≤/≥/=, variables ≥0/≤0/free | The dual transformer |
| Unit 02's `two_phase`, `pivot` (via `colib.ref`) | Duals read off the tableau |
| `colib.solvers.highs_general` (tests only) | An exact optimality certificate check |
| | Adding a constraint to a solved tableau, and the dual simplex |
| | RHS ranging and objective prediction |

## Running it

```fish
uv run co test 03
uv run co test 03 --solution functional   # the no-mutation reference
```

## Style

Any style passes. `dual` is naturally two table lookups and a transpose
(`tuple(zip(*A))`). `certify_optimal` is a tuple of (condition, reason) pairs
where you return the first failing reason, which is
`next(((False, why) for ok, why in checks if not ok), (True, "optimal"))`. The
dual simplex is the same unfold as unit 02's loop, so reuse the pattern.

---

## Step 1 — The dual transformer  *(35 min)*

*Shape: lookup tables and a transpose.* The slides have the six sign rules for a
max primal; for a min primal every one of them flips.

**Done when** `step 1 ✓`: the textbook pair is exact, every rule is exercised
for both senses, `dual(dual(P)) == P` on 40 random general LPs, and HiGHS finds
equal optima for each pair, or unbounded primal with infeasible dual.

*Think about:* why must `dual(dual(P))` equal `P` *exactly*, and not just
"equivalently"? (Because the rules are an involution. If yours isn't, one of the
six is wrong.)

## Step 2 — Duals from the tableau  *(15 min)*

*Shape: a slice.* One line, once you see where the dual values sit.

**Done when** `step 2 ✓`: (*u*, *v*) = (1, 1) on the textbook LP. On 30 random LPs your *y* is
nonnegative, satisfies *Aᵀy ≥ c*, and has *bᵀy* equal to the primal optimum.

## Step 3 — Certify optimality  *(25 min)*

*Shape: a conjunction of predicates, each with a reason.* Primal feasibility,
dual feasibility, complementary slackness, all checked exactly.

**Done when** `step 3 ✓`: it accepts every simplex answer paired with its duals,
and it rejects six pairs, each failing a different condition.

*Think about:* "equal objective values" is an alternative to complementary
slackness. Why are they equivalent for a feasible pair? (Write out *bᵀy − cᵀx*
as a sum of products of slacks.)

## Step 4 — Warm start: add a cut, run the dual simplex  *(45 min)*

*Shape: one row reduction, then an unfold.* `add_constraint` writes the new row
in the current basis. Starting from there, `dual_simplex` restores primal
feasibility while keeping the objective row nonnegative.

**Done when** `step 4 ✓`: it agrees with a cold `two_phase` re-solve on 40 random
cuts, a redundant cut takes 0 pivots, and a cut that removes everything is
reported infeasible.

## Step 5 — Sensitivity  *(30 min)*

*Shape: a min/max over one column.* Increasing *b_i* by δ moves the basic
solution along the slack column *i* of the final tableau. The basis survives
while every basic value stays nonnegative.

**Done when** `step 5 ✓`: on 25 random LPs your prediction equals an exact re-solve
at both ends and the middle of every range, and `predict_objective` refuses
δ just outside it.

---

## Then — against HiGHS  *(10 min, runs ~2 s)*

```fish
uv run co then 03
```

1. **Sign conventions.** The same LP's shadow prices four ways. Yours and HiGHS
   with `sense=max` report **(1, 1)**. HiGHS on the same LP written as `min −c·x`,
   and SciPy's `ineqlin.marginals` (SciPy always minimizes), both report
   **(−1, −1)**. They are the same fact, since a dual is d(objective)/d(rhs) in
   the solver's own objective sense.
2. **Ranging.** Your ranges agree with HiGHS's ranging report on **103/103**
   binding constraints of 50 random LPs. For non-binding constraints HiGHS reports a different
   quantity, so the script skips them. By the argument on the slides, their range
   is [activity, +∞).
3. **Warm start.** Over 163 feasible re-solves after adding a cut, your dual
   simplex averages **0.98** pivots against **3.34** for a cold two-phase solve.
   HiGHS warm-started averages 0.96 iterations, cold 3.47. That factor of about 3.5
   on a 4×5 LP grows with size, and branch-and-bound re-solves one LP per node.

## Checkpoint

- [ ] `uv run co test 03` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** given a solved LP, you can read off the
      shadow price of each constraint and predict the objective change from a
      small right-hand-side perturbation before re-solving, and be right. Try it
      by hand on the textbook LP: tighten `2x + y ≤ 6` to `≤ 5` and predict the
      new optimum, then check with `two_phase`.
- [ ] You can state in one sentence why the dual simplex, not the primal, is the
      method used after adding a cut.

In `NOTES.md`: your warm/cold pivot averages, and the prediction you made by hand.

## Reading

- Bertsimas & Tsitsiklis, ch. 4 (§4.1–4.5): duality, complementary slackness,
  the dual simplex method; ch. 5 (§5.1–5.2): sensitivity analysis.
- Chvátal, ch. 5 and 10, for the economic reading of dual values.
- Optional: Gärtner & Matoušek §6.5–6.6, a short proof of strong duality from
  Farkas.
