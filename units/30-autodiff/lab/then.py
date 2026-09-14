"""Unit 30 — "Then": your autodiff against JAX, the cost of forward and reverse mode, an MLP on real data,
and where autodiff lies.

  1. Agreement: gradients, a Jacobian, and Hessian-vector products against jax.grad, jax.jacfwd/jacrev and
     jax.hessian, to 1e-6.
  2. Cost: forward mode needs one pass per input, reverse mode one backward sweep, as n grows.
  3. Real data: matplotlib's bundled Jacksboro fault elevation model (344 x 403 grid, metres). Your MLP
     learns elevation from (x, y) on 6 000 points and is tested on 6 000 others; the tape size is predicted
     before running; the same network and training loop in JAX, timed.
  4. Where autodiff lies: relu and abs at 0, sqrt(x^2) at 0, a branch, argmax.

    uv run co then 30
"""

import math
import random
import time

import jax
import jax.numpy as jnp
import numpy as np
from matplotlib import cbook

from colib.testing import load_lab

jax.config.update("jax_enable_x64", True)
lab = load_lab(__file__)


def timed(f, *a):
    t = time.perf_counter()
    out = f(*a)
    return out, time.perf_counter() - t


def expression_generic(x, y, z, sin, exp, log, tanh):
    a = x * y + sin(z) - x / (y * y + 1.5)
    b = exp(a * 0.3) + (z - x) ** 3 - 2.0 / (1.0 + x * x)
    return tanh(b * 0.1) * log(x * x + 2.0) + a * b - 3.0 * z + (1.0 - y) * (4.0 - x)


def agreement():
    print("1. Agreement with JAX (float64), largest absolute difference over 20 random points\n")
    ours_ops = dict(sin=lab.vsin, exp=lab.vexp, log=lab.vlog, tanh=lab.vtanh)
    jax_ops = dict(sin=jnp.sin, exp=jnp.exp, log=jnp.log, tanh=jnp.tanh)
    f_ours = lambda v: expression_generic(*v, **ours_ops)
    f_jax = lambda v: expression_generic(v[0], v[1], v[2], **jax_ops)
    g_jax = jax.grad(f_jax)
    h_jax = jax.hessian(f_jax)
    r = random.Random(0)
    worst_g = worst_h = worst_j = 0.0
    for _ in range(20):
        v = [r.uniform(0.5, 1.5) for _ in range(3)]
        d = [r.uniform(-1, 1) for _ in range(3)]
        _, g = lab.reverse_gradient(f_ours, v)
        worst_g = max(worst_g, float(np.max(np.abs(np.array(g) - np.array(g_jax(jnp.array(v)))))))
        hv = lab.hvp(f_ours, v, d)
        worst_h = max(worst_h, float(np.max(np.abs(np.array(hv) - np.array(h_jax(jnp.array(v)) @ jnp.array(d))))))
        # a vector function R^3 -> R^2: rows of the Jacobian by forward mode against jacfwd and jacrev
        F_dual = [lambda w: w[0] * lab.sin(w[1]) + w[2] * w[2], lambda w: lab.exp(w[0] * w[2]) - w[1] / (1 + w[0] * w[0])]
        F_jax = lambda w: jnp.array([w[0] * jnp.sin(w[1]) + w[2] * w[2], jnp.exp(w[0] * w[2]) - w[1] / (1 + w[0] * w[0])])
        J_ours = np.array([lab.forward_gradient(Fi, v)[0] for Fi in F_dual])
        for J in (jax.jacfwd(F_jax)(jnp.array(v)), jax.jacrev(F_jax)(jnp.array(v))):
            worst_j = max(worst_j, float(np.max(np.abs(J_ours - np.array(J)))))
    print(f"  gradient (reverse mode) vs jax.grad:        {worst_g:.1e}")
    print(f"  Jacobian (forward mode) vs jacfwd, jacrev:  {worst_j:.1e}")
    print(f"  Hessian-vector product vs jax.hessian @ v:  {worst_h:.1e}")


def cost():
    print("\n2. Cost of a gradient of f(x) = sum_i sin(x_i) x_{i+1}: seconds (passes)\n")
    print(f"  {'n':>6} {'forward mode':>18} {'reverse mode':>14} {'jax.grad (jit, 2nd call)':>26}")
    for n in (10, 100, 1000):
        xs = [random.Random(n).uniform(-1, 1) for _ in range(n)]
        f_dual = lambda v: sum((lab.sin(v[i]) * v[i + 1] for i in range(len(v) - 1)), 0.0)
        f_var = lambda v: sum((lab.vsin(v[i]) * v[i + 1] for i in range(len(v) - 1)), lab.Var(0.0))
        (gf, passes), tf = timed(lab.forward_gradient, f_dual, xs)
        (_, gr), tr = timed(lab.reverse_gradient, f_var, xs)
        assert np.allclose(gf, gr)
        gj = jax.jit(jax.grad(lambda v: jnp.sum(jnp.sin(v[:-1]) * v[1:])))
        gj(jnp.array(xs))
        _, tj = timed(lambda: np.array(gj(jnp.array(xs))))
        print(f"  {n:>6} {tf:>11.3f} ({passes:>4}) {tr:>10.4f} (1) {tj:>18.5f}")


def dem_data(rng):
    dem = cbook.get_sample_data("jacksboro_fault_dem.npz")
    z = dem["elevation"].astype(float)
    rows, cols = np.indices(z.shape)
    coords = np.stack([rows.ravel() / (z.shape[0] - 1) * 2 - 1, cols.ravel() / (z.shape[1] - 1) * 2 - 1], axis=1)
    order = rng.permutation(z.size)
    train, test = order[:6000], order[6000:12000]
    mean, std = z.mean(), z.std()
    y = (z.ravel() - mean) / std
    return coords[train], y[train], coords[test], y[test], std, z.shape


def real_data():
    print("\n3. An MLP on real data: elevation of the Jacksboro fault region (matplotlib sample data)\n")
    rng = np.random.default_rng(0)
    Xtr, ytr, Xte, yte, std, shape = dem_data(rng)
    sizes, batch, epochs, lr = [2, 64, 64, 1], 64, 60, 0.05
    print(f"  grid {shape[0]} x {shape[1]}, elevation std {std:.1f} m; train 6 000 points, test 6 000; MLP {sizes},"
          f" batch {batch}, {epochs} epochs, SGD lr {lr}")
    params = lab.init_mlp(sizes, rng)
    predicted = lab.predicted_tape_bytes(sizes, batch)
    tape, _, _ = lab.mlp_loss(params, Xtr[:batch], ytr[:batch])
    print(f"  tape memory per batch: predicted {predicted} bytes, measured {tape.saved_bytes()} bytes")
    trained, tr_ours = timed(lab.train, params, Xtr, ytr, epochs, lr, batch, np.random.default_rng(1))
    new, history = trained
    rmse = lambda p, X, y: std * math.sqrt(lab.mlp_gradients(p, X, y)[0])
    # baselines: the mean, and least squares on (1, x, y)
    A = np.c_[np.ones(len(Xtr)), Xtr]
    coef = np.linalg.lstsq(A, ytr, rcond=None)[0]
    linear = std * math.sqrt(np.mean((np.c_[np.ones(len(Xte)), Xte] @ coef - yte) ** 2))
    print(f"  test RMSE: predicting the mean {std * math.sqrt(np.mean(yte ** 2)):.1f} m,"
          f" linear in (x, y) {linear:.1f} m, your MLP {rmse(new, Xte, yte):.1f} m"
          f" (train {rmse(new, Xtr, ytr):.1f} m); {tr_ours:.1f} s")

    def jax_loss(p, X, y):
        h = X
        for k, (W, b) in enumerate(p):
            h = h @ W + b
            if k < len(p) - 1:
                h = jnp.tanh(h)
        return jnp.mean((h[:, 0] - y) ** 2)

    step = jax.jit(lambda p, X, y: [(W - lr * dW, b - lr * db) for (W, b), (dW, db) in zip(p, jax.grad(jax_loss)(p, X, y))])
    pj = [(jnp.array(W), jnp.array(b)) for W, b in params]
    order_rng = np.random.default_rng(1)
    step(pj, jnp.array(Xtr[:batch]), jnp.array(ytr[:batch]))           # compile once
    t = time.perf_counter()
    for _ in range(epochs):
        order = order_rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            idx = order[s:s + batch]
            if len(idx) == batch:
                pj = step(pj, jnp.array(Xtr[idx]), jnp.array(ytr[idx]))
            else:
                pj = [(W - lr * dW, b - lr * db) for (W, b), (dW, db) in zip(pj, jax.grad(jax_loss)(pj, jnp.array(Xtr[idx]), jnp.array(ytr[idx])))]
    tj = time.perf_counter() - t
    jax_rmse = std * math.sqrt(float(jax_loss(pj, jnp.array(Xte), jnp.array(yte))))
    print(f"  the same network, initial weights and batch order in JAX (jit): test RMSE {jax_rmse:.1f} m; {tj:.1f} s")
    ours_grad = lab.mlp_gradients(params, Xtr[:batch], ytr[:batch])[1]
    theirs = jax.grad(jax_loss)([(jnp.array(W), jnp.array(b)) for W, b in params], jnp.array(Xtr[:batch]), jnp.array(ytr[:batch]))
    diff = max(float(np.max(np.abs(a - np.array(c)))) for (a, b), (c, d) in zip(ours_grad, theirs))
    print(f"  one batch's gradients, yours vs jax.grad: largest difference {diff:.1e}")


def lies():
    print("\n4. Where autodiff lies (JAX; your engine makes the same choices where it can)\n")
    cases = [
        ("jnp.maximum(x, 0)'(0)", lambda x: jnp.maximum(x, 0.0), 0.0, "undefined: one-sided derivatives 0 and 1"),
        ("jax.nn.relu'(0)", jax.nn.relu, 0.0, "the same function, a different convention"),
        ("|x|'(0)", jnp.abs, 0.0, "undefined: one-sided derivatives -1 and 1"),
        ("d/dx sqrt(x^2) at 0", lambda x: jnp.sqrt(x * x), 0.0, "undefined, and the chain rule meets 0 * inf"),
        ("branch: x if x != 1 else 1.0, at 1", lambda x: jnp.where(x != 1.0, x, 1.0), 1.0, "the function is the identity: 1"),
        ("argmax of (x, 0.5) at x = 0.2", lambda x: jnp.argmax(jnp.array([x, 0.5])).astype(float), 0.2, "0 almost everywhere, a jump at 0.5"),
    ]
    for name, f, x, truth in cases:
        try:
            g = float(jax.grad(f)(x))
        except Exception as e:
            g = f"error: {type(e).__name__}"
        print(f"  {name:>36}: jax says {g}   (truth: {truth})")
    print(f"  {'your vrelu at 0':>36}: {lab.reverse_gradient(lambda v: lab.vrelu(v[0]), [0.0])[1][0]}")


if __name__ == "__main__":
    agreement()
    cost()
    real_data()
    lies()
