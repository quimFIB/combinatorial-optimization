"""Unit 20 lab — a CDCL SAT solver.  REFERENCE SOLUTION, imperative.

Clauses come in DIMACS form: lists of nonzero ints, v for x_v and -v for not x_v,
variables 1..n. Internally a literal is an int i = 2v + (1 if negative): its negation
is i ^ 1 and its variable is i >> 1. Unit 21 builds on this solver through
colib.ref.unit("20").
"""

from __future__ import annotations

from colib.ref import unit

luby = unit("19").luby


def to_internal(lit):
    return 2 * abs(lit) + (lit < 0)


def to_dimacs(i):
    return -(i >> 1) if i & 1 else i >> 1


# ---------------------------------------------------------------- step 1 ---

class Solver:
    def __init__(self, nvars, clauses=(), proof=None, restart_base=100, reduce_base=2000, decay=0.95):
        self.n = nvars
        self.clauses = []                       # lists of internal literals
        self.learnt = []                        # per clause
        self.lbd = []
        self.deleted = []
        self.watches = [[] for _ in range(2 * nvars + 2)]
        self.value = [None] * (nvars + 1)       # True / False / None per variable
        self.level = [0] * (nvars + 1)
        self.reason = [None] * (nvars + 1)      # clause index, or None for decisions and level-0 units
        self.trail, self.trail_lim, self.qhead = [], [], 0
        self.activity = [0.0] * (nvars + 1)
        self.var_inc, self.decay = 1.0, decay
        self.phase = [False] * (nvars + 1)
        self.proof = proof                      # a list to append DRAT lines to, or None
        self.restart_base, self.reduce_base = restart_base, reduce_base
        self.stats = dict(conflicts=0, decisions=0, propagations=0, learned=0, deleted=0, restarts=0)
        self.ok = True
        for c in clauses:
            self.add_clause(c)

    # -- assignment --

    def lit_value(self, i):
        v = self.value[i >> 1]
        return None if v is None else v != bool(i & 1)

    def decision_level(self):
        return len(self.trail_lim)

    def enqueue(self, i, reason):
        v = i >> 1
        self.value[v] = not (i & 1)
        self.level[v] = self.decision_level()
        self.reason[v] = reason
        self.trail.append(i)

    def add_clause(self, lits):
        """Add an original clause (DIMACS literals) at decision level 0. Returns self.ok."""
        if not self.ok:
            return False
        assert self.decision_level() == 0
        seen = set()
        c = []
        for lit in lits:
            i = to_internal(lit)
            if i ^ 1 in seen:
                return True                     # tautology
            if i in seen or self.lit_value(i) is False:
                continue
            if self.lit_value(i) is True:
                return True                     # already satisfied
            seen.add(i)
            c.append(i)
        if not c:
            self.ok = False
            return False
        if len(c) == 1:
            self.enqueue(c[0], None)
            if self.propagate() is not None:
                self.ok = False
            return self.ok
        self._attach(c, learnt=False, lbd=0)
        return True

    def _attach(self, c, learnt, lbd):
        ci = len(self.clauses)
        self.clauses.append(c)
        self.learnt.append(learnt)
        self.lbd.append(lbd)
        self.deleted.append(False)
        self.watches[c[0]].append(ci)
        self.watches[c[1]].append(ci)
        return ci

    def propagate(self):
        """Two-watched-literal unit propagation from self.qhead. watches[i] holds the clauses whose first
        two literals include i; they are visited when i becomes false. Returns a conflicting clause
        index, or None."""
        while self.qhead < len(self.trail):
            p = self.trail[self.qhead]
            self.qhead += 1
            self.stats["propagations"] += 1
            false_lit = p ^ 1
            ws = self.watches[false_lit]
            keep = []
            for k, ci in enumerate(ws):
                if self.deleted[ci]:
                    continue
                c = self.clauses[ci]
                if c[0] == false_lit:
                    c[0], c[1] = c[1], c[0]
                if self.lit_value(c[0]) is True:
                    keep.append(ci)
                    continue
                for j in range(2, len(c)):
                    if self.lit_value(c[j]) is not False:
                        c[1], c[j] = c[j], c[1]
                        self.watches[c[1]].append(ci)
                        break
                else:
                    keep.append(ci)
                    if self.lit_value(c[0]) is False:
                        keep.extend(ws[k + 1:])
                        self.watches[false_lit] = keep
                        self.qhead = len(self.trail)
                        return ci
                    self.enqueue(c[0], ci)
            self.watches[false_lit] = keep
        return None

    # ---------------------------------------------------------------- step 2 ---

    def analyze(self, confl):
        """First-UIP conflict analysis. Returns (learned clause as internal literals with the asserting
        literal first and a literal of the backjump level second, backjump level, LBD). Bumps the
        activity of every variable seen."""
        seen = [False] * (self.n + 1)
        learnt = [None]
        counter = 0
        p = None
        index = len(self.trail) - 1
        current = self.decision_level()
        while True:
            c = self.clauses[confl]
            for q in (c if p is None else c[1:]):
                v = q >> 1
                if not seen[v] and self.level[v] > 0:
                    seen[v] = True
                    self.bump(v)
                    if self.level[v] >= current:
                        counter += 1
                    else:
                        learnt.append(q)
            while not seen[self.trail[index] >> 1]:
                index -= 1
            p = self.trail[index]
            index -= 1
            confl = self.reason[p >> 1]
            seen[p >> 1] = False
            counter -= 1
            if counter == 0:
                break
        learnt[0] = p ^ 1
        if len(learnt) == 1:
            back = 0
        else:
            best = max(range(1, len(learnt)), key=lambda k: self.level[learnt[k] >> 1])
            learnt[1], learnt[best] = learnt[best], learnt[1]
            back = self.level[learnt[1] >> 1]
        lbd = len({self.level[q >> 1] for q in learnt})
        return learnt, back, lbd

    def bump(self, v):
        self.activity[v] += self.var_inc
        if self.activity[v] > 1e100:
            self.activity = [a * 1e-100 for a in self.activity]
            self.var_inc *= 1e-100

    def cancel_until(self, lvl):
        if self.decision_level() > lvl:
            for i in reversed(self.trail[self.trail_lim[lvl]:]):
                v = i >> 1
                self.phase[v] = self.value[v]
                self.value[v] = None
                self.reason[v] = None
            del self.trail[self.trail_lim[lvl]:]
            del self.trail_lim[lvl:]
            self.qhead = len(self.trail)

    # ---------------------------------------------------------------- step 3 ---

    def pick_branch(self):
        """The unassigned variable of highest activity (lowest index on ties), as a literal with its
        saved phase; None if every variable is assigned."""
        best, best_act = None, -1.0
        for v in range(1, self.n + 1):
            if self.value[v] is None and self.activity[v] > best_act:
                best, best_act = v, self.activity[v]
        return None if best is None else 2 * best + (0 if self.phase[best] else 1)

    def solve(self, conflict_limit=None):
        """True (satisfiable, see model()), False (unsatisfiable), or None if conflict_limit was hit."""
        if not self.ok:
            self._proof([])
            return False
        restart_count, conflicts_here = 0, 0
        limit = self.restart_base * luby(1)
        reduce_at = self.reduce_base
        while True:
            confl = self.propagate()
            if confl is not None:
                self.stats["conflicts"] += 1
                conflicts_here += 1
                if self.decision_level() == 0:
                    self.ok = False
                    self._proof([])
                    return False
                learnt, back, lbd = self.analyze(confl)
                self.cancel_until(back)
                self._proof(learnt)
                if len(learnt) == 1:
                    self.enqueue(learnt[0], None)
                else:
                    ci = self._attach(learnt, learnt=True, lbd=lbd)
                    self.enqueue(learnt[0], ci)
                self.stats["learned"] += 1
                self.var_inc /= self.decay
                if conflict_limit is not None and self.stats["conflicts"] >= conflict_limit:
                    self.cancel_until(0)
                    return None
                if conflicts_here >= limit:
                    self.cancel_until(0)
                    restart_count += 1
                    self.stats["restarts"] += 1
                    conflicts_here = 0
                    limit = self.restart_base * luby(restart_count + 1)
                if self.stats["learned"] >= reduce_at:
                    self.reduce_db()
                    reduce_at += self.reduce_base
            else:
                lit = self.pick_branch()
                if lit is None:
                    return True
                self.stats["decisions"] += 1
                self.trail_lim.append(len(self.trail))
                self.enqueue(lit, None)

    def model(self):
        """Values of variables 1..n as a list of booleans (index 0 is variable 1)."""
        return [bool(self.value[v]) for v in range(1, self.n + 1)]

    # ---------------------------------------------------------------- step 4 ---

    def _proof(self, lits):
        if self.proof is not None:
            self.proof.append(" ".join(str(to_dimacs(i)) for i in lits) + (" 0" if lits else "0"))

    def locked(self, ci):
        c = self.clauses[ci]
        v = c[0] >> 1
        return self.reason[v] == ci and self.lit_value(c[0]) is True

    def reduce_db(self):
        """Delete the worse half of the learned clauses by LBD (largest first), keeping clauses with
        LBD <= 2 and clauses that are the reason for a current assignment. Logs deletions to the proof."""
        candidates = [ci for ci in range(len(self.clauses))
                      if self.learnt[ci] and not self.deleted[ci] and self.lbd[ci] > 2 and not self.locked(ci)]
        candidates.sort(key=lambda ci: -self.lbd[ci])
        for ci in candidates[:len(candidates) // 2]:
            self.deleted[ci] = True
            self.stats["deleted"] += 1
            if self.proof is not None:
                self.proof.append("d " + " ".join(str(to_dimacs(i)) for i in self.clauses[ci]) + " 0")


# ---------------------------------------------------------------- step 5 ---

class Fresh:
    """A supply of new variable numbers above `start`."""

    def __init__(self, start):
        self.top = start

    def __call__(self):
        self.top += 1
        return self.top


def amo_pairwise(lits, fresh=None):
    return [[-a, -b] for k, a in enumerate(lits) for b in lits[k + 1:]]


def amo_sequential(lits, fresh):
    """Sinz's sequential counter for at most one: s_i means 'some of the first i literals is true'."""
    n = len(lits)
    if n <= 1:
        return []
    s = [fresh() for _ in range(n - 1)]
    clauses = [[-lits[0], s[0]]]
    for i in range(1, n - 1):
        clauses += [[-lits[i], s[i]], [-s[i - 1], s[i]], [-lits[i], -s[i - 1]]]
    clauses.append([-lits[n - 1], -s[n - 2]])
    return clauses


def amo_bitwise(lits, fresh):
    """Binary encoding: literal i true forces the bits b to spell i."""
    n = len(lits)
    if n <= 1:
        return []
    width = (n - 1).bit_length()
    bits = [fresh() for _ in range(width)]
    return [[-lits[i], bits[j] if (i >> j) & 1 else -bits[j]] for i in range(n) for j in range(width)]


def at_most_k(lits, k, fresh):
    """Sinz's sequential counter: at most k of lits true. r[i][j] means 'at least j+1 of the first i+1 are true'."""
    n = len(lits)
    if k >= n:
        return []
    if k == 0:
        return [[-x] for x in lits]
    r = [[fresh() for _ in range(k)] for _ in range(n - 1)]
    clauses = [[-lits[0], r[0][0]]] + [[-r[0][j]] for j in range(1, k)]
    for i in range(1, n - 1):
        clauses.append([-lits[i], r[i][0]])
        clauses.append([-r[i - 1][0], r[i][0]])
        for j in range(1, k):
            clauses.append([-lits[i], -r[i - 1][j - 1], r[i][j]])
            clauses.append([-r[i - 1][j], r[i][j]])
        clauses.append([-lits[i], -r[i - 1][k - 1]])
    clauses.append([-lits[n - 1], -r[n - 2][k - 1]])
    return clauses


def pigeonhole(n):
    """n + 1 pigeons, n holes: x_{p,h} = variable p * n + h + 1. Returns (nvars, clauses)."""
    var = lambda p, h: p * n + h + 1
    clauses = [[var(p, h) for h in range(n)] for p in range(n + 1)]
    for h in range(n):
        clauses += amo_pairwise([var(p, h) for p in range(n + 1)])
    return (n + 1) * n, clauses


def queens(n, amo=amo_pairwise):
    """x_{r,c} = variable r * n + c + 1: exactly one queen per row, at most one per column and diagonal."""
    var = lambda r, c: r * n + c + 1
    fresh = Fresh(n * n)
    clauses = []
    for r in range(n):
        row = [var(r, c) for c in range(n)]
        clauses.append(row)
        clauses += amo(row, fresh)
    for c in range(n):
        clauses += amo([var(r, c) for r in range(n)], fresh)
    for d in range(-(n - 1), n):
        diag = [var(r, r + d) for r in range(n) if 0 <= r + d < n]
        anti = [var(r, d + n - 1 - r) for r in range(n) if 0 <= d + n - 1 - r < n]
        clauses += amo(diag, fresh) + amo(anti, fresh)
    return fresh.top, clauses


def colouring(n, edges, k, amo=amo_pairwise):
    """x_{v,c} = variable v * k + c + 1: every vertex gets exactly one colour; adjacent vertices differ."""
    var = lambda v, c: v * k + c + 1
    fresh = Fresh(n * k)
    clauses = []
    for v in range(n):
        clauses.append([var(v, c) for c in range(k)])
        clauses += amo([var(v, c) for c in range(k)], fresh)
    for u, v in edges:
        clauses += [[-var(u, c), -var(v, c)] for c in range(k)]
    return fresh.top, clauses
