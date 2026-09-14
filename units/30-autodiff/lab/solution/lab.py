"""Unit 30 lab — automatic differentiation.  REFERENCE SOLUTION, imperative.

Three engines. Dual numbers carry a value and a derivative forward (forward mode). A scalar tape records
every operation on Var nodes and sweeps it backwards (reverse mode). An array tape does the same for numpy
arrays, which is what makes training an MLP practical. The scalar tape is written so that its values can
themselves be Dual numbers: running reverse mode on dual inputs gives Hessian-vector products.
"""

from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------- step 1 ---

class Dual:
    """a + b ε with ε² = 0. `value` is a, `deriv` is b."""

    def __init__(self, value, deriv=0.0):
        self.value, self.deriv = value, deriv

    @staticmethod
    def lift(x):
        return x if isinstance(x, Dual) else Dual(x, 0.0)

    def __add__(self, other):
        o = Dual.lift(other)
        return Dual(self.value + o.value, self.deriv + o.deriv)

    __radd__ = __add__

    def __sub__(self, other):
        o = Dual.lift(other)
        return Dual(self.value - o.value, self.deriv - o.deriv)

    def __rsub__(self, other):
        return Dual.lift(other) - self

    def __mul__(self, other):
        o = Dual.lift(other)
        return Dual(self.value * o.value, self.deriv * o.value + self.value * o.deriv)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = Dual.lift(other)
        return Dual(self.value / o.value, (self.deriv * o.value - self.value * o.deriv) / (o.value * o.value))

    def __rtruediv__(self, other):
        return Dual.lift(other) / self

    def __neg__(self):
        return Dual(-self.value, -self.deriv)

    def __pow__(self, p):
        """Constant real exponent p."""
        return Dual(self.value ** p, p * self.value ** (p - 1) * self.deriv)

    def __gt__(self, other):
        return self.value > Dual.lift(other).value

    def __lt__(self, other):
        return self.value < Dual.lift(other).value


def exp(x):
    """exp for floats and Duals."""
    if isinstance(x, Dual):
        e = exp(x.value)
        return Dual(e, e * x.deriv)
    return math.exp(x)


def log(x):
    if isinstance(x, Dual):
        return Dual(log(x.value), x.deriv / x.value)
    return math.log(x)


def sin(x):
    if isinstance(x, Dual):
        return Dual(sin(x.value), cos(x.value) * x.deriv)
    return math.sin(x)


def cos(x):
    if isinstance(x, Dual):
        return Dual(cos(x.value), -sin(x.value) * x.deriv)
    return math.cos(x)


def tanh(x):
    if isinstance(x, Dual):
        t = tanh(x.value)
        return Dual(t, (1 - t * t) * x.deriv)
    return math.tanh(x)


def derivative(f, x):
    """f'(x) for f: R -> R, by one forward pass on Dual(x, 1)."""
    return f(Dual(x, 1.0)).deriv


def forward_gradient(f, xs):
    """The gradient of f: R^n -> R by n forward passes, one per coordinate. f takes a list of numbers.
    Returns (gradient list, number of passes)."""
    grad = []
    for i in range(len(xs)):
        grad.append(f([Dual(x, 1.0 if j == i else 0.0) for j, x in enumerate(xs)]).deriv)
    return grad, len(xs)


# ---------------------------------------------------------------- step 2 ---

class Var:
    """A node in a scalar computation graph. `parents` is a list of (node, local derivative) pairs; `grad` is
    filled in by backward. Values may be floats or Duals, so local derivatives are computed with the step 1
    functions."""

    def __init__(self, value, parents=()):
        self.value, self.parents, self.grad = value, list(parents), 0.0

    @staticmethod
    def lift(x):
        return x if isinstance(x, Var) else Var(x)

    def __add__(self, other):
        o = Var.lift(other)
        return Var(self.value + o.value, [(self, 1.0), (o, 1.0)])

    __radd__ = __add__

    def __sub__(self, other):
        o = Var.lift(other)
        return Var(self.value - o.value, [(self, 1.0), (o, -1.0)])

    def __rsub__(self, other):
        return Var.lift(other) - self

    def __mul__(self, other):
        o = Var.lift(other)
        return Var(self.value * o.value, [(self, o.value), (o, self.value)])

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = Var.lift(other)
        return Var(self.value / o.value, [(self, 1.0 / o.value), (o, -self.value / (o.value * o.value))])

    def __rtruediv__(self, other):
        return Var.lift(other) / self

    def __neg__(self):
        return Var(-self.value, [(self, -1.0)])

    def __pow__(self, p):
        return Var(self.value ** p, [(self, p * self.value ** (p - 1))])


def vexp(x):
    e = exp(x.value)
    return Var(e, [(x, e)])


def vlog(x):
    return Var(log(x.value), [(x, 1.0 / x.value)])


def vsin(x):
    return Var(sin(x.value), [(x, cos(x.value))])


def vtanh(x):
    t = tanh(x.value)
    return Var(t, [(x, 1 - t * t)])


def vrelu(x):
    """max(x, 0), with derivative 0 at x = 0 (jax.nn.relu's convention; jnp.maximum(x, 0) gives 0.5 there)."""
    return Var(x.value if x.value > 0 else 0.0 * x.value, [(x, 1.0 if x.value > 0 else 0.0)])


def backward(output):
    """Reverse sweep: order the graph topologically (iterative DFS from output), set output.grad = 1, then for
    each node in reverse topological order add grad * local to each parent's grad. Each node is processed
    once, however many paths reach it."""
    order, seen, stack = [], set(), [(output, False)]
    while stack:
        node, done = stack.pop()
        if done:
            order.append(node)
            continue
        if id(node) in seen:
            continue
        seen.add(id(node))
        stack.append((node, True))
        for parent, _ in node.parents:
            if id(parent) not in seen:
                stack.append((parent, False))
    for node in order:
        node.grad = 0.0
    output.grad = 1.0
    for node in reversed(order):
        for parent, local in node.parents:
            parent.grad = parent.grad + node.grad * local
    return order


def reverse_gradient(f, xs):
    """(f(xs), gradient list) with one forward evaluation on Vars and one backward sweep."""
    inputs = [Var(x) for x in xs]
    out = f(inputs)
    backward(out)
    return out.value, [v.grad for v in inputs]


def hvp(f, xs, vs):
    """Hessian-vector product H(xs) v by forward-over-reverse: run reverse_gradient on inputs Dual(x_i, v_i);
    the derivative parts of the gradient are H v."""
    _, grads = reverse_gradient(f, [Dual(x, v) for x, v in zip(xs, vs)])
    return [g.deriv if isinstance(g, Dual) else 0.0 for g in grads]


# ---------------------------------------------------------------- step 3 ---

class Tape:
    """Records array operations. Each entry is (output Tensor, list of (input Tensor, vjp function), list of the
    arrays the vjps keep alive), where vjp maps the output's gradient to that input's gradient contribution."""

    def __init__(self):
        self.entries = []

    def saved_bytes(self):
        """Memory the tape holds for the backward pass: the nbytes of every distinct array (by identity) that is
        a recorded output value or in some entry's saved list."""
        arrays = {}
        for out, _, saved in self.entries:
            for a in [out.value, *saved]:
                arrays[id(a)] = a
        return sum(a.nbytes for a in arrays.values())


class Tensor:
    def __init__(self, value, tape=None):
        self.value, self.tape, self.grad = np.asarray(value, float), tape, None

    def _record(self, value, inputs, saved):
        out = Tensor(value, self.tape)
        self.tape.entries.append((out, inputs, saved))
        return out


def matmul(a, b):
    """(batch, m) @ (m, n). Its vjps need both inputs."""
    return a._record(a.value @ b.value, [(a, lambda g: g @ b.value.T), (b, lambda g: a.value.T @ g)],
                     [a.value, b.value])


def add_bias(a, b):
    """a (batch, k) + b (k,) broadcast over rows. Its vjps need nothing but the incoming gradient."""
    return a._record(a.value + b.value, [(a, lambda g: g), (b, lambda g: g.sum(axis=0))], [])


def tensor_tanh(a):
    """Elementwise tanh; the vjp reuses the output itself."""
    t = np.tanh(a.value)
    return a._record(t, [(a, lambda g: g * (1 - t * t))], [t])


def tensor_relu(a):
    """Elementwise max(x, 0), derivative 0 at 0; the vjp keeps a boolean mask."""
    mask = a.value > 0
    return a._record(a.value * mask, [(a, lambda g: g * mask)], [mask])


def mse(pred, target):
    """mean((pred - target)^2) over all entries; target is a numpy array (not differentiated). Keeps the
    difference array."""
    diff = pred.value - target
    return pred._record(np.array(np.mean(diff * diff)), [(pred, lambda g: g * 2 * diff / diff.size)], [diff])


def tensor_backward(tape, output):
    """Seed output.grad with ones and apply the recorded vjps in reverse order, accumulating input grads."""
    for out, _, _ in tape.entries:
        out.grad = None
    output.grad = np.ones_like(output.value)
    for out, inputs, _ in reversed(tape.entries):
        if out.grad is None:
            continue
        for tensor, vjp in inputs:
            contribution = vjp(out.grad)
            tensor.grad = contribution if tensor.grad is None else tensor.grad + contribution


def check_op(op, shapes, rng, h=1e-6):
    """Gradient-check an array op: random inputs of the given shapes, loss = sum(op(inputs) * W) for a random W,
    tape gradients against central differences. Returns the largest absolute difference."""
    arrays = [rng.standard_normal(s) for s in shapes]
    tape = Tape()
    inputs = [Tensor(a, tape) for a in arrays]
    out = op(*inputs)
    W = rng.standard_normal(out.value.shape)
    loss_value = lambda arrs: float(np.sum(op(*[Tensor(a, Tape()) for a in arrs]).value * W))
    weighted = out._record(np.array(np.sum(out.value * W)), [(out, lambda g: g * W)], [])
    tensor_backward(tape, weighted)
    worst = 0.0
    for k, a in enumerate(arrays):
        for idx in np.ndindex(a.shape):
            plus = [x.copy() for x in arrays]
            minus = [x.copy() for x in arrays]
            plus[k][idx] += h
            minus[k][idx] -= h
            numeric = (loss_value(plus) - loss_value(minus)) / (2 * h)
            analytic = 0.0 if inputs[k].grad is None else inputs[k].grad[idx]
            worst = max(worst, abs(numeric - analytic))
    return worst


# ---------------------------------------------------------------- step 4 ---

def init_mlp(sizes, rng):
    """For consecutive sizes (m, n): W of shape (m, n) drawn from N(0, 1/m) with rng.standard_normal, and a zero
    bias of shape (n,). Returns a list of (W, b) numpy pairs."""
    return [(rng.standard_normal((m, n)) / math.sqrt(m), np.zeros(n)) for m, n in zip(sizes, sizes[1:])]


def mlp_loss(params, X, y):
    """Build the tape for mean-squared error of the MLP x -> tanh(x W1 + b1) -> ... -> x W_L + b_L (no
    activation on the last layer). Returns (tape, loss Tensor, list of (W Tensor, b Tensor))."""
    tape = Tape()
    h = Tensor(X, tape)
    leaves = []
    for k, (W, b) in enumerate(params):
        Wt, bt = Tensor(W, tape), Tensor(b, tape)
        leaves.append((Wt, bt))
        h = add_bias(matmul(h, Wt), bt)
        if k < len(params) - 1:
            h = tensor_tanh(h)
    return tape, mse(h, y.reshape(h.value.shape)), leaves


def mlp_gradients(params, X, y):
    """(loss value, list of (dW, db)) by one forward and one backward pass."""
    tape, loss, leaves = mlp_loss(params, X, y)
    tensor_backward(tape, loss)
    return float(loss.value), [(W.grad, b.grad) for W, b in leaves]


def predicted_tape_bytes(sizes, batch):
    """The tape's saved_bytes for mlp_loss on a float64 batch, from sizes alone. Distinct arrays: the input batch
    (batch x sizes[0]); for each layer its weights (m x n), matmul output and bias-add output (batch x n each),
    plus the tanh output on hidden layers; then the loss's difference array (batch x sizes[-1]) and the scalar
    loss. The matmul's saved input is the previous layer's tanh output, already counted. 8 bytes per number."""
    numbers = batch * sizes[0]
    for k, (m, n) in enumerate(zip(sizes, sizes[1:])):
        hidden = k < len(sizes) - 2
        numbers += m * n + 2 * batch * n + (batch * n if hidden else 0)
    numbers += batch * sizes[-1] + 1
    return 8 * numbers


def train(params, X, y, epochs, lr, batch, rng):
    """Mini-batch SGD: each epoch, a permutation from rng.permutation, batches in order, params -= lr * grad.
    Returns (new params, list of per-epoch mean batch losses). The input params are not modified."""
    params = [(W.copy(), b.copy()) for W, b in params]
    history = []
    n = len(X)
    for _ in range(epochs):
        order = rng.permutation(n)
        losses = []
        for start in range(0, n, batch):
            idx = order[start:start + batch]
            loss, grads = mlp_gradients(params, X[idx], y[idx])
            params = [(W - lr * dW, b - lr * db) for (W, b), (dW, db) in zip(params, grads)]
            losses.append(loss)
        history.append(float(np.mean(losses)))
    return params, history
