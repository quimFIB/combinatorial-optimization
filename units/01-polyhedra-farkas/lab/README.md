# Lab 01 — Polyhedra, Fourier–Motzkin, and Farkas

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 01`).
**You write:** 5 functions in `lab.py`, 60–80 lines in all.
**Needs:** lab 00 (you'll use the habit, not the code).

This lab never uses a solver. It shows three facts about polyhedra with code
you wrote yourself:

1. Projecting a polyhedron gives a polyhedron. Fourier–Motzkin elimination
   computes that projection, and the number of constraints explodes.
2. A bounded polyhedron is the convex hull of finitely many vertices, and a
   vertex is where *n* independent constraints are tight.
3. When a system has no solution, there is a short proof of that fact. The
   proof falls out of step 1 for free.

## Given, and what you write

| Given in `colib.polyhedra` | Yours in `lab.py` |
|---|---|
| Constraints as rows `(a, b)` = *a·x ≤ b*, exact integers | Fourier–Motzkin elimination of one variable |
| `normalize`, `satisfies`, `dot` | Feasibility by eliminating everything |
| `solve_exact`: square systems in `Fraction`s | Vertex enumeration by basis enumeration |
| `random_polytope`, `random_infeasible`, `box` | A Farkas certificate checker |
| | A Farkas certificate *finder*, with no LP solver |

## Running it

```fish
uv run co test 01
uv run co test 01 -k step3 --tb=short
```

## Style

Any style passes, as in lab 00. This lab is the most fold-shaped in the course
so far, so the functional reference solution is the shorter of the two:

```fish
uv run co test 01 --solution              # solution/lab.py
uv run co test 01 --solution functional   # solution/functional.py
```

---

## Step 1 — Eliminate one variable  *(40 min)*

*Shape: partition, cartesian product, map, filter.* Three comprehensions split
the constraints; `itertools.product(pos, neg)` pairs them; `dict.fromkeys` deduplicates
while keeping order.

Split the constraints by the sign of `a[k]`, into the slides' *Z*, *U* and *L*.
Constraints with `a[k] = 0` (*Z*) pass through. Every constraint with a positive
coefficient (*U*, an upper bound on `x_k`) pairs with every constraint with a
negative coefficient (*L*, a lower bound). Scale both by positive numbers so the
`x_k` terms cancel, and add them.

**Done when** `step 1 ✓`. The main test samples integer points and checks that
your projected system accepts a point exactly when there is a real `x_k`
extending it. The test computes that interval directly.

*Think about:* why must the multipliers be positive? What goes wrong if you
subtract two constraints the way Gaussian elimination does? (Inequalities only survive
nonnegative combinations. This one fact is the whole of Farkas' lemma.)

## Step 2 — Decide feasibility  *(10 min)*

*Shape: a fold.* `reduce(eliminate, range(n), system)`, then one `all`.

Eliminate *x₀, …, x₍ₙ₋₁₎* in turn. Every remaining constraint reads *0 ≤ c*. The
system is feasible exactly when every such *c* is nonnegative.

**Done when** `step 2 ✓`. Agrees with HiGHS on feasible and infeasible systems.

*Think about:* this is a complete decision procedure for linear feasibility,
written in 10 lines. Why isn't it how anyone solves LPs? (`then` answers it with
a number.)

## Step 3 — Enumerate vertices  *(30 min)*

*Shape: generate, filter, collect.* A set comprehension over
`combinations(system, n)`.

For every *n*-subset of constraints, solve them as equalities with `solve_exact`. Keep
the solutions that satisfy the whole system, and deduplicate.

**Done when** `step 3 ✓`. That means the eight corners of a cube, a square
pyramid whose apex is tight on four constraints but listed once, and agreement
with qhull on random polytopes. Every vertex you return is also checked to have
tight constraints of rank *n*.

*Think about:* this is lab 00's brute force wearing different clothes. Checking
all C(*m*, *n*) bases is to vertices what enumerating 2ⁿ is to vertex cover.
Simplex (unit 02) is the idea of walking between neighbouring bases instead of
listing all of them.

## Step 4 — Check a certificate  *(15 min)*

*Shape: a conjunction of predicates.*

*y* ≥ 0, *yᵀA* = 0, *yᵀb* < 0. Three conditions, and all of them are needed. The
tests try certificates that fail each one.

**Done when** `step 4 ✓`.

## Step 5 — Find a certificate  *(40 min)*

*Shape: the step-2 fold on augmented constraints, then a search.* `next(...)` with a
default of `None` is the functional "first match or nothing".

Every constraint `eliminate` produces is a nonnegative combination of the
original constraints. If you eliminate everything and a constraint *0 ≤ c* with
*c* < 0 is left, the
combination that produced it *is* a Farkas certificate. You only have to record
which combination it was.

You can do it by adding bookkeeping to `eliminate`. There is also a trick that
needs no change to `eliminate` at all (HINTS.org, rung 2). Try for ten minutes
before looking.

**Done when** `step 5 ✓`. You get a valid certificate for 15 infeasible systems,
checked independently of your step 4, and `None` for feasible ones.

*Think about:* you have just proved Farkas' lemma constructively. FM always
terminates, and it ends either with every *0 ≤ c* satisfied (feasible) or with
one violated, and that constraint carries its certificate. This is the proof on slide
"Farkas, constructively".

---

## Then — against qhull and HiGHS  *(10 min, runs ~5 s)*

```fish
uv run co then 01
```

1. **Blow-up.** Constraints after each FM step, next to the number of *true* facets of
   each projection, which qhull computes. The reference run went 26 → 64 → 601 →
   70 996 constraints while the true facet count stayed between 29 and 39. Nearly
   everything FM generates is redundant. Keeping only the useful constraints is a
   research problem (Chernikov's rules, Imbert's acceleration), not a tidy-up.
2. **Vertices.** Your C(*m*, 3) enumeration against qhull as *m* grows. You get
   the same answer, and the reference run was about 60× to 6 000× slower. Note that
   the vertex count does *not* grow with C(*m*, 3): most bases are infeasible.
3. **A proof.** One infeasible system, your certificate printed as "multiply
   these constraints by these numbers and add", and HiGHS's verdict next to it. HiGHS
   is right, but in floating point. Yours is a proof in integers.

## Checkpoint

- [ ] `uv run co test 01` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** take the system `then` prints in part 3,
      cover the certificate, and produce one by hand (FM on paper, or by eye).
      Then explain *without reference to any solver* why it proves infeasibility.
      One sentence should do it.
- [ ] Say in your own words why a vertex, an extreme point and a basic feasible
      solution are the same thing, and which of the three your `vertices`
      function actually computes.

In `NOTES.md`: your blow-up numbers, and the sentence from the second box.

## Reading

- Bertsimas & Tsitsiklis, *Introduction to Linear Optimization*, ch. 2 (§2.1–2.6),
  and §4.6 for Farkas.
- Gärtner & Matoušek, *Understanding and Using Linear Programming*, §6.1–6.4. This
  is the cleanest short proof of Farkas, and it goes through FM exactly as step 5
  does.
- Optional: Ziegler, *Lectures on Polytopes*, lecture 1, for Minkowski–Weyl
  done properly.
