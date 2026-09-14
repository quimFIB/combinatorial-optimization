# Hints — lab 00

Open one rung at a time. Each rung gives away more than the one before it. If
you get to the last rung and are still stuck, read `solution/lab.py` and write it
again from memory. That is not a failure; it is how the time budget holds.

The numbered rungs lean towards loops. Each step also has a **Functional
route** fold for writing it without mutation. `solution/functional.py` is its
reference, and `FUNCTIONAL.md` at the project root maps Haskell names to Python
and toolz.

## Step 1 — Model it

<details><summary>Rung 1 — nudge</summary>

Vertex cover is one `all(...)` over the edges. For bin packing, the only thing
you need is each bin's total load.
</details>

<details><summary>Rung 2 — approach</summary>

Bin packing: a dict from bin label to running total, filled in one pass over
`enumerate(x)`. The number of bins used is the number of distinct labels in `x`.
</details>

<details><summary>Functional route</summary>

Feasibility is `all(...)` over the edges. If you want it as an explicit left
fold, `functools.reduce(lambda ok, edge: ok and ..., inst.edges, True)` is
`foldl`. It gives the same answer but does not stop at the first uncovered edge;
`all` does.

For bin packing the loads are a fold grouped by bin, which is
`tz.reduceby(key, binop, seq, init)` over the `(bin, size)` pairs `zip(x, inst.sizes)`.
Without toolz: `{b: sum(s for s, l in zip(inst.sizes, x) if l == b) for b in set(x)}`.
</details>

## Step 2 — Enumerate set partitions

<details><summary>Rung 1 — nudge</summary>

Build the string left to right. At position *i* the only choices are "join a
block that already exists" or "open exactly one new block".
</details>

<details><summary>Rung 2 — approach</summary>

Recursive generator `extend(i, top)`, where `top` is the largest label used so
far. For each `v` in `range(top + 2)`, set `a[i] = v` and recurse with
`max(top, v)`. Fix `a[0] = 0` and start at `i = 1`. Handle `n == 0` on its own.
</details>

<details><summary>Rung 3 — near-code</summary>

```python
a = [0] * n
def extend(i, top):
    if i == n:
        yield tuple(a); return
    for v in range(top + 2):
        a[i] = v
        yield from extend(i + 1, max(top, v))
yield from extend(1, 0)
```
Yield `tuple(a)`, not `a`. The list is mutated after it is yielded, so yielding
`a` itself hands out the same object every time.
</details>

<details><summary>Functional route</summary>

Recurse on an immutable prefix: `extend(prefix, top)` returns the strings that
start with `prefix`. When `len(prefix) == n` that is `(prefix,)`; otherwise it is
`chain.from_iterable(extend(prefix + (b,), max(top, b)) for b in range(top + 2))`.
Start from `extend((0,), 0)`, and handle `n == 0` on its own. Everything stays
lazy, and no tuple is ever mutated, so the `tuple(a)` trap from rung 3 cannot
happen.
</details>

## Step 3 — The oracle

<details><summary>Rung 1 — nudge</summary>

The easy thing to get wrong is the first feasible candidate. "Best so far" has
no value until one exists. Use `None`, not `0` or `inf`: either of those is wrong
for one of the two senses.
</details>

<details><summary>Rung 2 — approach</summary>

Count `examined` for every candidate and `feasible` only for those that pass.
Replace the incumbent on *strict* improvement only, so the first optimum found is
the one kept (the tests check `solution` is optimal, not which one it is).
</details>

<details><summary>Functional route</summary>

The accumulator is the answer: fold with `Result(None, None, 0, 0)` as the
initial value, and have the step function return a new `Result`.
`dataclasses.replace(acc, examined=acc.examined + 1)` updates one field of the
frozen dataclass without mutating it. Pick the comparison once, outside the fold:
`better = (lambda v, b: v < b) if problem.sense == "min" else (lambda v, b: v > b)`.
</details>

## Step 4 — Certificates

<details><summary>Rung 1 — nudge</summary>

Edges are unordered: `(2, 1)` is the edge `(1, 2)`. `frozenset((u, v))` makes
that automatic.
</details>

<details><summary>Rung 2 — approach</summary>

`matching_lower_bound`: set of `frozenset` edges; walk the matching, keeping a set
of used vertices, and raise on a non-edge or a reused vertex.
`certify_vertex_cover`: catch the `ValueError` and return `False`; otherwise check
`inst.is_feasible(cover)` and `sum(cover) == size`.
</details>

<details><summary>Functional route</summary>

Write a pure `is_matching(inst, matching) -> bool`: every pair's `frozenset` is
among the graph's edge frozensets, and the flattened endpoints have no
repeats (`len(set(ends)) == len(ends)`). Then `matching_lower_bound` raises when
it is false, and `certify_vertex_cover` is a single `and` of three conditions,
with no `try`.
</details>

## Step 5 — Break it

<details><summary>Rung 1 — nudge</summary>

"Take the vertex that covers the most still-uncovered edges, repeat" is the one
most people believe.
</details>

<details><summary>Rung 2 — why it fails</summary>

A high-degree vertex whose neighbours can all be covered by a few other
vertices, which each also cover other edges. Taking the hub first commits you to
paying for the spokes too. The harness will find a concrete case; you don't need
to construct one.
</details>

<details><summary>If the test says "DID NOT RAISE"</summary>

Your heuristic was optimal on every instance tried (sizes 1–12, 40 seeds each).
Either you wrote an exact algorithm, or you break ties in a lucky way. Try taking
the *last* maximum-degree vertex instead of the first, or switch to the
"pick an uncovered edge, take both endpoints" rule. That one is feasible and at
most 2× optimal, and so it is not optimal.
</details>

<details><summary>Functional route</summary>

`go(remaining, chosen)`: if `remaining` is empty, return `chosen`. Otherwise
count degrees with `tz.frequencies(tz.concat(remaining))`, take `best`
by `max(range(inst.n), key=...)`, and recurse on the edges not touching it. The
recursion depth is at most *n*.
</details>
