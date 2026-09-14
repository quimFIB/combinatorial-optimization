"""Unit 30 lab — automatic differentiation.  REFERENCE SOLUTION, functional.

Dual numbers and graph nodes are immutable values: every operation returns a new one. The API still has two
places that are state by definition, and this version confines mutation to them. `backward` accumulates
gradients into one local dict (a fold written as a loop, because copying persistent structures would make
deep graphs quadratic), then writes node.grad because the API reads it there. The array tape is appended to
by the given Tensor._record, and tensor_backward folds gradients into a dict before assigning them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import reduce
from itertools import chain

import numpy as np
import toolz as tz


# ---------------------------------------------------------------- step 1 ---

@dataclass(frozen=True, eq=False)
class Dual:
    value: object
    deriv: object = 0.0

    def _o(self, other):
        return other if isinstance(other, Dual) else Dual(other, 0.0)

    def __add__(self, other):
        o = self._o(other)
        return Dual(self.value + o.value, self.deriv + o.deriv)

    __radd__ = __add__

    def __sub__(self, other):
        o = self._o(other)
        return Dual(self.value - o.value, self.deriv - o.deriv)

    def __rsub__(self, other):
        return self._o(other) - self

    def __mul__(self, other):
        o = self._o(other)
        return Dual(self.value * o.value, self.deriv * o.value + self.value * o.deriv)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = self._o(other)
        return Dual(self.value / o.value, (self.deriv * o.value - self.value * o.deriv) / (o.value * o.value))

    def __rtruediv__(self, other):
        return self._o(other) / self

    def __neg__(self):
        return Dual(-self.value, -self.deriv)

    def __pow__(self, p):
        return Dual(self.value ** p, p * self.value ** (p - 1) * self.deriv)

    def __gt__(self, other):
        return self.value > self._o(other).value

    def __lt__(self, other):
        return self.value < self._o(other).value


def _lift_unary(f, df):
    """A function on floats and Duals from f and its derivative, both written with these same functions."""
    def g(x):
        return Dual(g(x.value), df(x.value) * x.deriv) if isinstance(x, Dual) else f(x)
    return g


exp = _lift_unary(math.exp, lambda v: exp(v))
log = _lift_unary(math.log, lambda v: 1.0 / v)
sin = _lift_unary(math.sin, lambda v: cos(v))
cos = _lift_unary(math.cos, lambda v: -sin(v))
tanh = _lift_unary(math.tanh, lambda v: 1 - tanh(v) * tanh(v))


def derivative(f, x):
    return f(Dual(x, 1.0)).deriv


def forward_gradient(f, xs):
    seeds = [[Dual(x, float(j == i)) for j, x in enumerate(xs)] for i in range(len(xs))]
    return [f(s).deriv for s in seeds], len(xs)


# ---------------------------------------------------------------- step 2 ---

class Var:
    __slots__ = ("value", "parents", "grad")

    def __init__(self, value, parents=()):
        self.value, self.parents, self.grad = value, tuple(parents), 0.0

    @staticmethod
    def _o(x):
        return x if isinstance(x, Var) else Var(x)

    def __add__(self, other):
        o = Var._o(other)
        return Var(self.value + o.value, ((self, 1.0), (o, 1.0)))

    __radd__ = __add__

    def __sub__(self, other):
        o = Var._o(other)
        return Var(self.value - o.value, ((self, 1.0), (o, -1.0)))

    def __rsub__(self, other):
        return Var._o(other) - self

    def __mul__(self, other):
        o = Var._o(other)
        return Var(self.value * o.value, ((self, o.value), (o, self.value)))

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = Var._o(other)
        return Var(self.value / o.value, ((self, 1.0 / o.value), (o, -self.value / (o.value * o.value))))

    def __rtruediv__(self, other):
        return Var._o(other) / self

    def __neg__(self):
        return Var(-self.value, ((self, -1.0),))

    def __pow__(self, p):
        return Var(self.value ** p, ((self, p * self.value ** (p - 1)),))


def vexp(x):
    return (lambda e: Var(e, ((x, e),)))(exp(x.value))


def vlog(x):
    return Var(log(x.value), ((x, 1.0 / x.value),))


def vsin(x):
    return Var(sin(x.value), ((x, cos(x.value)),))


def vtanh(x):
    return (lambda t: Var(t, ((x, 1 - t * t),)))(tanh(x.value))


def vrelu(x):
    positive = x.value > 0
    return Var(x.value if positive else 0.0 * x.value, ((x, 1.0 if positive else 0.0),))


def _topological(output):
    """Post-order DFS. The stack and the seen-set are local mutable state: persistent tuples would make a
    20 000-node graph quadratic, which the tests rule out."""
    order, seen, stack = [], set(), [(output, False)]
    while stack:
        node, done = stack.pop()
        if done:
            order.append(node)
        elif id(node) not in seen:
            seen.add(id(node))
            stack.append((node, True))
            stack.extend((p, False) for p, _ in node.parents if id(p) not in seen)
    return order


def backward(output):
    order = _topological(output)
    grads = {id(output): 1.0}
    for node in reversed(order):        # a fold over the reversed order, accumulating into one local dict
        g = grads.get(id(node), 0.0)
        for parent, local in node.parents:
            grads[id(parent)] = grads.get(id(parent), 0.0) + g * local
    for node in order:                  # the API reads gradients from the nodes
        node.grad = grads.get(id(node), 0.0)
    return order


def reverse_gradient(f, xs):
    inputs = [Var(x) for x in xs]
    out = f(inputs)
    backward(out)
    return out.value, [v.grad for v in inputs]


def hvp(f, xs, vs):
    _, grads = reverse_gradient(f, [Dual(x, v) for x, v in zip(xs, vs)])
    return [g.deriv if isinstance(g, Dual) else 0.0 for g in grads]


# ---------------------------------------------------------------- step 3 ---

class Tape:
    def __init__(self):
        self.entries = []

    def saved_bytes(self):
        arrays = {id(a): a for out, _, saved in self.entries for a in chain([out.value], saved)}
        return sum(a.nbytes for a in arrays.values())


class Tensor:
    def __init__(self, value, tape=None):
        self.value, self.tape, self.grad = np.asarray(value, float), tape, None

    def _record(self, value, inputs, saved):
        out = Tensor(value, self.tape)
        self.tape.entries.append((out, inputs, saved))
        return out


def matmul(a, b):
    return a._record(a.value @ b.value, [(a, lambda g: g @ b.value.T), (b, lambda g: a.value.T @ g)], [a.value, b.value])


def add_bias(a, b):
    return a._record(a.value + b.value, [(a, lambda g: g), (b, lambda g: g.sum(axis=0))], [])


def tensor_tanh(a):
    t = np.tanh(a.value)
    return a._record(t, [(a, lambda g: g * (1 - t * t))], [t])


def tensor_relu(a):
    mask = a.value > 0
    return a._record(a.value * mask, [(a, lambda g: g * mask)], [mask])


def mse(pred, target):
    diff = pred.value - target
    return pred._record(np.array(np.mean(diff * diff)), [(pred, lambda g: g * 2 * diff / diff.size)], [diff])


def tensor_backward(tape, output):
    def push(grads, entry):
        out, inputs, _ = entry
        g = grads.get(id(out))
        if g is None:
            return grads
        return reduce(lambda acc, iv: tz.assoc(acc, id(iv[0]), iv[1](g) if acc.get(id(iv[0])) is None
                                               else acc[id(iv[0])] + iv[1](g)), inputs, grads)

    grads = reduce(push, reversed(tape.entries), {id(output): np.ones_like(output.value)})
    tensors = {id(t): t for out, inputs, _ in tape.entries for t in chain([out], (i for i, _ in inputs))}
    for key, tensor in tensors.items():
        tensor.grad = grads.get(key)


def check_op(op, shapes, rng, h=1e-6):
    arrays = [rng.standard_normal(s) for s in shapes]
    tape = Tape()
    inputs = [Tensor(a, tape) for a in arrays]
    out = op(*inputs)
    W = rng.standard_normal(out.value.shape)
    weighted = out._record(np.array(np.sum(out.value * W)), [(out, lambda g: g * W)], [])
    tensor_backward(tape, weighted)
    loss = lambda arrs: float(np.sum(op(*[Tensor(a, Tape()) for a in arrs]).value * W))

    def bumped(k, idx, delta):
        unit = np.zeros(arrays[k].shape)
        unit[idx] = delta
        return [x + unit if j == k else x for j, x in enumerate(arrays)]

    diffs = [abs((loss(bumped(k, idx, h)) - loss(bumped(k, idx, -h))) / (2 * h)
                 - (0.0 if inputs[k].grad is None else inputs[k].grad[idx]))
             for k, a in enumerate(arrays) for idx in np.ndindex(a.shape)]
    return max(diffs, default=0.0)


# ---------------------------------------------------------------- step 4 ---

def init_mlp(sizes, rng):
    return [(rng.standard_normal((m, n)) / math.sqrt(m), np.zeros(n)) for m, n in zip(sizes, sizes[1:])]


def mlp_loss(params, X, y):
    tape = Tape()
    leaves = [(Tensor(W, tape), Tensor(b, tape)) for W, b in params]

    def layer(h, k_leaf):
        k, (Wt, bt) = k_leaf
        z = add_bias(matmul(h, Wt), bt)
        return tensor_tanh(z) if k < len(params) - 1 else z

    out = reduce(layer, enumerate(leaves), Tensor(X, tape))
    return tape, mse(out, y.reshape(out.value.shape)), leaves


def mlp_gradients(params, X, y):
    tape, loss, leaves = mlp_loss(params, X, y)
    tensor_backward(tape, loss)
    return float(loss.value), [(W.grad, b.grad) for W, b in leaves]


def predicted_tape_bytes(sizes, batch):
    layers = list(zip(sizes, sizes[1:]))
    per_layer = sum(m * n + 2 * batch * n + (batch * n if k < len(layers) - 1 else 0) for k, (m, n) in enumerate(layers))
    return 8 * (batch * sizes[0] + per_layer + batch * sizes[-1] + 1)


def train(params, X, y, epochs, lr, batch, rng):
    def step(params, idx):
        _, grads = mlp_gradients(params, X[idx], y[idx])
        return [(W - lr * dW, b - lr * db) for (W, b), (dW, db) in zip(params, grads)]

    def epoch(state, _):
        params, history = state
        order = rng.permutation(len(X))
        batches = [order[s:s + batch] for s in range(0, len(X), batch)]
        losses = [mlp_gradients(p, X[idx], y[idx])[0]
                  for p, idx in zip(tz.accumulate(step, batches, params), batches)]
        return reduce(step, batches, params), history + [float(np.mean(losses))]

    return reduce(epoch, range(epochs), (list(params), []))
