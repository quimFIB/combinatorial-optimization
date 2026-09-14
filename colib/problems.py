"""The nine problems the course keeps returning to.

Each problem is a frozen dataclass holding one instance, and offers the same
four things:

    sense            "min" or "max"
    space()          a finite, enumerable superset of the feasible set
    is_feasible(x)   the constraints, as a predicate over that space
    objective(x)     the value of a feasible x

plus `random(n, seed)` to generate an instance whose size grows with n. This is
the *reference* modelling: unit 00's lab has you write two of these yourself
and checks them against the versions here.
"""

from __future__ import annotations

import math
import random as _random
from dataclasses import dataclass
from typing import ClassVar

from colib.spaces import Binary, Permutations, Product, SetPartitions


def _rng(seed):
    return _random.Random(seed)


def _random_graph(n: int, p: float, rng) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p)


# ---------------------------------------------------------------------------
# selection problems over {0,1}^n
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Knapsack:
    values: tuple[int, ...]
    weights: tuple[int, ...]
    capacity: int
    sense: ClassVar[str] = "max"

    @property
    def n(self):
        return len(self.values)

    def space(self):
        return Binary(self.n)

    def is_feasible(self, x) -> bool:
        return sum(w for w, xi in zip(self.weights, x) if xi) <= self.capacity

    def objective(self, x):
        return sum(v for v, xi in zip(self.values, x) if xi)

    @classmethod
    def random(cls, n: int, seed=0):
        r = _rng(seed)
        w = tuple(r.randint(1, 30) for _ in range(n))
        v = tuple(r.randint(1, 30) for _ in range(n))
        return cls(v, w, max(1, sum(w) // 2))


@dataclass(frozen=True)
class SetCover:
    universe: int                      # elements are range(universe)
    sets: tuple[frozenset[int], ...]
    costs: tuple[int, ...]
    sense: ClassVar[str] = "min"

    @property
    def n(self):
        return len(self.sets)

    def space(self):
        return Binary(self.n)

    def is_feasible(self, x) -> bool:
        covered = set()
        for s, xi in zip(self.sets, x):
            if xi:
                covered |= s
        return len(covered) == self.universe

    def objective(self, x):
        return sum(c for c, xi in zip(self.costs, x) if xi)

    @classmethod
    def random(cls, n: int, seed=0):
        """n sets over a universe of about 1.5n elements; always coverable."""
        r = _rng(seed)
        u = max(1, (3 * n) // 2)
        sets = [set(r.sample(range(u), r.randint(1, max(1, u // 3)))) for _ in range(n)]
        for e in range(u):                      # guarantee every element is somewhere
            if not any(e in s for s in sets):
                sets[r.randrange(n)].add(e)
        return cls(u, tuple(frozenset(s) for s in sets),
                   tuple(r.randint(1, 10) for _ in range(n)))


@dataclass(frozen=True)
class VertexCover:
    n: int
    edges: tuple[tuple[int, int], ...]
    sense: ClassVar[str] = "min"

    def space(self):
        return Binary(self.n)

    def is_feasible(self, x) -> bool:
        return all(x[u] or x[v] for u, v in self.edges)

    def objective(self, x):
        return sum(x)

    @classmethod
    def random(cls, n: int, seed=0, p: float = 0.3):
        return cls(n, _random_graph(n, p, _rng(seed)))


@dataclass(frozen=True)
class MaxCut:
    n: int
    edges: tuple[tuple[int, int], ...]
    weights: tuple[int, ...]
    sense: ClassVar[str] = "max"

    def space(self):
        return Binary(self.n)

    def is_feasible(self, x) -> bool:
        return True

    def objective(self, x):
        return sum(w for (u, v), w in zip(self.edges, self.weights) if x[u] != x[v])

    @classmethod
    def random(cls, n: int, seed=0, p: float = 0.5):
        r = _rng(seed)
        edges = _random_graph(n, p, r)
        return cls(n, edges, tuple(r.randint(1, 10) for _ in edges))


# ---------------------------------------------------------------------------
# ordering problems over permutations
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Assignment:
    cost: tuple[tuple[int, ...], ...]  # cost[i][j]: worker i does job j
    sense: ClassVar[str] = "min"

    @property
    def n(self):
        return len(self.cost)

    def space(self):
        return Permutations(self.n)

    def is_feasible(self, x) -> bool:
        return sorted(x) == list(range(self.n))

    def objective(self, x):
        return sum(self.cost[i][j] for i, j in enumerate(x))

    @classmethod
    def random(cls, n: int, seed=0):
        r = _rng(seed)
        return cls(tuple(tuple(r.randint(1, 50) for _ in range(n)) for _ in range(n)))


@dataclass(frozen=True)
class TSP:
    dist: tuple[tuple[int, ...], ...]  # symmetric, zero diagonal
    sense: ClassVar[str] = "min"

    @property
    def n(self):
        return len(self.dist)

    def space(self):
        return Permutations(self.n, fix_first=True)

    def is_feasible(self, x) -> bool:
        return sorted(x) == list(range(self.n))

    def objective(self, x):
        return sum(self.dist[x[i]][x[(i + 1) % len(x)]] for i in range(len(x)))

    @classmethod
    def random(cls, n: int, seed=0):
        """Euclidean: n points in a 100x100 square, distances rounded (TSPLIB EUC_2D)."""
        r = _rng(seed)
        pts = [(r.uniform(0, 100), r.uniform(0, 100)) for _ in range(n)]
        return cls(tuple(tuple(int(math.dist(a, b) + 0.5) for b in pts) for a in pts))


# ---------------------------------------------------------------------------
# partitioning problems over set partitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BinPacking:
    sizes: tuple[int, ...]
    capacity: int
    sense: ClassVar[str] = "min"

    @property
    def n(self):
        return len(self.sizes)

    def space(self):
        return SetPartitions(self.n)

    def is_feasible(self, x) -> bool:
        load: dict[int, int] = {}
        for item, b in enumerate(x):
            load[b] = load.get(b, 0) + self.sizes[item]
        return all(l <= self.capacity for l in load.values())

    def objective(self, x):
        return len(set(x))

    @classmethod
    def random(cls, n: int, seed=0):
        r = _rng(seed)
        return cls(tuple(r.randint(10, 60) for _ in range(n)), 100)


@dataclass(frozen=True)
class GraphColouring:
    n: int
    edges: tuple[tuple[int, int], ...]
    sense: ClassVar[str] = "min"

    def space(self):
        return SetPartitions(self.n)

    def is_feasible(self, x) -> bool:
        return all(x[u] != x[v] for u, v in self.edges)

    def objective(self, x):
        return len(set(x))

    @classmethod
    def random(cls, n: int, seed=0, p: float = 0.4):
        return cls(n, _random_graph(n, p, _rng(seed)))


# ---------------------------------------------------------------------------
# scheduling
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class JobShop:
    """jobs[j] is the ordered list of (machine, duration) operations of job j.

    A solution fixes, for every machine, the order in which the jobs using it
    run: x[m] is a permutation of the list `self.jobs_on(m)`. It is feasible iff
    the resulting disjunctive graph is acyclic; its value is the makespan, the
    longest path through that graph (semi-active schedule).
    """
    jobs: tuple[tuple[tuple[int, int], ...], ...]
    sense: ClassVar[str] = "min"

    @property
    def machines(self) -> int:
        return 1 + max(m for job in self.jobs for m, _ in job)

    def jobs_on(self, m: int) -> tuple[int, ...]:
        return tuple(j for j, job in enumerate(self.jobs) if any(mm == m for mm, _ in job))

    def space(self):
        return Product(tuple(Permutations(len(self.jobs_on(m))) for m in range(self.machines)))

    def _schedule(self, x):
        """Start times per operation, or None if the machine orders form a cycle."""
        ops = [(j, k) for j, job in enumerate(self.jobs) for k in range(len(job))]
        succ = {op: [] for op in ops}
        indeg = {op: 0 for op in ops}

        def arc(a, b):
            succ[a].append(b)
            indeg[b] += 1

        for j, job in enumerate(self.jobs):
            for k in range(len(job) - 1):
                arc((j, k), (j, k + 1))
        for m in range(self.machines):
            users = self.jobs_on(m)
            order = [users[i] for i in x[m]]
            op_of = {j: next(k for k, (mm, _) in enumerate(self.jobs[j]) if mm == m) for j in users}
            for a, b in zip(order, order[1:]):
                arc((a, op_of[a]), (b, op_of[b]))

        start = {op: 0 for op in ops}
        queue = [op for op in ops if indeg[op] == 0]
        seen = 0
        while queue:
            a = queue.pop()
            seen += 1
            end = start[a] + self.jobs[a[0]][a[1]][1]
            for b in succ[a]:
                start[b] = max(start[b], end)
                indeg[b] -= 1
                if indeg[b] == 0:
                    queue.append(b)
        return start if seen == len(ops) else None

    def is_feasible(self, x) -> bool:
        return self._schedule(x) is not None

    def objective(self, x):
        start = self._schedule(x)
        return max(start[(j, k)] + self.jobs[j][k][1] for (j, k) in start)

    @classmethod
    def ft06(cls):
        """Fisher & Thompson's 6x6 instance (1963). Optimal makespan 55."""
        return cls((((2, 1), (0, 3), (1, 6), (3, 7), (5, 3), (4, 6)),
                    ((1, 8), (2, 5), (4, 10), (5, 10), (0, 10), (3, 4)),
                    ((2, 5), (3, 4), (5, 8), (0, 9), (1, 1), (4, 7)),
                    ((1, 5), (0, 5), (2, 5), (3, 3), (4, 8), (5, 9)),
                    ((2, 9), (1, 3), (4, 5), (5, 4), (0, 3), (3, 1)),
                    ((1, 3), (3, 3), (5, 9), (0, 10), (4, 4), (2, 1))))

    @classmethod
    def random(cls, n: int, seed=0, machines: int = 3):
        """n jobs, each visiting every machine once in a random order."""
        r = _rng(seed)
        jobs = []
        for _ in range(n):
            order = list(range(machines))
            r.shuffle(order)
            jobs.append(tuple((m, r.randint(1, 9)) for m in order))
        return cls(tuple(jobs))


PROBLEMS = (Knapsack, SetCover, Assignment, BinPacking, GraphColouring,
            MaxCut, TSP, JobShop, VertexCover)
