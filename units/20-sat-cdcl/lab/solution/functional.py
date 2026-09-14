"""Unit 20 lab — a CDCL SAT solver.  REFERENCE SOLUTION, functional where it clarifies.

CDCL's trail, watch lists and activity array are mutable state by design: the whole point
of two watched literals is to avoid rebuilding anything on backtrack. So this reference
inherits that machinery from the imperative solver (as the lab sheet says) and rewrites
the parts where a functional reading teaches something:

* conflict analysis as an explicit *fold of resolution steps*: start from the conflicting
  clause and resolve it with the reason of the latest current-level literal until one
  current-level literal remains. That is literally what first-UIP learning is;
* branching as a max over unassigned variables;
* every encoder as a comprehension.
"""

from __future__ import annotations

import importlib.util
import sys
from itertools import combinations, takewhile
from pathlib import Path

import toolz as tz


def _imperative():
    name = "_unit20_imperative_reference"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name("lab.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


_imp = _imperative()
to_internal, to_dimacs, luby = _imp.to_internal, _imp.to_dimacs, _imp.luby


class Solver(_imp.Solver):
    """Steps 1, 3 (the loop) and 4 are the imperative machinery; analysis and branching are rewritten."""

    def analyze(self, confl):
        current = self.decision_level()
        position = {i >> 1: k for k, i in enumerate(self.trail)}
        at_current = lambda clause: [q for q in clause if self.level[q >> 1] == current]

        def resolve(clause):
            """Resolve on the most recently assigned current-level literal (dropping level-0 literals)."""
            pivot = max(at_current(clause), key=lambda q: position[q >> 1])
            reason = self.clauses[self.reason[pivot >> 1]]
            return (clause - {pivot}) | frozenset(q for q in reason if q >> 1 != pivot >> 1 and self.level[q >> 1] > 0)

        start = frozenset(q for q in self.clauses[confl] if self.level[q >> 1] > 0)
        chain = list(takewhile(lambda c: len(at_current(c)) > 1, tz.iterate(resolve, start)))
        learnt_set = resolve(chain[-1]) if chain else start
        for v in {q >> 1 for c in chain + [learnt_set] for q in c}:
            self.bump(v)
        uip = at_current(learnt_set)[0]
        rest = sorted(learnt_set - {uip}, key=lambda q: -self.level[q >> 1])
        learnt = [uip] + rest
        back = self.level[rest[0] >> 1] if rest else 0
        return learnt, back, len({self.level[q >> 1] for q in learnt})

    def pick_branch(self):
        free = [(self.activity[v], -v) for v in range(1, self.n + 1) if self.value[v] is None]
        if not free:
            return None
        v = -max(free)[1]
        return 2 * v + (0 if self.phase[v] else 1)


# ---------------------------------------------------------------- step 5 ---

Fresh = _imp.Fresh


def amo_pairwise(lits, fresh=None):
    return [[-a, -b] for a, b in combinations(lits, 2)]


def amo_sequential(lits, fresh):
    n = len(lits)
    if n <= 1:
        return []
    s = [fresh() for _ in range(n - 1)]
    middle = [cl for i in range(1, n - 1) for cl in ([-lits[i], s[i]], [-s[i - 1], s[i]], [-lits[i], -s[i - 1]])]
    return [[-lits[0], s[0]]] + middle + [[-lits[-1], -s[-1]]]


def amo_bitwise(lits, fresh):
    n = len(lits)
    if n <= 1:
        return []
    bits = [fresh() for _ in range((n - 1).bit_length())]
    return [[-x, b if (i >> j) & 1 else -b] for i, x in enumerate(lits) for j, b in enumerate(bits)]


def at_most_k(lits, k, fresh):
    n = len(lits)
    if k >= n:
        return []
    if k == 0:
        return [[-x] for x in lits]
    r = [[fresh() for _ in range(k)] for _ in range(n - 1)]
    first = [[-lits[0], r[0][0]]] + [[-r[0][j]] for j in range(1, k)]
    middle = [cl for i in range(1, n - 1) for cl in
              [[-lits[i], r[i][0]], [-r[i - 1][0], r[i][0]]]
              + [c for j in range(1, k) for c in ([-lits[i], -r[i - 1][j - 1], r[i][j]], [-r[i - 1][j], r[i][j]])]
              + [[-lits[i], -r[i - 1][k - 1]]]]
    return first + middle + [[-lits[-1], -r[n - 2][k - 1]]]


def pigeonhole(n):
    var = lambda p, h: p * n + h + 1
    return (n + 1) * n, ([[var(p, h) for h in range(n)] for p in range(n + 1)]
                         + [cl for h in range(n) for cl in amo_pairwise([var(p, h) for p in range(n + 1)])])


def queens(n, amo=amo_pairwise):
    var = lambda r, c: r * n + c + 1
    fresh = Fresh(n * n)
    rows = [[var(r, c) for c in range(n)] for r in range(n)]
    cols = [[var(r, c) for r in range(n)] for c in range(n)]
    diags = [line for d in range(-(n - 1), n) for line in
             ([var(r, r + d) for r in range(n) if 0 <= r + d < n],
              [var(r, d + n - 1 - r) for r in range(n) if 0 <= d + n - 1 - r < n])]
    clauses = [cl for row in rows for cl in [row] + amo(row, fresh)]
    clauses += [cl for line in cols + diags for cl in amo(line, fresh)]
    return fresh.top, clauses


def colouring(n, edges, k, amo=amo_pairwise):
    var = lambda v, c: v * k + c + 1
    fresh = Fresh(n * k)
    per_vertex = [cl for v in range(n) for cl in [[var(v, c) for c in range(k)]] + amo([var(v, c) for c in range(k)], fresh)]
    return fresh.top, per_vertex + [[-var(u, c), -var(v, c)] for u, v in edges for c in range(k)]
