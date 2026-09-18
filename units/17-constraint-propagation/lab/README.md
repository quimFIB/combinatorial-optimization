# Lab 17 — A small constraint programming engine

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 17`).
**You write:** a store, AC-3, five propagators, the fixpoint loop, search and four models,
250–320 lines in all.
**Needs:** unit 00 only. This is the start of Part IV.

MIP relaxes and bounds. CP does something else: it removes values that can't be part
of any solution, as early and as cheaply as possible, and searches over what remains.
This lab builds the whole loop: domains with a trail, propagators, a queue that runs
them to a fixpoint, and depth-first search that branches and undoes. It then models
four classic puzzles. Two numbers, **nodes** and **propagations**, are the whole
diagnostic vocabulary of Part IV. You instrument both, and units 18–21 improve one
at the expense of the other.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `Stats`, `watches`, `_Overlay` | A trailed domain store |
| Propagator class skeletons (their constructors) | `revise` and AC-3 |
| OR-Tools CP-SAT (in `then`) | `prune` for Binary, NotEqual, LinearLe, LinearEq, Count |
| | The propagation fixpoint |
| | First-fail and depth-first search with propagation |
| | Models: n-queens, sudoku, map colouring, magic series |

**This engine is reused.** Unit 18 adds global constraints to it, unit 19 swaps its search,
and unit 21 makes its propagators explain themselves. Keep the interfaces exactly as the
docstrings say.

## Running it

```fish
uv run co test 17
uv run co test 17 --solution functional
```

## Style

Propagators are pure functions of the domains, by design, so they read the same in either
style. The interesting difference is search. The imperative engine mutates one store and
undoes changes on the trail. The functional engine passes immutable domain tuples down the
recursion, so backtracking is simply returning and it needs no trail at all. It's 3–10×
slower in Python, and it produces **identical node and propagation counts**. The trail is
what mutation costs you.

---

## Step 1 — The store  *(20 min)*

*Shape: a list of frozensets and a stack of (variable, old domain).*

**Done when** `step 1 ✓`: narrowing, undo to nested marks, and random sequences of changes
and undos restore exactly the right domains. No-op changes aren't trailed, and `changed` lists
the variables touched.

## Step 2 — AC-3  *(25 min)*

*Shape: a queue of arcs.*

**Done when** `step 2 ✓`: 40 random binary CSPs match naive repeated sweeps, a chain
x₀ < x₁ < … < x₉ collapses to singletons in under 180 revise calls, and a wipe-out returns None.
One test is a triangle with two colours: arc consistent, yet unsatisfiable.

## Step 3 — Propagators and the fixpoint  *(55 min)*

*Shape: five small pure functions, then a queue of propagators with watch lists.*

**Done when** `step 3 ✓`. NotEqual and Binary are arc consistent, and LinearLe is domain
consistent, all checked against brute-force supports. LinearEq and Count never remove a
supported value, and both prune in the textbook examples. On 60 random models with every
propagator kind, your fixpoint equals the one naive sweeps reach. `dirty` wakes only
watchers, and the failing propagator is reported.

*Think about:* why must a propagator that narrows its own variables be re-queued? (LinearEq
and Count are not idempotent. The random fixpoint test catches an engine that assumes they
are.)

## Step 4 — Search  *(30 min)*

*Shape: recursive DFS, mark, branch, propagate, undo.*

**Done when** `step 4 ✓`: n-queens has 1, 0, 0, 2, 10, 4, 40, 92 solutions for n = 1…8,
all distinct and valid. Colouring matches brute force, the node limit stops the search, and a
custom heuristic and the failure hook are both used.

## Step 5 — Models  *(25 min)*

*Shape: build lists of propagators.*

**Done when** `step 5 ✓`. The easy sudoku is solved **with zero search nodes**, and Inkala's
"hardest" sudoku has exactly one solution. The 4×4 sudoku has 56 constraints and one
solution, and Australia has 18 3-colourings. Magic series has the right solutions for n = 4, 5,
6, 7 and 10, in at most 2n nodes, thanks to the redundant constraint.

---

## Then — against CP-SAT  *(10 min, runs ~2 minutes)*

```fish
uv run co then 17
```

Same decomposed models for both:

| model | your nodes | propagations | your s | CP-SAT branches | conflicts | CP-SAT s |
|---|---:|---:|---:|---:|---:|---:|
| queens 8, all 92 | 766 | 47 958 | 0.07 | 4 091 | 1 361 | 0.087 |
| queens 11, all 2 680 | 48 950 | 4 805 359 | 7.52 | 226 330 | 97 093 | 8.60 |
| queens 60, one | 862 | 921 885 | 1.61 | 38 681 | 149 | 2.37 |
| sudoku (Inkala), all | 3 598 | 823 458 | 1.30 | 6 538 | 626 | **0.12** |
| magic series 40, all | 74 | 4 317 | 0.07 | 0 | 0 | 0.02 |
| 3-colour G(200, 4.4/n) #0, unsat | 120 334 | 17 610 637 | 26.5 | 3 106 | 92 | **0.16** |
| 3-colour G(300, 4.4/n) #0, unsat | limit 300 000 | 40 779 224 | 67.7 | 17 937 | 2 590 | **0.27** |

On queens, your pure-Python engine keeps up with CP-SAT, and is sometimes faster.
Enumerating all solutions is a pure search-tree walk (CP-SAT enumerates single-threaded), and a
small engine has less overhead per node. On sudoku, CP-SAT is 10× faster
even though it branches more (6 538 against your 3 598 nodes). On unsatisfiable 3-colouring near the phase transition, your engine
explores 120 000 nodes where CP-SAT needs 3 000, and at n = 300 yours gives up after 300 000.
The difference is **learning**: CP-SAT records why each branch failed and never repeats that
mistake. Units 20 and 21 build exactly that.

## Checkpoint

- [ ] `uv run co test 17` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** you can trace your propagator's fixpoint by hand on a 4×4
      sudoku (try the one in the tests), and explain why arc consistency does not imply
      satisfiability (the two-colour triangle).
- [ ] You can say what nodes and propagations each measure, and why one usually rises when
      the other falls.

## Reading

- Rossi, van Beek & Walsh (eds.), *Handbook of Constraint Programming* (2006), ch. 3
  (consistency) and ch. 4 (search). Chapter 3 by Bessière is the reference.
- Mackworth, "Consistency in networks of relations", *Artificial Intelligence* 8 (1977): AC-3.
- Schulte & Stuckey, "Efficient constraint propagation engines", *TOPLAS* 31 (2008). How real
  engines schedule propagators. Your fixpoint is the simple version.
