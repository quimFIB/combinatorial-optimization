# Lab 24 — LP rounding and the primal–dual method

**Time:** about 2½–3 hours. **Before:** the slides (`uv run co slides 24`).
**You write:** 17 functions in `lab.py`, 170–220 lines in all.
**Needs:** unit 03 (duality), unit 23 (lower bounds and tight instances).

Unit 23's lower bounds were ad hoc: a matching here, a spanning tree there. This unit replaces them
with one systematic bound, the LP relaxation, and uses it in the two classic ways. **Rounding** solves
the LP and turns its fractional solution into an integral one, deterministically (vertex cover) or at
random (set cover). **Primal–dual** never solves the LP. It grows a feasible dual solution and buys
primal objects that the dual has paid for exactly (set cover, then Jain and Vazirani's facility
location). Every analysis compares against the LP, so the LP's **integrality gap** limits all of them.
Step 5 builds instances that attain it.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.approx.covering_lp`: min c·x, Ax ≥ 1, 0 ≤ x ≤ 1, by HiGHS | Vertex cover LP and threshold rounding |
| `colib.approx.FacilityLocation` (metric, integer distances) | Set cover LP, randomized rounding, exact miss probabilities, expected cost, union bound |
| HiGHS MIP, brute force (tests); CP-SAT (`then`) | Frequency, primal–dual set cover |
| | Jain–Vazirani: dual ascent, pruning, assignment |
| | Two gap families, and a uniform fractional solution |

## Running it

```fish
uv run co test 24
uv run co test 24 --solution functional
```

## Style

Rounding is a map and probabilities are products, so steps 1–2 are comprehensions either way. The
primal–dual set cover is a fold over elements. Jain–Vazirani's dual ascent is an event-driven loop,
and it is the step where style matters: the imperative reference mutates `alpha` and a dict of opening
times, while the functional one unfolds over `(t, alpha, opened)` states. Use `Fraction` for times and
duals in both, because the tests check tightness with `==`.

---

## Step 1 — Vertex cover: the ½ threshold  *(20 min)*

*Shape: build a 0/1 matrix, call the LP, one comprehension.*

**Done when** `step 1 ✓`. The LP value never exceeds the integer optimum (HiGHS, 20 graphs), the
rounded cover is feasible and within 2·LP on 25 more, and the 5-cycle has LP 2.5 with all halves rounded
up to 5.

## Step 2 — Randomized rounding for set cover  *(35 min)*

*Shape: repeated coin flips; products; a sum; a formula.*

**Done when** `step 2 ✓`. The LP is feasible and ≤ OPT. Your exact per-element miss probabilities and
expected cost match 4 000 simulated roundings within 5 standard deviations. The rounds are independent
repetitions (a hand-built instance at x = ⅓ with t = 1 and t = 3), and the union bound holds for
t = 1, 2, 4, 8.

**The curriculum's build item** is "the failure probability measured empirically against the bound".
The tests do it per element. `then` does it for the whole cover.

## Step 3 — Primal–dual set cover  *(25 min)*

*Shape: a loop over elements with running payments.*

**Done when** `step 3 ✓`. On 30 instances, y is dual feasible, every bought set is exactly tight, cost ≤
f·Σy, and Σy ≤ LP. Hand-built instances check the element order and that *every* set that goes tight is
bought. On vertex cover (f = 2), cost ≤ 2·OPT.

## Step 4 — Jain–Vazirani facility location  *(50 min)*

*Shape: an event loop in exact arithmetic; a greedy non-conflicting set; nearest assignment.*

**Done when** `step 4 ✓`. Three hand-traced ascents give exact α and opening times. On 25 random
instances, no facility is overpaid, every temporarily open facility was paid exactly at its opening time,
and each client froze at min over open facilities of max(opening time, distance). Σα ≤ OPT. Pruning keeps
a maximal non-conflicting set in opening order (strictly-paying clients only), and cost ≤ 3·Σα ≤ 3·OPT.

*Think about:* the client-freezing test is stronger than the guarantee needs. Which invariant does the
factor-3 proof actually use?

## Step 5 — Integrality gaps  *(20 min)*

*Shape: two instance builders; a frequency count.*

**Done when** `step 5 ✓`. K_n has LP n/2 and optimum n − 1. The GF(2)^k family (k = 2, 3, 4) has sets of
size 2^{k−1}, a uniform fractional solution of value (2^k − 1)/2^{k−1} < 2, and a brute-forced optimum of
exactly k.

**This is the checkpoint.** An instance with OPT/LP = r proves that *no* algorithm analysed against this
LP can guarantee better than r. Write in `NOTES.md` why that's a statement about proofs, not about
algorithms: greedy set cover solves every instance of this family optimally (see `then`).

---

## Then — LP, optimum, algorithm  *(10 min, runs a few minutes)*

```fish
uv run co then 24
```

Plot: `out/then.png`, with the LP bound, the optimum and your algorithm on every instance.

**Weighted vertex cover** (24 graphs, weights 1–20, optimum by CP-SAT):

| | LP / OPT | rounding / OPT | primal–dual / OPT |
|---|---:|---:|---:|
| G(40, 0.15), G(80, 0.08), G(160, 0.04) | 0.89 | **1.74–1.75** | **1.38–1.40** |

Every LP solution HiGHS returned was **half-integral** (24/24), as the theory says basic solutions of
this LP must be. Rounding takes every ½, and that's why it loses to primal–dual here, though both carry
the same guarantee of 2.

**Set cover** (10 instances, 150 elements, 100 sets):

| | mean / OPT | worst / OPT | guarantee |
|---|---:|---:|---:|
| LP | 0.937 | 1.000 | — |
| randomized rounding, t = 7, best of 20 | 1.728 | 2.140 | O(log n) |
| primal–dual | 1.964 | 2.556 | f = 21 |
| greedy (unit 23) | **1.148** | **1.326** | H_d ≈ 5 |

Failure rates of randomized rounding against the union bound 150·e^{−t}:

| t | 1 | 2 | 4 | 7 |
|---|---:|---:|---:|---:|
| measured | 0.896 | 0.728 | 0.123 | **0.0033** |
| bound | 1 | 1 | 1 | 0.137 |

**The GF(2)^k family:**

| k | sets | LP | OPT | OPT / LP | greedy | primal–dual |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 7 | 1.750 | 3 | 1.71 | 3 | 4 |
| 5 | 31 | 1.938 | 5 | 2.58 | 5 | 16 |
| 7 | 127 | 1.984 | 7 | 3.53 | 7 | **64** |

The gap grows like k/2 ≈ ½ log₂ n. Greedy is optimal on every member. Primal–dual pays 2^{k−1}: every
element here lies in 2^{k−1} sets, and the analysis's factor f is attained.

**Facility location** (30 instances up to 30 facilities × 120 clients): the LP was **integral on all
30**. JV's mean ratio to the optimum was 1.03–1.06 (worst 1.14), and Σα / OPT was 0.99. The integrality gap you
read about doesn't appear on random metric instances. Its bad cases have to be built.

Things to notice:

- **The LP-based algorithms lose to greedy on set cover**, even though greedy's worst case is the same
  order. A better guarantee from a relaxation isn't a better algorithm on your instances. Unit 28 will
  ask you to measure before believing either.
- **The union bound is loose** by a factor of 40 at t = 7. It counts every element's miss separately,
  but misses are rare and correlated through shared sets.

## Checkpoint

- [ ] `uv run co test 24` shows all five steps ✓.
- [ ] You can exhibit an instance realising the integrality gap of a given LP (K_n for vertex cover, GF(2)^k
      for set cover) and explain why it proves no rounding of that LP can beat that ratio.
- [ ] You can explain why primal–dual set cover pays f on the GF(2)^k family, and greedy doesn't.

## Reading

- Williamson & Shmoys (2011), ch. 1 (rounding and dual fitting), ch. 7 (primal–dual), ch. 4 (facility
  location). Free online.
- Vazirani, *Approximation Algorithms* (2001), ch. 14–15 and 24.
- Jain & Vazirani, "Approximation algorithms for metric facility location and k-median problems using the
  primal-dual schema and Lagrangian relaxation", *JACM* 48 (2001).
- Jain, "A factor 2 approximation algorithm for the generalized Steiner network problem", *Combinatorica*
  21 (2001): iterative rounding.
