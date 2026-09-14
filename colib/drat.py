"""A DRAT-style proof checker for RUP proofs (units 20 and 21).

A proof is a sequence of lines in DRAT text format: "l1 l2 ... 0" adds a lemma,
"d l1 l2 ... 0" deletes a clause. Every added lemma must be RUP (reverse unit
propagation) with respect to the current clause set: assigning the negation of its
literals and unit-propagating must reach a conflict. The proof is accepted when all
lemmas check and the empty clause has been added (or is RUP at the end).

CDCL solvers only ever need RUP lemmas, so this checker does not implement the RAT
check. If `drat-trim` is on your PATH, `check_with_drat_trim` runs it on the same files.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def _parse(lines):
    for line in lines:
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        delete = line.startswith("d")
        nums = [int(t) for t in (line[1:] if delete else line).split()]
        if not nums or nums[-1] != 0:
            raise ValueError(f"proof line not terminated by 0: {line!r}")
        yield delete, tuple(nums[:-1])


class _DB:
    """Clauses with two watched literals; assignments are pushed and popped per check."""

    def __init__(self, nvars):
        self.value = {}
        self.clauses = []
        self.active = []
        self.watches = {}
        self.units = []                                        # indices of unit clauses
        self.index = {}                                        # sorted literals -> list of clause indices

    def add(self, lits):
        lits = list(dict.fromkeys(lits))
        ci = len(self.clauses)
        self.clauses.append(lits)
        self.active.append(True)
        self.index.setdefault(tuple(sorted(lits)), []).append(ci)
        if len(lits) == 1:
            self.units.append(ci)
        elif len(lits) >= 2:
            for lit in lits[:2]:
                self.watches.setdefault(-lit, []).append(ci)
        return ci

    def delete(self, lits):
        key = tuple(sorted(dict.fromkeys(lits)))
        for ci in self.index.get(key, []):
            if self.active[ci]:
                self.active[ci] = False
                return True
        return False

    def val(self, lit):
        v = self.value.get(abs(lit))
        return None if v is None else (v if lit > 0 else not v)

    def rup(self, lemma):
        """True iff assigning the negation of `lemma` and unit propagating gives a conflict."""
        self.value = {}
        trail = []

        def assign(lit):
            cur = self.val(lit)
            if cur is False:
                return False
            if cur is None:
                self.value[abs(lit)] = lit > 0
                trail.append(lit)
            return True

        for lit in lemma:
            if not assign(-lit):
                return True                                    # lemma is a tautology
        for ci in self.units:
            if self.active[ci] and not assign(self.clauses[ci][0]):
                return True
        if any(self.active[ci] and not self.clauses[ci] for ci in range(len(self.clauses))):
            return True
        head = 0
        while head < len(trail):
            false_lit = -trail[head]
            head += 1
            ws = self.watches.get(-false_lit, [])
            keep = []
            conflict = False
            for k, ci in enumerate(ws):
                if conflict:
                    keep.append(ci)
                    continue
                if not self.active[ci]:
                    continue
                c = self.clauses[ci]
                if c[0] == false_lit:
                    c[0], c[1] = c[1], c[0]
                if self.val(c[0]) is True:
                    keep.append(ci)
                    continue
                for j in range(2, len(c)):
                    if self.val(c[j]) is not False:
                        c[1], c[j] = c[j], c[1]
                        self.watches.setdefault(-c[1], []).append(ci)
                        break
                else:
                    keep.append(ci)
                    if self.val(c[0]) is False:
                        conflict = True
                    else:
                        assign(c[0])
            self.watches[-false_lit] = keep
            if conflict:
                return True
        return False


def check_rup_proof(nvars, clauses, proof_lines, limit=None):
    """Check a RUP proof of unsatisfiability. Returns (accepted, message)."""
    db = _DB(nvars)
    for c in clauses:
        db.add(list(c))
    derived_empty = False
    for n, (delete, lits) in enumerate(_parse(proof_lines), 1):
        if limit is not None and n > limit:
            return False, f"proof longer than the limit of {limit} lines"
        if delete:
            db.delete(lits)
            continue
        if not db.rup(lits):
            return False, f"line {n}: lemma {' '.join(map(str, lits))} is not RUP"
        db.add(list(lits))
        if not lits:
            derived_empty = True
            break
    if not derived_empty and not db.rup(()):
        return False, "the empty clause was not derived"
    return True, "accepted"


def check_with_drat_trim(cnf_path, proof_path, timeout=60):
    """Run drat-trim if installed. Returns (accepted, output) or None if drat-trim is not on PATH."""
    exe = shutil.which("drat-trim")
    if exe is None:
        return None
    out = subprocess.run([exe, str(cnf_path), str(proof_path)], capture_output=True, text=True, timeout=timeout)
    return "s VERIFIED" in out.stdout, out.stdout


def write_proof(path, lines):
    Path(path).write_text("\n".join(lines) + "\n")
