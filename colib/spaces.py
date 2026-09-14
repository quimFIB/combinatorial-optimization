"""Solution spaces: the finite sets a brute-force oracle walks.

A problem's feasible set is described *implicitly* — by a predicate over a
space that is easy to enumerate. Choosing that space well is the first
modelling decision: bin packing over item→bin maps visits n^n candidates, over
set partitions only the Bell number B(n), because it never tells two
relabelings of the same packing apart.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Binary:
    """All 0/1 vectors of length n."""
    n: int

    def __iter__(self) -> Iterator[tuple[int, ...]]:
        return itertools.product((0, 1), repeat=self.n)

    def size(self) -> int:
        return 2 ** self.n


@dataclass(frozen=True)
class Permutations:
    """All orderings of range(n); with fix_first, those starting at 0.

    Fixing the first element removes the n-fold rotational symmetry of a tour.
    """
    n: int
    fix_first: bool = False

    def __iter__(self) -> Iterator[tuple[int, ...]]:
        if self.fix_first and self.n > 0:
            return ((0, *p) for p in itertools.permutations(range(1, self.n)))
        return itertools.permutations(range(self.n))

    def size(self) -> int:
        return math.factorial(self.n - 1 if self.fix_first and self.n else self.n)


@dataclass(frozen=True)
class SetPartitions:
    """All partitions of range(n), as restricted growth strings.

    A restricted growth string a has a[0] = 0 and a[i] <= 1 + max(a[:i]);
    a[i] is the block of element i. Each partition appears exactly once.
    """
    n: int

    def __iter__(self) -> Iterator[tuple[int, ...]]:
        return restricted_growth_strings(self.n)

    def size(self) -> int:
        return bell(self.n)


@dataclass(frozen=True)
class Product:
    """The cartesian product of several spaces; yields tuples of their elements."""
    factors: tuple

    def __iter__(self):
        return itertools.product(*self.factors)

    def size(self) -> int:
        return math.prod(f.size() for f in self.factors)


def restricted_growth_strings(n: int) -> Iterator[tuple[int, ...]]:
    if n == 0:
        yield ()
        return
    a = [0] * n

    def rec(i: int, top: int):
        if i == n:
            yield tuple(a)
            return
        for v in range(top + 2):
            a[i] = v
            yield from rec(i + 1, max(top, v))

    yield from rec(1, 0)


def bell(n: int) -> int:
    row = [1]
    for _ in range(n):
        nxt = [row[-1]]
        for x in row:
            nxt.append(nxt[-1] + x)
        row = nxt
    return row[0]
