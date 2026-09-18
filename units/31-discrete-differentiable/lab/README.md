# Lab 31 — Where discrete meets differentiable

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 31`).
**You write:** 17 functions in `lab.py`, 150–200 lines in all.
**Needs:** unit 30 (autodiff), unit 07 (branch and bound), unit 15 (assignment), unit 28 (evaluation).

Every decision in this course is an argmax: an assignment, a branching variable, a tour. Its derivative is
zero almost everywhere and undefined where the decision switches, so gradient-based learning can't see
through it. This lab tries the four standard ways around that. It relaxes the decision (Sinkhorn instead of the
Hungarian algorithm), reparameterises a random one (Gumbel-softmax, straight-through), estimates the
gradient without differentiating (REINFORCE), and differentiates the optimality conditions of a continuous
relaxation (the implicit function theorem on KKT). Then it asks whether learning helps inside an exact
solver: a branching rule for unit 07 trained to imitate strong branching, evaluated with unit 28's method.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| JAX; scipy's `logsumexp` | Log-domain Sinkhorn; greedy rounding; assignment cost |
| cvxpy, scipy's assignment solver (tests) | A differentiable entropic cost and its gradient |
| Unit 07's branch and bound and strong branching (`colib.ref`) | Gumbel-max, Gumbel-softmax, straight-through; exact and REINFORCE gradients |
| Unit 15's Hungarian, unit 28's statistics (`then`) | Active constraints and the argmin Jacobian of a QP |
| | Branching features, strong-branching data collection, a ranker, a learned rule |

## Running it

```fish
uv run co test 31
uv run co test 31 --solution functional
```

The suite takes about a minute: the argmin tests solve about 90 QPs for finite differences.

## Style

Sinkhorn and the ranker are folds over iterations; rounding is a fold over sorted entries. The one stateful
piece in the functional reference is the strong-branching recorder, which has to observe unit 07's tree while
it runs, so it appends to a local list.

---

## Step 1 — Sinkhorn  *(30 min)*

*Shape: two logsumexp updates in a loop; a greedy pass over sorted entries.*

**Done when** `step 1 ✓`. On 8 cost matrices the plan is positive, columns sum to 1 exactly and rows to within
1e−6, and log P has the potential structure f_i + g_j − C_ij. One iteration matches a hand computation.
At ε = 0.02 and 3 000 iterations the rounded plan is optimal on 8 instances with integer-like costs. The
greedy rounding follows its tie rule.

## Step 2 — Gradients through Sinkhorn  *(20 min)*

*Shape: the same loop in JAX; jax.grad.*

**Done when** `step 2 ✓`. The entropic cost matches its formula, and its gradient equals the Sinkhorn
plan P to 1e−6 on 5 instances (the envelope theorem), and a central difference to 1e−5.

## Step 3 — Discrete samples, continuous gradients  *(35 min)*

*Shape: noise plus argmax; softmax at a temperature; stop_gradient; two formulas.*

**Done when** `step 3 ✓`. 20 000 Gumbel-max samples match softmax probabilities within 5 standard errors.
Gumbel-softmax uses the specified noise and approaches one-hot as τ → 0. Straight-through is exactly one-hot
forward, with the soft sample's gradient. The exact expectation gradient matches `jax.grad`, REINFORCE over
40 000 samples is within 0.02 of it, and a single-sample estimate matches its formula.

## Step 4 — Differentiating an argmin  *(30 min)*

*Shape: select the active constraints; one block linear solve.*

**Done when** `step 4 ✓`. Active sets exclude weakly active constraints. On 8 random QPs with 6 constraints
the Jacobian matches finite differences of CVXPY solutions to 1e−4. With no active constraint it's −Q⁻¹,
and a variable pinned by a bound gets a zero column.

## Step 5 — Learning to branch  *(55 min)*

*Shape: a feature table per node; a recording rule; softmax cross-entropy by gradient descent.*

**Done when** `step 5 ✓`. Features match a hand-built node, recorded choices are exactly strong
branching's, and the ranker learns the informative feature of a synthetic task (accuracy ≥ 0.8) with an
exactly averaged first step. The learned rule picks the top-scoring candidate and reaches the optimum.

---

## Then — four comparisons  *(15 min, runs about 6 minutes)*

```fish
uv run co then 31
```

**1. Sinkhorn against the Hungarian algorithm** (costs uniform in [0, 1]; mean cost per row; a random
assignment costs 0.5):

| n | optimal | Hungarian | Sinkhorn ε = 0.05 | ε = 0.01 | ε = 0.002 (6 000 iterations) |
|---:|---:|---:|---:|---:|---:|
| 50 | 0.0238 | 0.002 s | 0.0371 (0.11 s) | 0.0320 (0.55 s) | **0.0238** (2.2 s) |
| 100 | 0.0163 | 0.013 s | 0.0311 (0.21 s) | 0.0261 (1.0 s) | 0.0250 (4.1 s) |
| 200 | 0.0089 | 0.062 s | 0.0193 (0.87 s) | 0.0217 (2.9 s) | 0.0225 (11.6 s) |

Sinkhorn is **not** a competitive way to solve an assignment on a CPU. It was 180× slower than your
Hungarian at n = 200 and 2.5× worse in cost, and colder ε didn't help there (greedy rounding of a
plan that is still spread over many entries). The optimal gaps between good assignments shrink like 1/n,
so ε has to shrink with them, and Sinkhorn's iteration count grows like 1/ε. Its value is elsewhere: a
smooth, batched, GPU-friendly plan with a gradient (step 2) that the Hungarian algorithm can't give.

**2. One-sample gradient estimators** of E[f(k)] over 10 categories, 2 000 draws (exact gradient norm 0.496):

| estimator | bias (norm) | spread (norm of std) | noise level of the bias, spread/√2000 |
|---|---:|---:|---:|
| REINFORCE | 0.020 | 1.818 | 0.041 |
| straight-through, τ = 0.1 | 0.059 | 2.529 | 0.057 |
| straight-through, τ = 0.5 | 0.044 | 0.841 | 0.019 |
| straight-through, τ = 1.0 | **0.137** | **0.406** | 0.009 |

REINFORCE is unbiased and noisy. Straight-through trades noise for bias as τ grows: at τ = 1 its spread is
4.5× smaller than REINFORCE's, and its bias is 15 noise levels wide. At τ = 0.1 it's noisier than REINFORCE
and its bias can't be told from noise.

**3. An argmin layer** for a box-constrained QP (n = 30, 19 variables at a bound): your implicit Jacobian
and JAX differentiating through 500 unrolled projected-gradient steps both match finite differences to
6.8e−10. The implicit one takes 1.1 ms after the solve, the unrolled one 4.9 ms, and finite differences need 60
extra solves (0.34 s). cvxpylayers isn't installed; it does what step 4 does for any convex program written in its disciplined parametrized form.

**4. A learned branching rule** trained on 954 strong-branching decisions from 10 knapsacks (16 items) and
tested on 20 held-out knapsacks (18 items):

| rule | SGM nodes | median | SGM seconds | fewest nodes on |
|---|---:|---:|---:|---:|
| most-fractional | 541 | 574 | 0.35 | 0 |
| pseudocost | 510 | 543 | 0.35 | 0 |
| **strong** | **386** | **431** | 0.84 | **20** |
| learned | 536 | 553 | 0.37 | 0 |

| paired on nodes | ratio [95% bootstrap] | Wilcoxon p (Holm) |
|---|---|---|
| learned / most-fractional | 0.99 [0.94, 1.03] | 0.65 (0.65) |
| learned / pseudocost | 1.05 [1.00, 1.10] | 0.05 (0.10) |
| learned / strong | 1.38 [1.29, 1.46] | 0.0001 (0.0003) |

**The learned rule does not beat most-fractional.** Here is why, in unit 28's terms rather than as an anecdote:

- The comparison is paired over 20 held-out instances from a stated generator, and the interval
  [0.94, 1.03] contains 1. There's no evidence of a difference: an improvement of more than 6%, or a loss of
  more than 3%, is unlikely.
- The model learned mostly fractionality: weights [2.27, 0.62, 0.36, −0.07, 0.07] on
  [fractionality, |c|, column weight, f, 1 − f]. So it's close to most-fractional by construction.
- Its imitation accuracy on held-out decisions, 0.58, is barely above **most-fractional's own agreement with
  strong branching, 0.55**. The features can't express what strong branching knows. Strong branching's
  choice depends on the LP bound change from probing each child. Nothing in the five features (the
  variable's cost and column, and its current LP value) carries that information.
- What would change it: features computed from the node LP (reduced costs, dual values, the objective
  change predicted by one dual simplex step), which is what Gasse et al. (2019) feed a graph neural network.
  The same protocol would then decide whether that helps.

## Checkpoint

- [ ] `uv run co test 31` shows all five steps ✓.
- [ ] **Your imitation-learned branching rule beats most-fractional branching on node count on held-out
      instances, or you can say precisely why it did not, in terms of unit 28's methodology rather than
      anecdote.** (Above: it did not, with the interval, the test, and the imitation-accuracy baseline that
      explains it.)
- [ ] You can say, for each of the four techniques, what it buys and what it costs, with the numbers.

## Reading

- Cuturi, "Sinkhorn distances: lightspeed computation of optimal transport", *NeurIPS* 2013.
- Maddison, Mnih & Teh, "The concrete distribution", and Jang, Gupta & Poole, "Categorical
  reparameterization with Gumbel-softmax", both *ICLR* 2017.
- Amos & Kolter, "OptNet: differentiable optimization as a layer in neural networks", *ICML* 2017; Agrawal et
  al., "Differentiable convex optimization layers" (cvxpylayers), *NeurIPS* 2019.
- Gasse, Chételat, Ferroni, Charlin & Lodi, "Exact combinatorial optimization with graph convolutional
  neural networks", *NeurIPS* 2019.
- Bengio, Lodi & Prouvost, "Machine learning for combinatorial optimization: a methodological tour
  d'horizon", *EJOR* 290 (2021).
