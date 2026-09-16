# Lab 20 — SAT and the CDCL engine

**Time:** about 3½ hours. **Before:** the slides (`uv run co slides 20`).
**You write:** a solver class (13 methods) and 7 encoders in `lab.py`, 280–350 lines in all.
**Needs:** unit 17 (propagation and search), unit 19's `luby`.

Conflict-driven clause learning is the algorithm behind every competitive SAT solver, and
since unit 21 behind CP-SAT too. This lab builds it from the inside: two watched literals for
propagation, first-UIP conflict analysis, non-chronological backjumping, VSIDS activity with
phase saving, Luby restarts, and clause deletion by LBD. Every unsatisfiability answer comes
with a DRAT proof that an independent checker replays. Then you encode puzzles as CNF, including
the pigeonhole principle, which **no** resolution-based solver can refute quickly. That lower bound
is the unit's point.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `to_internal`, `to_dimacs`, `Fresh`, unit 19's `luby` | Assignment, clause loading, two-watched-literal propagation |
| `colib.drat.check_rup_proof` (and drat-trim, if installed) | First-UIP conflict analysis, backjumping with phase saving |
| `colib.formats.read_cnf`/`write_cnf`; pysat's MiniSat, CaDiCaL, Kissat (tests, `then`) | Branching, the CDCL loop, restarts |
| | DRAT output and LBD-based clause deletion |
| | At-most-one encodings (pairwise, sequential, bitwise), at-most-k, pigeonhole, queens, colouring |

## Running it

```fish
uv run co test 20
uv run co test 20 --solution functional
```

## Style

A CDCL solver's trail, watch lists and activity array are mutable state by design: two watched
literals exist precisely to avoid rebuilding anything when you backtrack. **The functional reference
inherits that machinery from the imperative one** and rewrites the parts a functional reading
clarifies. Conflict analysis becomes an explicit fold of resolution steps (`iterate(resolve,
conflict)` until one current-level literal remains), and every encoder becomes a comprehension. Do
the same if you're working functionally.

---

## Step 1 — Assignment and propagation  *(50 min)*

*Shape: a trail, per-variable value/level/reason, and the watch loop.*

**Done when** `step 1 ✓`: clause loading drops tautologies and duplicates and propagates units. On
40 random formulas with random decisions, your propagation reaches the same assignment and the same
conflicts as naive unit propagation. Reasons and levels are recorded, with the implied literal first
in its reason.

## Step 2 — Conflict analysis  *(50 min)*

*Shape: walk the trail backwards, resolving away current-level literals.*

**Done when** `step 2 ✓`. On 60 random conflicts (with level-0 facts mixed in), every learned clause
is false now, has exactly one current-level literal (first), and puts a literal of the backjump level
second. It is **implied by the formula** (checked by MiniSat) and becomes unit after the backjump.
On the textbook example, the first UIP is the decision itself, not the literal that looks closest to
the conflict. Backjumping saves phases.

## Step 3 — The loop  *(35 min)*

*Shape: propagate; learn, backjump and enqueue on conflict; decide otherwise.*

**Done when** `step 3 ✓`: 80 random 3-SAT instances at the threshold agree with MiniSat and every model
satisfies its formula. Branching picks the most active variable with its saved phase. The conflict
limit returns None at level 0. Restarts happen, and the VSIDS increment grows.

## Step 4 — Proofs and deletion  *(30 min)*

*Shape: append lines; sort candidates by LBD and delete half.*

**Done when** `step 4 ✓`: 30 above-threshold instances produce DRAT proofs that `colib.drat` accepts,
including a pigeonhole proof with deletions. reduce_db keeps glue (LBD ≤ 2) and locked clauses and
deletes exactly the worse half. Deleting every 5 conflicts leaves the solver correct.

## Step 5 — Encodings  *(35 min)*

*Shape: clause comprehensions with fresh variables.*

**Done when** `step 5 ✓`: every at-most-one encoding and the at-most-k counter allow exactly the right
assignments on the original variables, with the textbook clause and variable counts. Queens solutions
are valid under all three encodings, 6-queens has exactly 4, and colouring matches brute force.
**Pigeonhole's conflicts grow more than 3× per extra hole.**

---

## Then — against MiniSat, CaDiCaL and Kissat  *(10 min, runs ~8 minutes)*

```fish
uv run co then 20
```

Every instance goes out to a DIMACS file and is read back before solving.

**Random 3-SAT, m = 4.26 n** (conflicts / seconds; Kissat's pysat binding reports no conflicts):

| instance | result | yours | MiniSat | CaDiCaL | Kissat s |
|---|---|---:|---:|---:|---:|
| n=150 #1 | UNSAT | 2 236 / 0.40 | 3 051 / 0.015 | 3 217 / 0.034 | 0.053 |
| n=200 #0 | SAT | 8 588 / 2.31 | 7 748 / 0.048 | 1 171 / 0.012 | 0.066 |
| n=250 #0 | UNSAT | > 100 000 / 35 | 331 773 / 2.85 | 141 277 / 4.14 | 3.11 |
| n=250 #1 | SAT | > 100 000 / 40 | 68 809 / 0.54 | 21 028 / 0.40 | 0.068 |

Up to n = 200 your solver needs about as many conflicts as MiniSat, which is the algorithm working,
at 30–50× the time per conflict, which is Python. At n = 250 the conflict counts explode for everyone:
random 3-SAT at the threshold is exponentially hard for resolution.

**Pigeonhole** (n + 1 into n):

| instance | yours | MiniSat | CaDiCaL | Kissat s |
|---|---:|---:|---:|---:|
| 7 into 6 | 784 / 0.11 | 2 498 / 0.007 | 1 044 / 0.005 | 0.004 |
| 9 into 8 | 41 364 / 26.5 | 39 063 / 0.19 | 31 719 / 0.37 | 0.13 |
| 10 into 9 | — | 510 308 / 3.6 | 267 023 / 4.7 | 0.50 |
| 11 into 10 | — | **10.7 M / 124** | 2.2 M / 48.8 | **3.2** |

Each extra hole multiplies MiniSat's conflicts by roughly 4–20. Resolution refutations of pigeonhole need
exponential size (Haken 1985), and CDCL is resolution. Kissat's 40× lead at 11 into 10 doesn't
contradict that. The bound is exponential in n, not a fixed large number, and at n = 10 better
heuristics and preprocessing still fit inside it. Its own conflict count isn't reported, so this lab
doesn't claim to explain the gap. Add a hole or two and it grows for Kissat too.

**Queens, your solver** (variables / clauses / seconds):

| n | pairwise | sequential | bitwise |
|---:|---:|---:|---:|
| 20 | 400 / 12 560 / 0.04 | 1 882 / 4 352 / 0.15 | 866 / 7 276 / 0.09 |
| 40 | 1 600 / 103 520 / **0.33** | 7 762 / 18 292 / 3.82 | 2 776 / 35 584 / 0.88 |
| 60 | 3 600 / 352 880 / **0.97** | 17 642 / 41 832 / 20.9 | 5 496 / 83 604 / 10.5 |

The encoding with the most clauses is the fastest. Pairwise at-most-one propagates in one step,
while the sequential counter needs a chain of auxiliary variables and gives the heuristic many
irrelevant variables to branch on. "Fewer clauses" is not the goal.

**Proofs:** an unsatisfiable 3-SAT instance with n = 120 gives 831 lemmas, and 7 into 6 gives 784.
The colib checker accepts both in 0.2 s. Install drat-trim and `then` runs it on the same files.

## Checkpoint

- [ ] `uv run co test 20` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** your solver emits a DRAT proof that an external checker accepts,
      and you can explain pigeonhole's hardness in terms of resolution lower bounds rather than "it
      just takes a long time".
- [ ] You can say why the first UIP in the textbook example is the decision, and what the learned
      clause is.

## Reading

- Marques-Silva, Lynce & Malik, "Conflict-driven clause learning SAT solvers", ch. 4 of the *Handbook
  of Satisfiability* (2nd ed., 2021).
- Eén & Sörensson, "An extensible SAT-solver", *SAT* 2003: the MiniSat paper, and this lab's architecture.
- Audemard & Simon, "Predicting learnt clauses quality in modern SAT solvers", *IJCAI* 2009: LBD.
- Haken, "The intractability of resolution", *TCS* 39 (1985). Buss's short survey "Towards NP–P via
  proof complexity and search" (2012) is the gentle entry.
- Wetzler, Heule & Hunt, "DRAT-trim", *SAT* 2014.
