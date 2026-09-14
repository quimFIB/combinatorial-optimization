"""Tests for unit 30. Run with `uv run co test 30`. You should not need to edit this."""

import math
import random
from types import SimpleNamespace

import numpy as np
import pytest

from colib.testing import load_lab, time_limit

lab = load_lab(__file__)

DUAL_OPS = SimpleNamespace(sin=lambda x: lab.sin(x), exp=lambda x: lab.exp(x), log=lambda x: lab.log(x),
                           tanh=lambda x: lab.tanh(x))
VAR_OPS = SimpleNamespace(sin=lambda x: lab.vsin(x), exp=lambda x: lab.vexp(x), log=lambda x: lab.vlog(x),
                          tanh=lambda x: lab.vtanh(x))
FLOAT_OPS = SimpleNamespace(sin=math.sin, exp=math.exp, log=math.log, tanh=math.tanh)


def expression(v, S):
    """A fixed function of 3 inputs using every operation, written once for any number type."""
    x, y, z = v
    a = x * y + S.sin(z) - x / (y * y + 1.5)
    b = S.exp(a * 0.3) + (z - x) ** 3 - 2.0 / (1.0 + x * x)
    return S.tanh(b * 0.1) * S.log(x * x + 2.0) + a * b - 3.0 * z + (1.0 - y) * (4.0 - x)


def numeric_gradient(v, h=1e-6):
    grad = []
    for i in range(len(v)):
        up = list(v)
        dn = list(v)
        up[i] += h
        dn[i] -= h
        grad.append((expression(up, FLOAT_OPS) - expression(dn, FLOAT_OPS)) / (2 * h))
    return grad


# ---------------------------------------------------------------- step 1 ---

def test_step1_dual_arithmetic():
    x = lab.Dual(3.0, 1.0)
    assert (x * x).deriv == 6.0 and (x + 2).deriv == 1.0 and (2 + x).value == 5.0
    assert (5 - x).value == 2.0 and (5 - x).deriv == -1.0 and (-x).deriv == -1.0
    assert (1 / x).deriv == pytest.approx(-1 / 9) and (x / 2).deriv == 0.5
    assert (x ** 2.5).deriv == pytest.approx(2.5 * 3 ** 1.5)
    assert lab.exp(1.0) == pytest.approx(math.e) and isinstance(lab.sin(0.5), float)


@pytest.mark.parametrize("fn,df", [
    (lambda x: lab.sin(x) * lab.cos(x), lambda x: math.cos(2 * x)),
    (lambda x: lab.exp(lab.tanh(x)), lambda x: math.exp(math.tanh(x)) * (1 - math.tanh(x) ** 2)),
    (lambda x: lab.log(x * x + 1), lambda x: 2 * x / (x * x + 1)),
    (lambda x: x ** 3 / (1 + x), lambda x: (3 * x * x * (1 + x) - x ** 3) / (1 + x) ** 2),
])
def test_step1_derivative(fn, df):
    for x in (-1.3, 0.2, 0.7, 2.5):
        assert lab.derivative(fn, x) == pytest.approx(df(x), rel=1e-9, abs=1e-12)


@pytest.mark.parametrize("seed", range(5))
def test_step1_forward_gradient(seed):
    r = random.Random(seed)
    v = [r.uniform(0.5, 1.5) for _ in range(3)]
    grad, passes = lab.forward_gradient(lambda w: expression(w, DUAL_OPS), v)
    assert passes == 3
    assert grad == pytest.approx(numeric_gradient(v), rel=1e-5, abs=1e-6)


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(8))
def test_step2_reverse_matches_forward(seed):
    r = random.Random(seed)
    v = [r.uniform(0.5, 1.5) for _ in range(3)]
    value, grad = lab.reverse_gradient(lambda w: expression(w, VAR_OPS), v)
    forward, _ = lab.forward_gradient(lambda w: expression(w, DUAL_OPS), v)
    assert value == pytest.approx(expression(v, FLOAT_OPS))
    assert grad == pytest.approx(forward, rel=1e-12, abs=1e-12)


def test_step2_shared_subexpressions_accumulate():
    def f(v):
        x, = v
        y = x * x
        return y + y * 3 + y * y
    value, grad = lab.reverse_gradient(f, [2.0])
    assert value == 4 + 12 + 16 and grad == [4 * 2 * 2 + 4 * 2 ** 3]


def test_step2_each_node_once():
    def f(v):
        x, = v
        y = x * 1.0
        for _ in range(30):             # 2^30 paths from output to x, 33 nodes
            y = y + y
        return y
    with time_limit(5, "process each node once, in topological order, instead of every path"):
        value, grad = lab.reverse_gradient(f, [1.0])
    assert grad == [2.0 ** 30]


def test_step2_deep_graphs_do_not_recurse():
    def f(v):
        x, = v
        y = x
        for _ in range(20000):
            y = y * 1.0 + 0.0
        return y
    assert lab.reverse_gradient(f, [3.0])[1] == [1.0]


def test_step2_repeated_calls_start_from_zero():
    f = lambda v: v[0] * v[1]
    assert lab.reverse_gradient(f, [2.0, 5.0])[1] == [5.0, 2.0]
    x = lab.Var(2.0)
    y = x * x
    lab.backward(y)
    lab.backward(y)
    assert x.grad == 4.0, "backward resets gradients before sweeping"


def test_step2_relu_convention():
    for x0, g in ((1.5, 1.0), (-0.5, 0.0), (0.0, 0.0)):
        assert lab.reverse_gradient(lambda v: lab.vrelu(v[0]), [x0])[1] == [g]


@pytest.mark.parametrize("seed", range(5))
def test_step2_hessian_vector_products(seed):
    r = random.Random(seed)
    v = [r.uniform(0.5, 1.5) for _ in range(3)]
    d = [r.uniform(-1, 1) for _ in range(3)]
    hv = lab.hvp(lambda w: expression(w, VAR_OPS), v, d)
    h = 1e-5
    up = [a + h * b for a, b in zip(v, d)]
    dn = [a - h * b for a, b in zip(v, d)]
    gu = lab.reverse_gradient(lambda w: expression(w, VAR_OPS), up)[1]
    gd = lab.reverse_gradient(lambda w: expression(w, VAR_OPS), dn)[1]
    assert hv == pytest.approx([(a - b) / (2 * h) for a, b in zip(gu, gd)], rel=1e-4, abs=1e-6)


def test_step2_hvp_of_a_quadratic_is_exact():
    Q = [[2.0, 1.0, 0.0], [1.0, 3.0, -1.0], [0.0, -1.0, 4.0]]
    f = lambda w: sum(0.5 * Q[i][j] * w[i] * w[j] for i in range(3) for j in range(3))
    assert lab.hvp(f, [0.3, -0.2, 0.9], [1.0, 2.0, -1.0]) == pytest.approx([4.0, 8.0, -6.0])


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("op,shapes", [
    ("matmul", [(4, 3), (3, 2)]), ("add_bias", [(5, 3), (3,)]), ("tensor_tanh", [(3, 4)]), ("tensor_relu", [(4, 3)]),
])
def test_step3_gradient_check_ops(op, shapes):
    assert lab.check_op(getattr(lab, op), shapes, np.random.default_rng(1)) < 1e-6


def test_step3_check_op_catches_a_wrong_vjp():
    def wrong_tanh(a):
        t = np.tanh(a.value)
        return a._record(t, [(a, lambda g: g * (1 - t))], [t])
    assert lab.check_op(wrong_tanh, [(3, 3)], np.random.default_rng(2)) > 1e-3


def test_step3_mse_and_accumulation():
    rng = np.random.default_rng(3)
    tape = lab.Tape()
    P = lab.Tensor(rng.standard_normal((6, 1)), tape)
    target = rng.standard_normal((6, 1))
    loss = lab.mse(P, target)
    lab.tensor_backward(tape, loss)
    assert float(loss.value) == pytest.approx(np.mean((P.value - target) ** 2))
    assert np.allclose(P.grad, 2 * (P.value - target) / 6)
    tape = lab.Tape()
    X = lab.Tensor(rng.standard_normal((4, 3)), tape)
    W = lab.Tensor(rng.standard_normal((3, 3)), tape)
    h = lab.matmul(lab.matmul(X, W), W)                # W used twice
    total = h._record(np.array(h.value.sum()), [(h, lambda g: g * np.ones_like(h.value))], [])
    lab.tensor_backward(tape, total)
    ones = np.ones((4, 3))
    expected = (X.value.T @ ones @ W.value.T) + (X.value @ W.value).T @ ones
    assert np.allclose(W.grad, expected)


def test_step3_saved_bytes_counts_distinct_arrays():
    tape = lab.Tape()
    a = lab.Tensor(np.ones((10, 10)), tape)
    t = lab.tensor_tanh(a)                   # output and saved array are the same object
    assert tape.saved_bytes() == 800
    lab.tensor_relu(t)                       # output 800 + bool mask 100
    assert tape.saved_bytes() == 800 + 800 + 100


# ---------------------------------------------------------------- step 4 ---

def test_step4_init_shapes():
    params = lab.init_mlp([3, 50, 2], np.random.default_rng(0))
    assert [W.shape for W, _ in params] == [(3, 50), (50, 2)] and [b.shape for _, b in params] == [(50,), (2,)]
    assert np.all(params[0][1] == 0)
    assert abs(params[0][0].std() - 1 / math.sqrt(3)) < 0.1


@pytest.mark.parametrize("seed", range(3))
def test_step4_mlp_gradients_by_finite_differences(seed):
    rng = np.random.default_rng(seed)
    sizes = [2, 5, 4, 1]
    params = lab.init_mlp(sizes, rng)
    X = rng.standard_normal((7, 2))
    y = rng.standard_normal(7)
    loss, grads = lab.mlp_gradients(params, X, y)
    h = 1e-6
    for k, (W, b) in enumerate(params):
        for arr, g in ((W, grads[k][0]), (b, grads[k][1])):
            assert g.shape == arr.shape
            for idx in np.ndindex(arr.shape):
                old = arr[idx]
                arr[idx] = old + h
                up = lab.mlp_gradients(params, X, y)[0]
                arr[idx] = old - h
                dn = lab.mlp_gradients(params, X, y)[0]
                arr[idx] = old
                assert g[idx] == pytest.approx((up - dn) / (2 * h), rel=1e-4, abs=1e-7)


@pytest.mark.parametrize("sizes,batch", [([2, 16, 16, 1], 50), ([5, 3], 7), ([4, 8, 1], 1), ([10, 20, 30, 40, 2], 33)])
def test_step4_tape_bytes_predicted(sizes, batch):
    rng = np.random.default_rng(0)
    params = lab.init_mlp(sizes, rng)
    tape, _, _ = lab.mlp_loss(params, rng.standard_normal((batch, sizes[0])), rng.standard_normal(batch * sizes[-1]))
    assert lab.predicted_tape_bytes(sizes, batch) == tape.saved_bytes()


def test_step4_training_learns():
    rng = np.random.default_rng(4)
    X = rng.uniform(-2, 2, (400, 2))
    y = np.sin(X[:, 0]) * np.cos(X[:, 1])
    params = lab.init_mlp([2, 32, 32, 1], rng)
    before = [W.copy() for W, _ in params]
    new, history = lab.train(params, X, y, 60, 0.05, 20, np.random.default_rng(5))
    assert all(np.array_equal(W, B) for (W, _), B in zip(params, before)), "input params unchanged"
    assert len(history) == 60 and history[-1] < 0.25 * history[0]
    assert lab.mlp_gradients(new, X, y)[0] < 0.05


def test_step4_one_full_batch_step_is_exact():
    rng = np.random.default_rng(7)
    params = lab.init_mlp([3, 4, 1], rng)
    X, y = rng.standard_normal((9, 3)), rng.standard_normal(9)
    _, grads = lab.mlp_gradients(params, X, y)
    new, history = lab.train(params, X, y, 1, 0.1, 9, np.random.default_rng(0))
    for (W, b), (dW, db), (W1, b1) in zip(params, grads, new):
        assert np.allclose(W1, W - 0.1 * dW) and np.allclose(b1, b - 0.1 * db)
    assert history == pytest.approx([lab.mlp_gradients(params, X, y)[0]])
