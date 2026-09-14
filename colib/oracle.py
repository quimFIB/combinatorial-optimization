"""The reference brute-force oracle.

Slow, obviously correct, and the thing every later algorithm is checked
against. Its "proof" of optimality is exhaustiveness: `examined` equals the
size of the space, so nothing was left unlooked-at.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Result:
    value: Any          # optimal objective, or None if infeasible
    solution: Any       # one optimal solution (the first found), or None
    feasible: int       # how many candidates satisfied the constraints
    examined: int       # how many candidates were looked at


def brute_force(problem, limit: int = 5_000_000) -> Result:
    space = problem.space()
    if space.size() > limit:
        raise ValueError(f"{type(problem).__name__}: space has {space.size():,} "
                         f"candidates, over the oracle's limit of {limit:,}")
    better = (lambda a, b: a < b) if problem.sense == "min" else (lambda a, b: a > b)
    best_val = best_sol = None
    feasible = examined = 0
    for x in space:
        examined += 1
        if not problem.is_feasible(x):
            continue
        feasible += 1
        v = problem.objective(x)
        if best_val is None or better(v, best_val):
            best_val, best_sol = v, x
    return Result(best_val, best_sol, feasible, examined)
