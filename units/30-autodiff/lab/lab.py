"""Unit 30 lab — automatic differentiation.

Fill in the functions and methods marked TODO, one step at a time, and run
    uv run co test 30
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Three engines. Dual numbers carry a value and a derivative forward (forward mode). A scalar tape records
every operation on Var nodes and sweeps it backwards (reverse mode). An array tape does the same for numpy
arrays, which is what makes training an MLP practical. Write the scalar tape so that its values may
themselves be Dual numbers: running reverse mode on dual inputs then gives Hessian-vector products.
"""

from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------- step 1 ---

class Dual:
    """a + b ε with ε² = 0. `value` is a, `deriv` is b. Arithmetic with plain numbers must work on both sides
    (2 * x, x / 3, 1 - x), and ** takes a constant real exponent. Define __gt__ and __lt__ on values, so
    code that branches (like relu) runs on Duals."""

    def __init__(self, value, deriv=0.0):
        self.value, self.deriv = value, deriv

    def __add__(self, other):
        raise NotImplementedError  # TODO step 1

    def __radd__(self, other):
        raise NotImplementedError  # TODO step 1

    def __sub__(self, other):
        raise NotImplementedError  # TODO step 1

    def __rsub__(self, other):
        raise NotImplementedError  # TODO step 1

    def __mul__(self, other):
        raise NotImplementedError  # TODO step 1

    def __rmul__(self, other):
        raise NotImplementedError  # TODO step 1

    def __truediv__(self, other):
        raise NotImplementedError  # TODO step 1

    def __rtruediv__(self, other):
        raise NotImplementedError  # TODO step 1

    def __neg__(self):
        raise NotImplementedError  # TODO step 1

    def __pow__(self, p):
        raise NotImplementedError  # TODO step 1

    def __gt__(self, other):
        raise NotImplementedError  # TODO step 1

    def __lt__(self, other):
        raise NotImplementedError  # TODO step 1


def exp(x):
    """exp for floats (returning a float) and Duals (returning a Dual)."""
    raise NotImplementedError  # TODO step 1


def log(x):
    """Natural log for floats and Duals."""
    raise NotImplementedError  # TODO step 1


def sin(x):
    """sin for floats and Duals."""
    raise NotImplementedError  # TODO step 1


def cos(x):
    """cos for floats and Duals."""
    raise NotImplementedError  # TODO step 1


def tanh(x):
    """tanh for floats and Duals."""
    raise NotImplementedError  # TODO step 1


def derivative(f, x):
    """f'(x) for f: R -> R, by one forward pass on Dual(x, 1)."""
    raise NotImplementedError  # TODO step 1


def forward_gradient(f, xs):
    """The gradient of f: R^n -> R by n forward passes, one per coordinate. f takes a list of numbers.
    Returns (gradient list, number of passes)."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

class Var:
    """A node in a scalar computation graph. `parents` is a list of (node, local derivative) pairs; `grad` is
    filled in by backward. Values may be floats or Duals, so compute local derivatives with arithmetic and the
    step 1 functions, never with math.* directly. Arithmetic with plain numbers works on both sides."""

    def __init__(self, value, parents=()):
        self.value, self.parents, self.grad = value, list(parents), 0.0

    def __add__(self, other):
        raise NotImplementedError  # TODO step 2

    def __radd__(self, other):
        raise NotImplementedError  # TODO step 2

    def __sub__(self, other):
        raise NotImplementedError  # TODO step 2

    def __rsub__(self, other):
        raise NotImplementedError  # TODO step 2

    def __mul__(self, other):
        raise NotImplementedError  # TODO step 2

    def __rmul__(self, other):
        raise NotImplementedError  # TODO step 2

    def __truediv__(self, other):
        raise NotImplementedError  # TODO step 2

    def __rtruediv__(self, other):
        raise NotImplementedError  # TODO step 2

    def __neg__(self):
        raise NotImplementedError  # TODO step 2

    def __pow__(self, p):
        raise NotImplementedError  # TODO step 2


def vexp(x):
    """exp of a Var, recording its local derivative."""
    raise NotImplementedError  # TODO step 2


def vlog(x):
    raise NotImplementedError  # TODO step 2


def vsin(x):
    raise NotImplementedError  # TODO step 2


def vtanh(x):
    raise NotImplementedError  # TODO step 2


def vrelu(x):
    """max(x, 0), with derivative 0 at x = 0 (jax.nn.relu's convention; jnp.maximum(x, 0) gives 0.5 there)."""
    raise NotImplementedError  # TODO step 2


def backward(output):
    """Reverse sweep: order the graph topologically (iteratively: graphs can be 20 000 nodes deep), reset every
    node's grad to 0, set output.grad = 1, then for each node in reverse topological order add grad * local to
    each parent's grad. Each node is processed once, however many paths reach it. Returns the order."""
    raise NotImplementedError  # TODO step 2


def reverse_gradient(f, xs):
    """(f(xs), gradient list) with one forward evaluation on Vars and one backward sweep."""
    raise NotImplementedError  # TODO step 2


def hvp(f, xs, vs):
    """Hessian-vector product H(xs) v by forward-over-reverse: run reverse_gradient on inputs Dual(x_i, v_i);
    the derivative parts of the gradient are H v."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

class Tape:
    """Records array operations. Each entry is (output Tensor, list of (input Tensor, vjp function), list of the
    arrays the vjps keep alive), where vjp maps the output's gradient to that input's gradient contribution."""

    def __init__(self):
        self.entries = []

    def saved_bytes(self):
        """Memory the tape holds for the backward pass: the nbytes of every distinct array (by identity) that is
        a recorded output value or in some entry's saved list."""
        raise NotImplementedError  # TODO step 3


class Tensor:
    """Given. A numpy value on a tape; _record appends an entry and returns the new output Tensor."""

    def __init__(self, value, tape=None):
        self.value, self.tape, self.grad = np.asarray(value, float), tape, None

    def _record(self, value, inputs, saved):
        out = Tensor(value, self.tape)
        self.tape.entries.append((out, inputs, saved))
        return out


def matmul(a, b):
    """(batch, m) @ (m, n). Its vjps need both inputs: save a.value and b.value."""
    raise NotImplementedError  # TODO step 3


def add_bias(a, b):
    """a (batch, k) + b (k,) broadcast over rows. Its vjps need nothing but the incoming gradient."""
    raise NotImplementedError  # TODO step 3


def tensor_tanh(a):
    """Elementwise tanh; the vjp reuses the output itself (save the output array, the same object)."""
    raise NotImplementedError  # TODO step 3


def tensor_relu(a):
    """Elementwise max(x, 0), derivative 0 at 0; the vjp keeps a boolean mask (save it)."""
    raise NotImplementedError  # TODO step 3


def mse(pred, target):
    """mean((pred - target)^2) over all entries; target is a numpy array (not differentiated). Keeps the
    difference array (save it)."""
    raise NotImplementedError  # TODO step 3


def tensor_backward(tape, output):
    """Seed output.grad with ones and apply the recorded vjps in reverse order, accumulating input grads.
    Reset the recorded outputs' grads first."""
    raise NotImplementedError  # TODO step 3


def check_op(op, shapes, rng, h=1e-6):
    """Gradient-check an array op: random inputs of the given shapes (rng.standard_normal), loss =
    sum(op(inputs) * W) for a random W of the output's shape, tape gradients against central differences.
    Returns the largest absolute difference."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def init_mlp(sizes, rng):
    """For consecutive sizes (m, n): W of shape (m, n) drawn from N(0, 1/m) with rng.standard_normal, and a zero
    bias of shape (n,). Returns a list of (W, b) numpy pairs."""
    raise NotImplementedError  # TODO step 4


def mlp_loss(params, X, y):
    """Build the tape for mean-squared error of the MLP x -> tanh(x W1 + b1) -> ... -> x W_L + b_L (no
    activation on the last layer). Returns (tape, loss Tensor, list of (W Tensor, b Tensor))."""
    raise NotImplementedError  # TODO step 4


def mlp_gradients(params, X, y):
    """(loss value, list of (dW, db)) by one forward and one backward pass."""
    raise NotImplementedError  # TODO step 4


def predicted_tape_bytes(sizes, batch):
    """The tape's saved_bytes for mlp_loss on a float64 batch, from sizes alone, before running anything."""
    raise NotImplementedError  # TODO step 4


def train(params, X, y, epochs, lr, batch, rng):
    """Mini-batch SGD: each epoch, a permutation from rng.permutation, batches in order, params -= lr * grad.
    Returns (new params, list of per-epoch mean batch losses). The input params are not modified."""
    raise NotImplementedError  # TODO step 4
