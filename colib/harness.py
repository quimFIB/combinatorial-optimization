"""Differential testing: run an algorithm against the oracle and fail loudly.

    differential(my_algorithm, instances(VertexCover, sizes=range(2, 12)))

`my_algorithm(problem)` returns a solution in the problem's space. For each
instance, smallest first, the harness checks that the solution is feasible and
that its value matches the oracle's — or, with `ratio=`, is within that factor
of it (for approximation algorithms). The first failure raises `Disagreement`
carrying the instance, so the counterexample you are shown is the smallest one
the sweep found.
"""

from __future__ import annotations

import pprint
from typing import Callable, Iterable

from colib.oracle import brute_force


class Disagreement(AssertionError):
    def __init__(self, reason: str, problem, got, oracle):
        self.reason, self.problem, self.got, self.oracle = reason, problem, got, oracle
        super().__init__(
            f"\n{reason}\n\ninstance:\n{pprint.pformat(problem, width=88)}\n\n"
            f"algorithm returned: {got!r}\n"
            f"oracle optimum:     {oracle.value!r} at {oracle.solution!r}")


def instances(cls, sizes: Iterable[int], seeds: Iterable[int] = range(20), **kw):
    """Random instances of `cls`, ordered by size then seed."""
    seeds = list(seeds)
    for n in sizes:
        for s in seeds:
            yield cls.random(n, seed=s, **kw)


def differential(algorithm: Callable, problems: Iterable, *, ratio: float | None = None,
                 oracle: Callable = brute_force) -> int:
    """Check `algorithm` on every problem; return how many were checked."""
    checked = 0
    for p in problems:
        truth = oracle(p)
        got = algorithm(p)
        checked += 1
        if truth.value is None:
            if got is not None:
                raise Disagreement("oracle says infeasible, algorithm returned a solution",
                                   p, got, truth)
            continue
        if got is None:
            raise Disagreement("algorithm returned None on a feasible instance", p, got, truth)
        if not p.is_feasible(got):
            raise Disagreement("algorithm returned an infeasible solution", p, got, truth)
        v = p.objective(got)
        if ratio is None:
            if v != truth.value:
                raise Disagreement(f"value {v} != optimum {truth.value}", p, got, truth)
        else:
            bound = truth.value * ratio if p.sense == "min" else truth.value / ratio
            worse = v > bound if p.sense == "min" else v < bound
            if worse:
                raise Disagreement(f"value {v} is outside ratio {ratio} of optimum "
                                   f"{truth.value}", p, got, truth)
    return checked
