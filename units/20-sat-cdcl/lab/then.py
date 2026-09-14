"""Unit 20 — "Then": your CDCL against MiniSat, CaDiCaL and Kissat, on the same DIMACS files.

  1. Random 3-SAT at the threshold (m = 4.26 n): conflicts and seconds.
  2. Pigeonhole: the humiliation, for everyone.
  3. n-queens with three at-most-one encodings: clause counts and your solve time.
  4. A DRAT proof from your solver, checked by colib's RUP checker (and drat-trim if installed).

Every instance is written to a DIMACS file in a temporary directory and read back before
solving, so the files travel both ways.

    uv run co then 20
"""

import random
import tempfile
import time
from pathlib import Path

from pysat.solvers import Solver as PySat

from colib.drat import check_rup_proof, check_with_drat_trim, write_proof
from colib.formats import read_cnf, write_cnf
from colib.testing import load_lab

lab = load_lab(__file__)
TMP = Path(tempfile.mkdtemp(prefix="unit20-"))


def rand3(n, m, seed):
    r = random.Random(seed)
    return [[v if r.random() < 0.5 else -v for v in r.sample(range(1, n + 1), 3)] for _ in range(m)]


def roundtrip(name, nvars, clauses):
    path = TMP / f"{name}.cnf"
    write_cnf(path, nvars, clauses, comment=name)
    return path, *read_cnf(path)


def mine(nvars, clauses, conflict_limit=100_000):
    s = lab.Solver(nvars, clauses)
    t = time.perf_counter()
    result = s.solve(conflict_limit=conflict_limit)
    return result, s.stats["conflicts"], time.perf_counter() - t


def theirs(name, clauses):
    with PySat(name=name, bootstrap_with=clauses) as s:
        t = time.perf_counter()
        result = s.solve()
        dt = time.perf_counter() - t
        try:
            stats = s.accum_stats() or {}
        except NotImplementedError:                             # Kissat's pysat binding exposes no statistics
            stats = {}
    return result, stats.get("conflicts", "—"), dt


SOLVERS = ("minisat22", "cadical195", "kissat404")


def header():
    print(f"  {'instance':<22} {'result':>6} | {'yours: conflicts':>16} {'s':>7} | " +
          " | ".join(f"{n + ': conflicts':>21} {'s':>6}" for n in SOLVERS))


def row(name, nvars, clauses, run_mine=True):
    _, nv, cl = roundtrip(name, nvars, clauses)
    cells = []
    result = None
    if run_mine:
        result, c, t = mine(nv, cl)
        cells.append(f"{c:>16} {t:>7.2f}" if result is not None else f"{'> ' + str(c):>16} {t:>7.2f}")
    else:
        cells.append(f"{'skipped':>16} {'':>7}")
    for s in SOLVERS:
        res, c, t = theirs(s, cl)
        result = res if result is None else result
        assert res == result, (name, s)
        cells.append(f"{str(c):>21} {t:>6.3f}")
    print(f"  {name:<22} {('SAT' if result else 'UNSAT'):>6} | " + " | ".join(cells))
    return result


def random_section():
    print("1. Random 3-SAT at m = 4.26 n\n")
    header()
    for n in (100, 150, 200, 250):
        for seed in range(2):
            row(f"3sat n={n} #{seed}", n, rand3(n, int(4.26 * n), 1000 * n + seed))


def pigeonhole_section():
    print("\n2. Pigeonhole: n + 1 pigeons, n holes (pairwise at-most-one)\n")
    header()
    for n in range(6, 11):
        nvars, clauses = lab.pigeonhole(n)
        row(f"php {n + 1} into {n}", nvars, clauses, run_mine=n <= 8)


def queens_section():
    print("\n3. n-queens, three at-most-one encodings (your solver)\n")
    print(f"  {'n':>3} " + " ".join(f"{e:>28}" for e in ("pairwise", "sequential", "bitwise")))
    print(f"  {'':>3} " + " ".join(f"{'vars / clauses / s':>28}" for _ in range(3)))
    for n in (10, 20, 40, 60):
        cells = []
        for enc in (lab.amo_pairwise, lab.amo_sequential, lab.amo_bitwise):
            nvars, clauses = lab.queens(n, enc)
            s = lab.Solver(nvars, clauses)
            t = time.perf_counter()
            assert s.solve()
            cells.append(f"{nvars:>7} / {len(clauses):>7} / {time.perf_counter() - t:>6.2f}")
        print(f"  {n:>3} " + " ".join(f"{c:>28}" for c in cells))


def proof_section():
    print("\n4. DRAT proofs from your solver\n")
    for name, (nvars, clauses) in (("3sat n=120 unsat", (120, rand3(120, 600, 5))), ("php 7 into 6", lab.pigeonhole(6))):
        path, nvars, clauses = roundtrip(name.replace(" ", "_"), nvars, clauses)
        proof = []
        s = lab.Solver(nvars, clauses, proof=proof)
        assert s.solve() is False
        proof_path = TMP / (path.stem + ".drat")
        write_proof(proof_path, proof)
        t = time.perf_counter()
        ok, message = check_rup_proof(nvars, clauses, proof)
        lemmas = sum(1 for line in proof if not line.startswith("d"))
        deletions = len(proof) - lemmas
        print(f"  {name:<18} {lemmas:>6} lemmas, {deletions:>6} deletions: colib checker {message} "
              f"({time.perf_counter() - t:.1f} s)")
        external = check_with_drat_trim(path, proof_path)
        if external is None:
            print(f"  {'':<18} drat-trim not installed; files kept in {TMP}")
        else:
            print(f"  {'':<18} drat-trim: {'VERIFIED' if external[0] else 'rejected'}")


if __name__ == "__main__":
    random_section()
    pigeonhole_section()
    queens_section()
    proof_section()
