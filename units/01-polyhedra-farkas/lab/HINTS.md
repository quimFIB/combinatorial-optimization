# Hints — lab 01

One rung at a time. If you get past the last rung, read `solution/lab.py`,
close it, and write it again yourself.

Each step also has a **Functional route** fold. This lab is fold-shaped, so it is
often the shorter answer. `solution/functional.py` is its reference, and
`FUNCTIONAL.md` at the project root maps Haskell names to Python and toolz.

## Step 1 — Eliminate one variable

<details><summary>Rung 1 — nudge</summary>

Take a row *p* with `a_p[k] > 0` and a row *q* with `a_q[k] < 0`. Multiply *p* by
`-a_q[k]` and *q* by `a_p[k]`. Both multipliers are positive, and the
*k*-coefficients cancel. With integer data you never need to divide.
</details>

<details><summary>Rung 2 — approach</summary>

Three lists: `zero`, `pos`, `neg`. Output `zero + [combine(p, q) for p in pos for
q in neg]`. Then tidy: `normalize` each row, skip rows whose `a` is all zeros
with `b >= 0`, skip rows you've already seen (a `set` of normalized rows works,
since rows are tuples).
</details>

<details><summary>Rung 3 — the case that trips people</summary>

If `pos` is empty (or `neg` is), no pairs are formed and only the `zero` rows
survive. That is correct: *x_k* is unbounded in one direction, so any *y* extends.
Don't special-case it.
</details>

<details><summary>Functional route</summary>

Three comprehensions for `zero`, `pos` and `neg`. A pure `combine(p, q, k)` that
returns the new row. Then one `tz.pipe`: start from
`chain(zero, (combine(p, q, k) for p, q in product(pos, neg)))`, and pass it
through curried `map(normalize)`, curried `filter(says_something)`, `tz.unique`
(which drops duplicates and keeps the order), and `list`.
</details>

## Step 2 — Decide feasibility

<details><summary>Rung 1</summary>

`n = len(system[0][0])`, loop `k` over `range(n)`, reassign `system =
eliminate(system, k)`. Afterwards every `a` is all zeros. Return
`all(b >= 0 for _, b in system)`.
</details>

<details><summary>Functional route</summary>

`reduce(eliminate, range(n), system)` is the whole elimination: `eliminate`
already has the `(acc, element)` signature `reduce` wants, with the system as the
accumulator and the variable index as the element.
</details>

## Step 3 — Enumerate vertices

<details><summary>Rung 1 — nudge</summary>

`itertools.combinations(system, n)` gives the *n*-subsets. `solve_exact` returns
`None` for a singular subset. Skip those, since they don't pin down a point.
</details>

<details><summary>Rung 2 — why a set works for deduplication</summary>

`solve_exact` returns exact `Fraction`s, so the same vertex reached from two
different bases is *equal*, not merely close. Put the tuples in a `set`, then
return `sorted(...)`. With floats this step would need a tolerance, and the
pyramid test is there to show why.
</details>

<details><summary>Functional route</summary>

`solutions = (solve_exact(...) for rows in combinations(system, n))`, then
`sorted({x for x in solutions if x is not None and satisfies(system, x)})`.
</details>

## Step 4 — Check a certificate

<details><summary>Rung 1</summary>

Check the length first, then nonnegativity. Compute `combo[j] = sum(y_i * a_i[j])`
for each column *j*, and require every entry to be `0` and `dot(y, b) < 0`. It
must be strict: *y* = 0 gives 0 ≤ 0, which proves nothing.
</details>

<details><summary>Functional route</summary>

One `return` with four conditions joined by `and`, in the order length,
nonnegativity, `yᵀA = 0`, `yᵀb < 0`, so the cheap checks run first.
</details>

## Step 5 — Find a certificate

<details><summary>Rung 1 — nudge</summary>

You need to know, for every row that FM produces, the multipliers on the
*original* rows. Is there a way to make those multipliers part of the row itself?
</details>

<details><summary>Rung 2 — the trick</summary>

Append *m* extra coordinates to every row: row *i* gets the unit vector *eᵢ*
appended to its `a`. Now eliminate only the first *n* coordinates, the real
variables. FM combines rows linearly, so the tail of every derived row is
exactly the combination of original rows that produced it. `normalize` scales
the head and the tail together, so the bookkeeping stays correct.

At the end, find a row whose first *n* coefficients are zero and whose `b < 0`.
Its tail is *y*.
</details>

<details><summary>Rung 3 — near-code</summary>

```python
m, n = len(system), len(system[0][0])
tagged = [(a + tuple(int(i == j) for j in range(m)), b)
          for i, (a, b) in enumerate(system)]
for k in range(n):
    tagged = eliminate(tagged, k)
for a, b in tagged:
    if not any(a[:n]) and b < 0:
        return tuple(a[n:])
return None
```
One consequence: with the tails attached, far fewer rows count as duplicates,
so the blow-up is worse. That is fine at test sizes, and it is a real cost of
asking for a proof as well as an answer.
</details>

<details><summary>Functional route</summary>

Build the tagged rows with a comprehension, fold `eliminate` over `range(n)`
exactly as in step 2, and return
`next((tuple(a[n:]) for a, b in final if not any(a[:n]) and b < 0), None)`.
</details>
