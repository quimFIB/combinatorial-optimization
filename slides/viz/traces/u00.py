"""Unit 00's recorded data, for units/00-models-and-oracle/explore.html.

The oracle run replays colib's brute_force on the running example, candidate by candidate:
the same loop, the same order (colib.spaces.Binary), the same "keep the first best" rule.
The result is checked against brute_force itself before it is written.
"""

from __future__ import annotations

from colib.oracle import brute_force
from colib.problems import VertexCover

EDGES = ((0, 1), (0, 2), (1, 2), (2, 3))


def oracle_run():
    problem = VertexCover(4, EDGES)
    best_val = best_sol = None
    feasible = examined = 0
    states = []
    for x in problem.space():
        examined += 1
        uncovered = [list(e) for e in problem.edges if not (x[e[0]] or x[e[1]])]
        ok = problem.is_feasible(x)
        improved = False
        if ok:
            feasible += 1
            v = problem.objective(x)
            if best_val is None or v < best_val:
                best_val, best_sol, improved = v, x, True
        picks = [i for i, b in enumerate(x) if b]
        if not ok:
            note = f"{{{', '.join(map(str, picks))}}} misses edge {uncovered[0][0]}{uncovered[0][1]}: not a cover"
        elif improved:
            note = f"{{{', '.join(map(str, picks))}}} is a cover of size {sum(x)}: new best"
        else:
            note = f"{{{', '.join(map(str, picks))}}} is a cover of size {sum(x)}, no better than {best_val}"
        states.append({
            "x": list(x), "feasible": ok, "uncovered": uncovered, "improved": improved,
            "examined": examined, "count_feasible": feasible,
            "best": best_val, "best_x": list(best_sol) if best_sol else None, "note": note,
        })
    result = brute_force(problem)
    assert (result.value, tuple(result.solution), result.feasible, result.examined) == \
        (best_val, best_sol, feasible, examined), "replay disagrees with colib.oracle.brute_force"
    states[-1]["explain"] = (f"All {examined} candidates examined, {feasible} of them covers. The best, "
                             f"value {best_val}, is the first one found; examined == 16 is the proof "
                             "that nothing was skipped.")
    return {"title": "Vertex cover on the running example (edges 01, 02, 12, 23)",
            "edges": [list(e) for e in EDGES], "n": 4, "states": states}


def data():
    return {"oracle": oracle_run()}
