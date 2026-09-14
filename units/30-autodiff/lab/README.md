# Lab 30 — Automatic differentiation

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 30`).
**You write:** 50 functions and methods in `lab.py`, most of them one or two lines; 220–280 lines in all.
**Needs:** unit 29 (gradients and their uses), unit 28 (checking claims against a reference).

Three things are constantly confused: symbolic differentiation (manipulating formulas), numerical
differentiation (finite differences), and automatic differentiation (applying the chain rule to the
operations a program actually executes). This lab builds automatic differentiation three times. Dual
numbers push derivatives forward, one input direction per pass. A scalar tape records operations and
sweeps them backwards, giving the whole gradient in one pass. An array tape does the same over numpy
arrays and trains a small network on real terrain data. The scalar tape is written so it works on dual
numbers too, which gives Hessian-vector products for free.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `Tensor` (a value on a tape, with `_record`) | `Dual` arithmetic; exp, log, sin, cos, tanh on floats and Duals; derivative; forward gradient |
| matplotlib's Jacksboro elevation model (`then`) | `Var` arithmetic; vexp, vlog, vsin, vtanh, vrelu; backward; reverse gradient; Hessian-vector products |
| JAX (`then` only) | The array ops and their vjps; tensor backward; saved bytes; an op gradient checker |
| | MLP init, loss, gradients, training, and the tape size predicted from the architecture |

**About the dataset.** The curriculum asks for "a real dataset". sklearn isn't installed and downloads
need your permission, so `then` uses a real dataset already on disk: matplotlib's sample digital
elevation model of the Jacksboro fault region, 344 × 403 elevations in metres. The MLP learns
elevation from grid coordinates.

## Running it

```fish
uv run co test 30
uv run co test 30 --solution functional
```

## Style

Dual numbers and graph nodes are values in both references. Where the API is state by definition (node
`.grad` fields, the tape's entry list), the functional reference computes gradients into a local dict and
writes them at the end. Its first attempt used persistent tuples for the DFS stack, and was far too slow on the 20 000-node
test. That's a real cost of purity in Python, so the lab sheet says so.

---

## Step 1 — Dual numbers  *(35 min)*

*Shape: a class with twelve operators; five functions that take either type.*

**Done when** `step 1 ✓`: the arithmetic rules on hand values, derivatives of four composite functions at
four points to 1e−9, and forward-mode gradients of a 3-input expression, using every operation, against
central differences.

## Step 2 — The scalar tape  *(45 min)*

*Shape: the same operators recording parents; an iterative topological sweep.*

**Done when** `step 2 ✓`. Reverse-mode gradients equal forward-mode ones to 1e−12 on 8 points. A
shared subexpression accumulates correctly, a graph with 2³⁰ paths finishes in time (each node once),
and a 20 000-deep graph doesn't hit the recursion limit. Repeated sweeps restart from zero, and relu has
derivative 0 at 0. Hessian-vector products match finite differences of your own gradients, and are exact
on a quadratic.

## Step 3 — The array tape  *(35 min)*

*Shape: four ops with vjps; a reverse loop; a gradient checker.*

**Done when** `step 3 ✓`. Your checker passes all four ops below 1e−6 and catches a wrong tanh vjp. MSE
and a matrix used twice accumulate correctly, and saved bytes count each array once (tanh's output isn't
double-counted, relu's boolean mask is one byte per entry).

## Step 4 — An MLP and its memory  *(35 min)*

*Shape: a layer loop; a closed-form byte count; an SGD loop.*

**Done when** `step 4 ✓`. Initialisation has the right shapes and scale. Every parameter's gradient matches
central differences on 3 networks. **Your predicted tape size equals the measured one** for four
architectures and batch sizes, one full-batch step is exactly W − lr·∇W for weights and biases, and 60
epochs learn a smooth 2-D function.

---

## Then — against JAX, and on real data  *(10 min, runs about 20 seconds)*

```fish
uv run co then 30
```

**Agreement** (float64, 20 random points): reverse-mode gradients vs `jax.grad` 8.9e−16; forward-mode
Jacobians vs `jacfwd` and `jacrev` 8.9e−16; Hessian-vector products vs `jax.hessian` 1.6e−15.

**Cost** of the gradient of Σ sin(x_i)·x_{i+1}:

| n | forward mode (n passes) | reverse mode (1 sweep) | `jax.grad`, jit |
|---:|---:|---:|---:|
| 10 | 0.000 s | 0.0001 s | 0.0002 s |
| 100 | 0.014 s | 0.0007 s | 0.0004 s |
| 1 000 | **1.55 s** | **0.0057 s** | 0.0021 s |

Forward mode's cost grows like n²: n passes, each O(n). Reverse mode's grows like n. At n = 1 000 that's
a factor of 270, and it's the reason every neural network is trained with reverse mode.

**Real data**: elevation over the 344 × 403 grid (standard deviation 162.5 m); MLP 2 → 64 → 64 → 1 with
tanh, batch 64, 60 epochs of SGD at lr 0.05, trained on 6 000 points and tested on 6 000 others.

| | test RMSE | seconds |
|---|---:|---:|
| predict the mean | 161.3 m | |
| least squares, linear in (x, y) | 144.9 m | |
| **your MLP** | **90.4 m** (train 88.6 m) | 1.8 |
| the same network, weights and batch order in JAX with jit | 90.4 m | 2.6 |

**Tape memory per batch: predicted 233 480 bytes, measured 233 480 bytes.** One batch's gradients agree
with `jax.grad` to 3.9e−16. JAX was *slower* here. A likely reason, not measured: with 64-unit layers,
per-step Python overhead and host-to-device array conversion outweigh what compilation saves. Don't read
it as a claim about JAX in general: wide layers or an accelerator change the balance.

**Where autodiff lies** (what JAX returns at points where the derivative doesn't exist or isn't what the
code suggests):

| expression | JAX's gradient | truth |
|---|---:|---|
| `jnp.maximum(x, 0)` at 0 | 0.5 | undefined (one-sided 0 and 1) |
| `jax.nn.relu` at 0 | 0.0 | the same function, another convention |
| `jnp.abs` at 0 | 1.0 | undefined (one-sided −1 and 1) |
| `sqrt(x²)` at 0 | nan | undefined, and the chain rule hits 0·∞ |
| `where(x != 1, x, 1.0)` at 1 | 0.0 | the function is the identity, so 1 |
| `argmax([x, 0.5])` at 0.2 | 0.0 | 0 almost everywhere, a jump at 0.5 |

Autodiff differentiates the program that ran, branch by branch, not the mathematical function it
computes.

## Checkpoint

- [ ] `uv run co test 30` shows all four steps ✓.
- [ ] **Your reverse-mode engine trains an MLP on a real dataset, and you can compute the tape's memory
      cost in bytes before you run it** (`then`: predicted and measured both 233 480).
- [ ] You can explain the n-versus-1 passes result, and give an example of each lie in the table.

## Reading

- Baydin, Pearlmutter, Radul & Siskind, "Automatic differentiation in machine learning: a survey", *JMLR* 18
  (2018).
- Griewank & Walther, *Evaluating Derivatives* (2nd ed., 2008), ch. 3–4 and 12 (checkpointing).
- Karpathy, *micrograd* (2020): a scalar reverse-mode engine in about 100 lines, the same design as step 2.
- The JAX documentation, "Autodiff cookbook": JVPs, VJPs, and forward-over-reverse Hessian-vector products.
