# Hints — lab 20

One rung at a time; then `solution/lab.py` (the solver) or `solution/functional.py`
(conflict analysis as a fold of resolutions, and the encoders).

## Step 1 — Assignment and propagation

<details><summary>Rung 1 — enqueue and lit_value</summary>

Literal i is true iff `value[i >> 1] == (not (i & 1))`. `enqueue(i, r)` sets the variable's
value, `level = len(trail_lim)`, `reason = r`, and appends i to the trail.
</details>

<details><summary>Rung 2 — the watch loop</summary>

For a newly true literal p, visit `watches[p ^ 1]` (clauses watching the literal that just became
false). For each clause c:

1. Make c[1] the false literal (swap with c[0] if needed).
2. If c[0] is true, keep watching and move on.
3. Look for j ≥ 2 with c[j] not false. If found, swap it into c[1], add the clause to
   `watches[c[1]]`, and **don't** keep it in this list.
4. Otherwise keep it. If c[0] is false, it's a conflict: copy the rest of the list back, set
   qhead to the end, and return. If c[0] is unassigned, enqueue it with this clause as reason.

Build a new list `keep` and assign it back at the end. Removing from a list while iterating
over it is the classic bug.
</details>

<details><summary>Rung 3 — add_clause at level 0</summary>

Normalise before storing: skip the clause if it contains i and i ^ 1, or a true literal; drop false
literals and duplicates. A unit is enqueued and propagated immediately, so a conflict there means
the whole formula is unsatisfiable.
</details>

<details><summary>Functional route</summary>

There isn't a good one, and the reference doesn't pretend. The trail, the value array and the watch lists
are mutable by design: two watched literals exist so that backtracking changes nothing but the trail pointer.
Rebuilding persistent structures on every assignment would give up exactly what this step teaches. The
functional reference inherits steps 1, 3 and 4 from the imperative solver and says so.
</details>

## Step 2 — Conflict analysis

<details><summary>Rung 1 — the MiniSat loop</summary>

```
seen = [False]*(n+1); learnt = [None]; counter = 0; p = None; index = len(trail) - 1
loop:
    for q in clause (skip c[0] when p is not None: it is p itself):
        v = q >> 1
        if not seen[v] and level[v] > 0:
            seen[v] = True; bump(v)
            if level[v] == current: counter += 1 else: learnt.append(q)
    while not seen[trail[index] >> 1]: index -= 1
    p = trail[index]; index -= 1; clause = clauses[reason[p >> 1]]; seen[p >> 1] = False; counter -= 1
    if counter == 0: break
learnt[0] = p ^ 1
```
</details>

<details><summary>Rung 2 — why this is resolution</summary>

Each iteration resolves the current clause with the reason of the latest current-level literal, on
that literal's variable. `counter` is the number of current-level literals still in the resolvent.
When it reaches 1, the remaining one is the first UIP. The functional reference writes exactly this
as `iterate(resolve, conflict_clause)`.
</details>

<details><summary>Rung 3 — the backjump level</summary>

Move the literal of the highest level among `learnt[1:]` to position 1. The backjump level is its
level (0 for a unit). After backjumping, every literal but `learnt[0]` is still false, so the clause
is unit and `learnt[0]` can be enqueued with it as reason. That's the asserting property the test
checks.
</details>

<details><summary>Rung 4 — the textbook test</summary>

Draw the implication graph: x2 → x4 (via −2 −3 4) and x2, x4 → x5 (via −2 −4 5); x4 and x5 are in
conflict. Every path from the decision x2 to the conflict passes through x2, but not every path
passes through x4 (x2 → x5 directly). So the first UIP is x2, and the learned clause is ¬x2 ∨ ¬x3.
</details>

<details><summary>Functional route</summary>

Conflict analysis is where a functional reading teaches something: first-UIP learning is a sequence of
resolutions. Start from the conflict clause as a frozenset (level-0 literals dropped), and resolve it with the
reason of its most recently assigned current-level literal. `tz.iterate(resolve, start)` gives the chain, and
`takewhile(more than one current-level literal)` cuts it at the UIP. Bumping, sorting the rest by level and
the backjump level then read off the final set.
</details>

## Step 3 — The loop

<details><summary>Rung 1 — branching</summary>

A linear scan over the variables is fine at the lab's sizes. MiniSat uses a binary heap ordered by
activity. The phase comes from `cancel_until`, which stores each unassigned variable's last value.
</details>

<details><summary>Rung 2 — restarts and reduction counters</summary>

Keep `conflicts_here` (since the last restart) and `limit = restart_base * luby(restarts + 1)`. Keep
`reduce_at`, starting at reduce_base: when `stats["learned"] >= reduce_at`, call reduce_db and add
reduce_base.
</details>

<details><summary>Functional route</summary>

Branching is the one functional piece: a `max` over `(activity, −v)` for the unassigned variables, with the
saved phase choosing the sign. The loop itself (propagate, analyse, backjump, restart on the Luby schedule,
reduce the database) drives mutable solver state and stays imperative, as in step 1.
</details>

## Step 4 — Proofs and deletion

<details><summary>Rung 1 — what goes in the proof</summary>

Every learned clause, written the moment it's learned (before it's used), in DIMACS literals ending
in 0. Every deleted clause, as `d ... 0`. The empty clause `0` when you return False. The checker
replays it: each lemma must follow from the clauses so far by unit propagation.
</details>

<details><summary>Rung 2 — locked clauses</summary>

A clause is locked when it's the reason of a current assignment: `reason[c[0] >> 1] == ci` and c[0] is
true. Deleting it would leave a dangling reason, and the next conflict analysis would crash or learn
nonsense.
</details>

<details><summary>Functional route</summary>

Also imperative by inheritance. A DRAT proof is an append-only log of additions and deletions, which is
already a persistent structure. Clause deletion has to respect locked clauses (reasons on the trail), which
is a filter over the learnt clauses.
</details>

## Step 5 — Encodings

<details><summary>Rung 1 — sequential counter (at most one)</summary>

s_i means "one of x_0..x_i is true":
x_0 → s_0; for 0 < i < n−1: x_i → s_i, s_{i−1} → s_i, ¬(x_i ∧ s_{i−1}); finally ¬(x_{n−1} ∧ s_{n−2}).
</details>

<details><summary>Rung 2 — bitwise</summary>

With b = ceil(log₂ n) bits: for each i and bit j, x_i → (bit j) if bit j of i is 1, else ¬(bit j).
Two literals true at once would force two different bit patterns.
</details>

<details><summary>Rung 3 — at most k</summary>

r[i][j] means "at least j+1 of x_0..x_i are true". Base: x_0 → r[0][0]; ¬r[0][j] for j ≥ 1. Step i:
x_i → r[i][0]; r[i−1][j] → r[i][j]; x_i ∧ r[i−1][j−1] → r[i][j]; overflow ¬(x_i ∧ r[i−1][k−1]).
Last: ¬(x_{n−1} ∧ r[n−2][k−1]).
</details>

<details><summary>Functional route</summary>

Every encoder is a comprehension that returns a clause list. `Fresh` hands out new variable numbers, the one
counter the encodings need. The sequential counter's middle clauses and at-most-k's register clauses are nested
comprehensions over positions i and counts j. Models concatenate the exactly-one parts per row, column or
vertex.
</details>
