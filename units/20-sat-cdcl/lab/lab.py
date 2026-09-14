"""Unit 20 lab — a CDCL SAT solver.

Fill in the parts marked TODO, one step at a time, and run
    uv run co test 20
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Clauses come in DIMACS form: lists of nonzero ints, v for x_v and -v for not x_v, variables
1..n. Internally a literal is the int i = 2v + (1 if negative): its negation is i ^ 1 and its
variable is i >> 1. Unit 21 builds on this solver.

The tests read these attributes directly, so keep their names and meanings:
    value[v]   True / False / None        level[v]  decision level of v's assignment
    reason[v]  clause index or None        trail     internal literals in assignment order
    trail_lim  trail positions where each decision level starts
    qhead      next trail position to propagate
    clauses    lists of internal literals; learnt / lbd / deleted: per clause
    activity   per variable; var_inc, decay; phase: saved polarity per variable
    stats      dict with conflicts, decisions, propagations, learned, deleted, restarts
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
        """Set up every attribute listed in the module docstring (watches: one list per internal literal,
        indices 0 .. 2n+1), store proof (a list to append DRAT lines to, or None), restart_base,
        reduce_base and decay, set var_inc = 1.0 and ok = True, then add_clause each clause."""
        raise NotImplementedError  # TODO step 1

    def lit_value(self, i):
        """True / False / None for internal literal i."""
        raise NotImplementedError  # TODO step 1

    def decision_level(self):
        return len(self.trail_lim)

    def enqueue(self, i, reason):
        """Make internal literal i true at the current decision level with the given reason."""
        raise NotImplementedError  # TODO step 1

    def add_clause(self, lits):
        """Add an original clause at level 0. Drop duplicate and false literals; ignore tautologies and
        satisfied clauses. Empty: ok = False. Unit: enqueue it and propagate (a conflict sets ok = False).
        Otherwise store it and watch its first two literals. Returns ok."""
        raise NotImplementedError  # TODO step 1

    def propagate(self):
        """Two-watched-literal unit propagation of the trail from qhead (count each literal dequeued in
        stats['propagations']). watches[i] lists the clauses watching literal i, visited when i becomes
        false. Keep the invariant that a clause's two watched literals are c[0] and c[1]; an implied literal
        is moved to c[0] before it is enqueued with the clause as reason. Skip deleted clauses.
        On a conflict set qhead = len(trail) and return the clause index; otherwise return None."""
        raise NotImplementedError  # TODO step 1

    # ---------------------------------------------------------------- step 2 ---

    def analyze(self, confl):
        """First-UIP conflict analysis from clause index `confl`. Walk the trail backwards, resolving away
        current-level literals until one remains. Ignore level-0 literals; bump the activity of every
        variable seen. Returns (learnt, backjump level, lbd): learnt as internal literals, the asserting
        literal first and, if there are others, one of the highest remaining level second; lbd = the number
        of distinct decision levels in learnt."""
        raise NotImplementedError  # TODO step 2

    def bump(self, v):
        """Add var_inc to activity[v]; if it exceeds 1e100, rescale every activity and var_inc by 1e-100."""
        raise NotImplementedError  # TODO step 2

    def cancel_until(self, lvl):
        """Undo every assignment above decision level lvl, saving each variable's value in phase."""
        raise NotImplementedError  # TODO step 2

    # ---------------------------------------------------------------- step 3 ---

    def pick_branch(self):
        """The unassigned variable with the highest activity (lowest index on ties), as the internal literal
        of its saved phase (positive if phase is True); None if every variable is assigned."""
        raise NotImplementedError  # TODO step 3

    def solve(self, conflict_limit=None):
        """The CDCL loop. Propagate; on a conflict: count it, return False at level 0 (logging the empty
        clause), else analyze, backjump, log the learned clause, add it (a unit is enqueued at level 0 with
        no reason; longer clauses are attached as learnt with their lbd and enqueued with it as reason),
        count it in stats['learned'], and divide var_inc by decay. Return None (after backjumping to level
        0) once stats['conflicts'] reaches conflict_limit. Restart (backjump to 0) after
        restart_base * luby(r + 1) conflicts since the last restart, where r counts restarts. Call reduce_db
        each time stats['learned'] passes another multiple of reduce_base.
        Without a conflict: pick a branch; none left means return True; otherwise count a decision, open a
        new level and enqueue it. Return False straight away if ok is already False (log the empty clause)."""
        raise NotImplementedError  # TODO step 3

    def model(self):
        """[bool(value[v]) for v in 1..n]."""
        raise NotImplementedError  # TODO step 3

    # ---------------------------------------------------------------- step 4 ---

    def _proof(self, lits):
        """Append a DRAT addition line for internal literals `lits` to proof, if proof is not None:
        the DIMACS literals separated by spaces, then ' 0' (the empty clause is the line '0')."""
        raise NotImplementedError  # TODO step 4

    def locked(self, ci):
        """True iff clause ci is the reason for the current assignment of its first literal."""
        raise NotImplementedError  # TODO step 4

    def reduce_db(self):
        """Among learned, not deleted, not locked clauses with lbd > 2, delete the half with the largest
        lbd (mark deleted, count in stats['deleted'], log 'd <literals> 0' to the proof)."""
        raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

class Fresh:
    """A supply of new variable numbers above `start`: fresh() returns start + 1, start + 2, ...;
    fresh.top is the last one handed out."""

    def __init__(self, start):
        self.top = start

    def __call__(self):
        self.top += 1
        return self.top


def amo_pairwise(lits, fresh=None):
    """At most one of lits: one binary clause per pair."""
    raise NotImplementedError  # TODO step 5


def amo_sequential(lits, fresh):
    """Sinz's sequential counter with n - 1 fresh variables and 3n - 4 clauses."""
    raise NotImplementedError  # TODO step 5


def amo_bitwise(lits, fresh):
    """The binary encoding with ceil(log2 n) fresh bits: literal i forces the bits to spell i (n * bits clauses)."""
    raise NotImplementedError  # TODO step 5


def at_most_k(lits, k, fresh):
    """Sinz's sequential counter for at most k (k = 0: every literal false; k >= n: no clauses)."""
    raise NotImplementedError  # TODO step 5


def pigeonhole(n):
    """n + 1 pigeons into n holes. x_{p,h} is variable p * n + h + 1. Each pigeon in some hole; at most one
    pigeon per hole, pairwise. Returns (nvars, clauses)."""
    raise NotImplementedError  # TODO step 5


def queens(n, amo=amo_pairwise):
    """x_{r,c} is variable r * n + c + 1. Each row: at least one queen, and amo; each column and each diagonal
    in both directions: amo. Fresh variables start above n * n. Returns (nvars, clauses)."""
    raise NotImplementedError  # TODO step 5


def colouring(n, edges, k, amo=amo_pairwise):
    """x_{v,c} is variable v * k + c + 1. Each vertex: at least one colour, and amo; each edge: not both
    ends with the same colour. Returns (nvars, clauses)."""
    raise NotImplementedError  # TODO step 5
