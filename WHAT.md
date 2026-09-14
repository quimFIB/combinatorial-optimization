A self-study curriculum in combinatorial and constrained optimization: 32 units
in which theory is interleaved with from-scratch Python implementations, each
then benchmarked against the industrial solver that does the same job.

`CURRICULUM.html` is the proposal — open it in a browser. It is ordered as a
dependency graph rather than a calendar, because there is no fixed schedule:
three independent trunks (LP→IP, combinatorial algorithms, CP/SAT) descend from
one root unit and converge at approximation, practice, and a coda on autodiff
and the discrete/differentiable seam.

`map/mkmap.py` generates the dependency diagram. It rewrites the region between
the `MAP:BEGIN` / `MAP:END` markers in `CURRICULUM.html` in place — edit the
node coordinates and edge list there, not the SVG in the HTML.

`README.md` describes the course materials: layout, the `co` command, and the
conventions for writing further units.

## State

- 2026-09-12: proposal written.
- 2026-09-13: delivery format settled and piloted. Theory is a reveal.js slide
  deck per unit, with notes for self-study. Practice is a scaffolded lab:
  `colib` provides problems, oracle, harness and runner; the learner fills in
  stubs against staged tests, with a hint ladder and a reference solution.
  Units 00 and 01 are fully built, and their reference solutions pass all tests.
- 2026-09-13 (later): building continued. Units 00–19 are built: slides, lab,
  two reference solutions (imperative and functional) that pass, a mutation
  check of the tests, and a measured `then.py` step. The README's "Built so far"
  table is the per-unit record. Nothing has been studied yet.
- 2026-09-13 (end of day): all 32 units (00–31) are built: slides, lab, two
  reference solutions that pass, a mutation check, and a measured `then.py`.
  The capstone is not built. Unit 28's audit withdrew one earlier conclusion
  (unit 19's "restarts make the median worse"), corrected in place.
  Units 27 and 30 deviate from the curriculum text (bin packing instead of "your model from 05/07";
  matplotlib's elevation data instead of a downloaded dataset) and say so in their lab sheets. Nothing has
  been studied yet.
- 2026-09-14: the capstone is built (`units/capstone-cvrptw`, `uv run co test capstone`): VRPTW on
  Solomon's instances (`uv run co data`), solved by SCIP branch-and-cut with the learner's capacity cuts,
  branch-and-price, CP-SAT and ALNS, then refereed. Both references pass all 114 tests, and the tests
  kill every non-equivalent mutant. The reference benchmark (672 runs, `lab/out/then.txt`) found no
  invalid solution or refuted claim. Branch-and-price wins tight-window instances at 25 customers, the
  compact MIP makes most proofs on clustered ones, and ALNS wins on solution quality past 25 customers.
  Every step of every unit's HINTS.md now has a "Functional route" fold.
- 2026-09-14: every unit's HINTS.md is now HINTS.org. The `<details>` folds only collapsed in a
  browser, and Emacs showed every rung open; `#+startup: content` opens the Org file with the step
  and rung headings visible and every rung body folded.

One consequence for the curriculum text: unit 00 no longer has the learner
build the harness and instance library. `colib` ships them, and lab 00 has the
learner write the oracle, the models and a certificate checker.
`CURRICULUM.html` still describes the original "build it all" version of
unit 00.

## Open questions the proposal names

- Which of the six optional branch units (04, 06, 09, 12, 21, 25) stay in.
- Whether the per-unit notes become one Markdown file each, or a dear-guide
  graph with each checkpoint as a task carrying its own falsifier.
- Whether a Gurobi academic licence is available; SCIP substitutes throughout
  if not.

Settled: the capstone problem is CVRPTW (2026-09-14).

## Resume

    uv sync && uv run co slides 00

## Promotion

Promoted out of `_scratch/` into `courses/` on 2026-09-14, with a card in the
workspace `index.html`.
