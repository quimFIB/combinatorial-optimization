# Hints — lab 21

One rung at a time; then `solution/lab.py` (everything) or `solution/functional.py` (the encoding,
propagators and model as pure functions; the solver subclass is inherited).

## Step 1 — The order encoding

<details><summary>Rung 1</summary>

`first = model.nvars + 1; model.nvars += ub - lb`, so `le(v) = first + (v - lb)`. The chain
clauses say "x ≤ v implies x ≤ v + 1". A value v then corresponds to exactly one assignment:
[x ≤ u] is false for u < v and true for u ≥ v.
</details>

<details><summary>Rung 2 — bounds</summary>

Scan v from lb upwards. A false [x ≤ v] means x ≥ v + 1 (keep raising lo). The first true [x ≤ v]
means x ≤ v (stop). Unassigned literals change neither bound.
</details>

<details><summary>Functional route</summary>

The model is a builder that hands out variable numbers and collects clauses, so creating an `IntVar` adds to
it. Reading bounds is the functional part: `hi` is the first `[x ≤ v]` literal that is true (`next(...,
default)`), and `lo` is one more than the last false one (`max(..., default=lb)`), both over one list of the
literal values.
</details>

## Step 2 — Precedence

<details><summary>Rung 1 — reading the explanation</summary>

"y ≥ xlo + d because x ≥ xlo" is the implication [x ≥ xlo] → [y ≥ xlo + d], which as a clause is
¬[x ≥ xlo] ∨ [y ≥ xlo + d]. With a guard b, add ¬b. If xlo is x's initial lower bound, the reason
is always true: drop it. If xlo + d exceeds y.ub, there's no head, and the clause (all false) is a
conflict.
</details>

<details><summary>Rung 2 — validity</summary>

The test decodes every literal back into integers and checks each of your clauses against every
(x, y, b) satisfying b → x + d ≤ y. So an explanation must be a consequence of the constraint
alone, not of the current search state. That's what lets CDCL keep it forever.
</details>

<details><summary>Functional route</summary>

A propagator is a pure function from the current bounds to a list of explanation clauses, and it touches no
solver state. Write each rule as a small function returning `(head literal, reason literals)`, where `None`
stands for "trivially true at the variable's bound". Select the rules whose condition fires, and build clauses
with a `_clause(*parts)` helper that drops the `None`s. Skip a clause whose head is already true.
</details>

## Step 3 — Unary

<details><summary>Rung 1 — why the explanation is valid</summary>

Suppose s_i ≤ lst and s_i ≥ ect − d_i. Then task i runs through the whole of [lst, ect). If also
s_j ≥ lst − d_j + 1, task j ends after lst, so j overlaps [lst, ect) unless it starts at ect or
later. Hence s_j ≥ ect. That's a valid clause whatever the current bounds are. The current bounds
only decide whether it fires now.
</details>

<details><summary>Rung 2 — building it</summary>

`part = [s_i.le(lst_i), s_i.ge(est_i)]`, dropping a literal when it's trivially true (lst_i = ub, or
est_i = lb). The clause is `[-l for l in part] + [-trigger] + [head]`, again dropping a trivial
trigger and an out-of-range head.
</details>

<details><summary>Functional route</summary>

Also pure: compute every task's bounds once, find the tasks with a compulsory part (lst < est + d), and
build clauses with a comprehension over (task with a part, other task) pairs. `explain(i, j)` returns zero or
one clause. Both the forward and backward cases use the same negated part of task i as their reason.
</details>

## Step 4 — The solver

<details><summary>Rung 1 — the propagate loop</summary>

```
while True:
    confl = super().propagate();  if confl is not None: return confl
    added = False
    for p in propagators:
        for clause in p.propagate(self):
            r = add_explanation(clause)
            if r == conflict: return the stored conflict index
            added |= (r == implied)
        if added: break          # let unit propagation catch up before more propagators run
    if not added: return None
```
</details>

<details><summary>Rung 2 — storing an explanation</summary>

Convert it with `sat.to_internal`. If the clause has an unassigned literal, put it first; sort the
rest by decreasing level, so c[1] is the highest-level false literal and the watches stay sensible
after backjumping. Append to clauses/learnt/lbd/deleted, watch c[0] and c[1] if it has two literals,
log it to the proof, then enqueue c[0] with this clause as reason. A conflict clause (all false) is
stored the same way, and its index is returned as the conflict. Unit 20's `analyze` then works
unchanged.
</details>

<details><summary>Rung 3 — degenerate explanations</summary>

A propagator can return the empty clause (a conflict needing no reason at all), and a unit explanation
can arrive above level 0. Store both. Enqueue a unit with its one-literal clause as reason, and make sure
unit 20's `locked` and `reduce_db` never index into an empty clause.
</details>

<details><summary>Functional route</summary>

The solver is unit 20's CDCL with an extra propagation phase, and it inherits that engine's mutable trail and
watches, for step 1's reasons in unit 20. The functional reference reuses the imperative `LCGSolver` and says
so. What stays functional is the interface: propagators hand back clauses, and the solver decides what to do
with them.
</details>

## Step 5 — Job-shop

<details><summary>Rung 1 — minimise</summary>

After a solution, `cancel_until(0)` and `add_clause([mk.le(best - 1)])`. Learned clauses stay valid:
every explanation followed from the constraints, and every learned clause from those. So the next
search starts with everything the last one learned. `add_clause` returning False means the new bound
is already refuted at level 0: best is optimal.
</details>

<details><summary>Functional route</summary>

The job-shop model is comprehensions, with `tz.groupby` giving the operations on each machine. Minimisation
is an unfold over `(best, trace, outcome)`: solve, and on a solution add `[makespan ≤ value − 1]` and go
again. Stop when the solver reports unsatisfiable (proved optimal), when the clause can't be added, or when the
conflict limit is hit. Adding the clause changes the live solver, the one effect in the loop.
</details>
