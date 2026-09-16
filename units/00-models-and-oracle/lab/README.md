# Lab 00 — Models, instances, and an oracle you trust

**Time:** about 2 hours. **Before:** the slides (`uv run co slides 00`).
**You write:** 8 functions in `lab.py`, 70–90 lines in all.

Self-study in this field usually goes wrong the same way: you have no way to tell
whether the clever thing you just wrote is correct. This lab builds the measuring
stick. Every later lab's tests lean on it.

## Given, and what you write

| Given in `colib` (not the lesson) | Yours in `lab.py` (the lesson) |
|---|---|
| The nine problems as dataclasses with random generators | Two of those models, re-derived: vertex cover and bin packing |
| Solution spaces: `Binary`, `Permutations`, `SetPartitions` | The set-partition enumerator |
| The differential harness, `differential(...)` | A generic brute-force oracle |
| DIMACS CNF and TSPLIB readers | A certificate checker for "nothing smaller exists" |
| | A heuristic that looks right, and the proof that it is not |

The library's reference oracle is `colib.brute_force`. Yours has to agree with it.
Don't read `colib/problems.py` or `colib/spaces.py` before step 3. Writing the
models blind is the exercise.

## Running it

```fish
uv run co test 00              # after every change; ends in a progress line
uv run co test 00 -k step2     # just one step
uv run co test 00 -x --tb=short
```

A stub you haven't touched shows as **·** (skipped: not started), not as a failure.
A red **✗** always means a real bug.

## Style

Write each step in whatever style fits it. The tests call your functions and
check what comes back, never how it was computed. Each step below names its
natural **shape**: some are predicates or folds, some are recursion, and a few
genuinely want mutable search state. There are two reference solutions, checked
by the same tests:

```fish
uv run co test 00 --solution              # solution/lab.py         loops and mutable state
uv run co test 00 --solution functional   # solution/functional.py  no mutation
```

For the vocabulary, `FUNCTIONAL.md` at the project root maps Haskell to
Python: `foldl` is `functools.reduce`, `scanl` is `itertools.accumulate`,
`groupBy`/`nub`/`.` are `toolz.groupby`/`toolz.unique`/`toolz.compose`, and so
on. `toolz` is already installed.

---

## Step 1 — Model it  *(15 min)*

*Shape: predicates and folds.* A universally quantified check over the edges; a
group-by-and-sum over the items.

Write the feasibility predicate and objective for vertex cover (over 0/1 vectors)
and bin packing (over restricted growth strings: `x[i]` is item *i*'s bin).

**Done when** `step 1 ✓`. The tests compare you against the reference model on every
candidate of several instances.

*Think about:* the objective is only ever called on feasible `x`. Would anything
change if it were called on infeasible ones? (Unit 11 turns on this question.)

## Step 2 — Enumerate set partitions  *(30 min)*

*Shape: recursion.* A string of length *i*+1 is a string of length *i* plus one
allowed label. A recursive generator with a shared mutable buffer is the
imperative version; building `prefix + (label,)` and chaining the results is the
functional one.

`set_partitions(n)` must yield each partition of `{0…n-1}` exactly once.
All maps from items to bins would be *n*ⁿ candidates. Restricted growth strings
give the Bell number B(*n*), because two packings that differ only by renaming
the bins are the same packing.

**Done when** `step 2 ✓`: counts equal B(*n*) for *n* ≤ 9, with no partition listed
twice.

*Think about:* at *n* = 10 how many candidates did this remove? (10¹⁰ vs 115 975.)
This is **symmetry breaking**, and units 05 and 27 come back to it as the biggest
lever on real models.

## Step 3 — The oracle  *(20 min)*

*Shape: one fold.* One pass over the space carrying (best value, best solution,
feasible, examined). A `for` loop with four variables, or `reduce` with a
`Result` as the accumulator.

`brute_force(problem)` for *any* colib problem: walk `problem.space()`, filter with
`is_feasible`, keep the best `objective` under `problem.sense`. Return a
`colib.Result`.

**Done when** `step 3 ✓`. It must agree with the reference on all nine problems,
report `None` on an infeasible instance, and maximise when the problem says `max`.

## Step 4 — A certificate of optimality  *(25 min)*

*Shape: predicates.* "Every pair is an edge" and "no endpoint repeats". The
functional version factors out an `is_matching` predicate and raises from it.

A cover of size *k* is easy to check. The claim that no cover of size *k*−1 exists
is a different kind of object. For vertex cover, a **matching** of size *k* is such
an object: the matched edges share no vertex, so any cover needs a separate vertex
for each of them.

Write `matching_lower_bound` (validate, return size) and `certify_vertex_cover`
(true exactly when cover and matching have the same size, which proves the cover
optimal).

**Done when** `step 4 ✓`. The last test runs your checker over every cover and
every edge set of a triangle and expects no certificate to be accepted. The
optimum there is 2, but the largest matching is 1.

*Think about:* write down, in one sentence, why the triangle breaks it. That
sentence is a preview of unit 03 (the duality gap) and unit 15 (König's theorem:
on bipartite graphs it never breaks).

## Step 5 — Break it on purpose  *(20 min)*

*Shape: iteration to a fixpoint.* Repeat until no edges remain: a `while` loop
that shrinks a set, or a recursive function on the remaining edges.

Write `plausible_vertex_cover`: a heuristic you would believe is optimal if you
hadn't tested it. It must always return a feasible cover. The test then runs the
harness and passes **only if the harness catches it**.

**Done when** `step 5 ✓`. Run `uv run co test 00 -k step5 -s` to see the smallest
counterexample it found. Draw that graph. Find the cover your heuristic chose and
the smaller one it missed.

---

## Then — find the wall  *(5 min, runs ~30 s)*

```fish
uv run co then 00
```

This times your oracle on 2ⁿ, (*n*−1)! and B(*n*) spaces and extrapolates the
largest *n* that fits in a minute, an hour and a year. In a minute, the
reference machine fits n = 11 for TSP and n = 12 for bin packing. The style
shows up in the vertex-cover number: the `reduce` oracle fits n = 24 there, the
loop n = 25, because building a new accumulator per candidate costs time. Your numbers are the size limit
for every "check against brute force" test in the rest of the course.

## Checkpoint

The unit is done when all three are true:

- [ ] `uv run co test 00` shows all five steps ✓.
- [ ] You can generate an instance of any of the nine problems and solve it by
      enumeration at the sizes `then` reported, without looking up how.
- [ ] You can explain, without notes, the difference between the certificate
      "here is a solution" and the certificate "nothing is better", and give the
      triangle as the case where the second kind can fail to exist for a given
      bound.

Write two or three lines in `NOTES.md` next to this file: your smallest
counterexample from step 5, and your three "wall" numbers.

## Reading

- Papadimitriou & Steiglitz, *Combinatorial Optimization*, ch. 1 (problems,
  instances, neighbourhoods). Short and still the clearest statement.
- Korte & Vygen, ch. 1 §1.1–1.3, if you want the formal version of
  "algorithm" and "running time" used from unit 13 on.
