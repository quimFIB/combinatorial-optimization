"""Unit 15's recorded matching runs, for units/15-matching/explore.html.

Each run is a logged copy of a reference function, and its result is checked against that
function before it is written: `hopcroft_karp` + `konig_cover` (the cover built from a maximum
matching), `hungarian` (potentials after every shift), and `gale_shapley` (every proposal).
"""

from __future__ import annotations

from collections import deque

from colib import ref

L = ref.unit("15")
INF = float("inf")

# ---------------------------------------------------------------- König's cover
NL, NR = 3, 3
K_EDGES = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]


def konig_states():
    matching = L.hopcroft_karp(NL, NR, K_EDGES)
    adj = [[] for _ in range(NL)]
    for l, r in K_EDGES:
        adj[l].append(r)
    match_r = {r: l for l, r in matching.items()}
    states = []

    def snap(note, reach_l, reach_r, edge=None, cover=None, explain=""):
        states.append({"matching": [[l, r] for l, r in sorted(matching.items())], "reach_l": sorted(reach_l),
                       "reach_r": sorted(reach_r), "edge": edge, "cover": cover, "note": note, "explain": explain})

    reach_l = {l for l in range(NL) if l not in matching}
    reach_r = set()
    snap(f"a maximum matching of size {len(matching)}, found by Hopcroft–Karp", set(), set(),
         explain="No augmenting path is left. König's construction turns the matching into a vertex cover of the same size.")
    snap(f"start from the free left vertices: {', '.join(f'ℓ{l}' for l in sorted(reach_l))}", reach_l, reach_r,
         explain="Search along alternating paths: an unmatched edge to the right, then the matched edge back to the left.")
    queue = deque(sorted(reach_l))
    while queue:
        l = queue.popleft()
        for r in adj[l]:
            if r not in reach_r and matching.get(l) != r:
                reach_r.add(r)
                m = match_r.get(r)
                if m is not None and m not in reach_l:
                    reach_l.add(m)
                    queue.append(m)
                    snap(f"ℓ{l} → r{r} (unmatched), then r{r} → ℓ{m} (matched)", reach_l, reach_r, edge=[l, r],
                         explain=f"r{r} is matched, so the path continues along its matched edge to ℓ{m}.")
                else:
                    snap(f"ℓ{l} → r{r} (unmatched)", reach_l, reach_r, edge=[l, r])
    left_cover = set(range(NL)) - reach_l
    cover = {"left": sorted(left_cover), "right": sorted(reach_r)}
    snap(f"cover = unreached left {{{', '.join(f'ℓ{l}' for l in sorted(left_cover))}}} ∪ reached right "
         f"{{{', '.join(f'r{r}' for r in sorted(reach_r))}}}", reach_l, reach_r, cover=cover,
         explain=f"Size {len(left_cover) + len(reach_r)} = matching size {len(matching)}: each certifies the other. "
                 f"The reached left vertices {{{', '.join(f'ℓ{l}' for l in sorted(reach_l))}}} have only "
                 f"{len(reach_r)} {'neighbour' if len(reach_r) == 1 else 'neighbours'} between them: a Hall violator.")
    ref_l, ref_r = L.konig_cover(NL, NR, K_EDGES, matching)
    assert (set(ref_l), set(ref_r)) == (left_cover, reach_r), "König trace disagrees with the reference"
    return states


# ---------------------------------------------------------------- Hungarian method
COST = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]


def hungarian_states():
    """A logged copy of the reference hungarian (1-based arrays, as there)."""
    n = len(COST)
    u, v, p, way = [0] * (n + 1), [0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    states = []

    def snap(note, tree_rows=(), tree_cols=(), explain="", row=None):
        assign = {p[j] - 1: j - 1 for j in range(1, n + 1) if p[j] != 0}
        states.append({"u": u[1:], "v": v[1:], "assign": [[i, j] for i, j in sorted(assign.items())],
                       "reduced": [[COST[i][j] - u[i + 1] - v[j + 1] for j in range(n)] for i in range(n)],
                       "tree_rows": sorted(tree_rows), "tree_cols": sorted(tree_cols), "row": row,
                       "note": note, "explain": explain})

    snap("potentials u = v = 0: every reduced cost is the cost itself",
         explain="Rows are added one at a time. Each time, potentials shift until a zero reduced cost leads to a free column.")
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = COST[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            tree_rows = {p[j] - 1 for j in range(n + 1) if used[j]}
            tree_cols = {j - 1 for j in range(1, n + 1) if used[j]}
            j0 = j1
            free = p[j0] == 0
            snap(f"row {i}: shift by {delta}; column {j0} becomes tight" + (" and is free" if free else f", held by row {p[j0]}"),
                 tree_rows, tree_cols | {j0 - 1}, row=i - 1,
                 explain=(f"Rows in the search tree gain {delta} in u, its columns lose {delta} in v, so their tight edges stay tight "
                          f"and the cheapest edge leaving the tree reaches reduced cost 0. ") +
                         ("A free column: augment." if free else "Its row joins the tree and the search continues."))
            if free:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
        snap(f"row {i} assigned: the matching grows along the tight path", row=i - 1,
             explain="Swap assignments along the path of tight edges, from the new row to the free column.")
    assign = [0] * n
    for j in range(1, n + 1):
        assign[p[j] - 1] = j - 1
    total = sum(COST[i][assign[i]] for i in range(n))
    states[-1]["note"] = f"done: cost {total}, equal to Σu + Σv = {sum(u[1:]) + sum(v[1:])}"
    states[-1]["explain"] = "Every reduced cost is ≥ 0 and the assigned ones are 0: the potentials certify that no assignment is cheaper."
    ref_assign, ref_total, ref_u, ref_v = L.hungarian(COST)
    assert (assign, total, u[1:], v[1:]) == (ref_assign, ref_total, ref_u, ref_v), "Hungarian trace disagrees with the reference"
    return states


# ---------------------------------------------------------------- Gale–Shapley
PROPOSERS, RECEIVERS = ["A", "B", "C"], ["X", "Y", "Z"]
P_PREFS = [[0, 1, 2], [0, 1, 2], [1, 0, 2]]
R_PREFS = [[1, 0, 2], [0, 1, 2], [0, 1, 2]]


def gale_shapley_states():
    n = len(P_PREFS)
    rank = [{p: k for k, p in enumerate(prefs)} for prefs in R_PREFS]
    next_choice, holder, free = [0] * n, {}, deque(range(n))
    states = []

    def snap(note, proposal=None, answer=None, explain=""):
        states.append({"holder": {RECEIVERS[r]: PROPOSERS[p] for r, p in holder.items()}, "next": next_choice[:],
                       "free": [PROPOSERS[p] for p in free], "proposal": proposal, "answer": answer,
                       "note": note, "explain": explain})

    snap("everyone starts free; A, B and C will propose, best choice first",
         explain="A receiver holds the best proposal so far and can trade up. A proposer rejected or dropped proposes to its next choice.")
    while free:
        p = free.popleft()
        r = P_PREFS[p][next_choice[p]]
        next_choice[p] += 1
        current = holder.get(r)
        P, Rn = PROPOSERS[p], RECEIVERS[r]
        if current is None:
            holder[r] = p
            snap(f"{P} → {Rn}: accepted", [P, Rn], "accept", explain=f"{Rn} was free, so it holds {P} for now.")
        elif rank[r][p] < rank[r][current]:
            holder[r] = p
            free.append(current)
            snap(f"{P} → {Rn}: accepted, {PROPOSERS[current]} is dropped", [P, Rn], "trade",
                 explain=f"{Rn} ranks {P} above {PROPOSERS[current]}, so it trades up; {PROPOSERS[current]} is free again.")
        else:
            free.append(p)
            snap(f"{P} → {Rn}: rejected", [P, Rn], "reject",
                 explain=f"{Rn} holds {PROPOSERS[current]}, whom it ranks above {P}. {P} will try its next choice.")
    result = {p: r for r, p in holder.items()}
    states[-1]["note"] += ": nobody is free, the matching is stable"
    assert result == L.gale_shapley(P_PREFS, R_PREFS), "Gale–Shapley trace disagrees with the reference"
    assert L.is_stable(P_PREFS, R_PREFS, result)
    return states


def data():
    return {
        "konig": {"title": "König's cover from a maximum matching", "nl": NL, "nr": NR, "edges": K_EDGES, "states": konig_states()},
        "hungarian": {"title": "the Hungarian method on a 3×3 cost matrix", "cost": COST, "states": hungarian_states()},
        "gale": {"title": "Gale–Shapley, proposers A, B, C", "proposers": PROPOSERS, "receivers": RECEIVERS,
                 "p_prefs": [[RECEIVERS[r] for r in prefs] for prefs in P_PREFS],
                 "r_prefs": [[PROPOSERS[p] for p in prefs] for prefs in R_PREFS], "states": gale_shapley_states()},
    }
