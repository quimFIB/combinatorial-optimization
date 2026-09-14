"""Unit 26's recorded local-search and annealing runs, for units/26-metaheuristics/explore.html.

Every move and length comes from unit 26's reference solution: 2-opt runs replay the reference
`two_opt_move` and `_reverse` in the order `two_opt(..., dont_look=False)` applies them (and the
final tour is checked against `two_opt` itself); annealing runs replay `simulated_annealing`'s
draws with the reference `accept` and `temperature`, and the best length is checked against it.
`uv run co viz 26` writes units/26-metaheuristics/viz-data.js.
"""

from __future__ import annotations

import math
import random

from colib import ref

L = ref.unit("26")


def euclid(coords):
    return [[round(math.dist(p, q)) for q in coords] for p in coords]


def two_opt_trace(coords, tour, k=5, names=None):
    dist = euclid(coords)
    nb = L.neighbour_lists(dist, k)
    nm = (lambda c: names[c]) if names else str
    tour = list(tour)
    n = len(tour)
    pos = [0] * n
    for i, c in enumerate(tour):
        pos[c] = i
    states = [{"tour": list(tour), "length": L.tour_length(dist, tour), "move": None,
               "note": f"start: length {L.tour_length(dist, tour)}"}]
    changed = True
    while changed:
        changed = False
        for a in list(tour):
            move = L.two_opt_move(dist, tour, pos, nb, a)
            if move is None:
                continue
            i, j, (a_, b, c, d) = move
            before = L.tour_length(dist, tour)
            L._reverse(tour, pos, i, j)
            after = L.tour_length(dist, tour)
            states.append({
                "tour": list(tour), "length": after, "move": [a_, b, c, d],
                "removed": [[a_, b], [c, d]], "added": [[a_, c], [b, d]],
                "note": f"remove {nm(a_)}–{nm(b)} and {nm(c)}–{nm(d)}, add {nm(a_)}–{nm(c)} and {nm(b)}–{nm(d)}: length {before} → {after}",
                "explain": (f"From city {nm(a_)}, its neighbour list offers {nm(c)}, closer than its tour neighbour {nm(b)} "
                            f"({dist[a_][c]} < {dist[a_][b]}). Swapping the two edges changes the length by "
                            f"({dist[a_][c]} + {dist[b][d]}) − ({dist[a_][b]} + {dist[c][d]}) = {after - before}, "
                            f"so the stretch between them is reversed."),
            })
            changed = True
    states[-1]["explain"] = (states[-1].get("explain", "") + " No city has an improving move left: a 2-opt local optimum."
                             ).strip()
    ref_tour = L.two_opt(dist, states[0]["tour"], nb, dont_look=False)
    assert L.tour_length(dist, ref_tour) == states[-1]["length"], "replay disagrees with reference two_opt"
    return {"coords": coords, "states": states}


def annealing_trace(coords, seed, iterations, t0, t_end, every=25):
    dist = euclid(coords)
    n = len(coords)
    start = list(range(n))
    rng = random.Random(seed)
    tour = list(start)
    length = L.tour_length(dist, tour)
    best = length
    snaps = []
    accepted_worse = proposed_worse = 0
    for it in range(iterations):
        i, j = sorted(rng.sample(range(n), 2))
        u = rng.random()
        T = L.temperature(t0, t_end, iterations, it)
        if not (i == 0 and j == n - 1):
            a, b = tour[i - 1], tour[i]
            c, d = tour[j], tour[(j + 1) % n]
            delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
            if delta > 0:
                proposed_worse += 1
            if L.accept(delta, T, u):
                if delta > 0:
                    accepted_worse += 1
                tour[i:j + 1] = reversed(tour[i:j + 1])
                length += delta
                best = min(best, length)
        if it % every == 0 or it == iterations - 1:
            snaps.append({"it": it, "T": T, "tour": list(tour), "length": length, "best": best,
                          "accepted_worse": accepted_worse, "proposed_worse": proposed_worse})
    _, ref_best = L.simulated_annealing(dist, start, random.Random(seed), iterations, t0, t_end)
    assert ref_best == best, (ref_best, best)
    mean_edge = sum(dist[a][b] for a in range(n) for b in range(n) if a != b) / (n * (n - 1))
    return {"coords": coords, "iterations": iterations, "t0": t0, "t_end": t_end, "every": every,
            "snaps": snaps, "mean_edge": round(mean_edge, 1), "start_length": L.tour_length(dist, start)}


def data():
    six = [(0, 0), (3, 0), (6, 0), (6, 4), (3, 4), (0, 4)]
    rng = random.Random(7)
    twelve = [(rng.randint(0, 100), rng.randint(0, 70)) for _ in range(12)]
    shuffled = list(range(12))
    random.Random(3).shuffle(shuffled)
    nn = L.nearest_neighbour_tour(euclid(twelve))
    rng = random.Random(11)
    twenty = [(rng.randint(0, 100), rng.randint(0, 70)) for _ in range(20)]
    runs = {
        "six": {"title": "Six cities, the crossing tour A B D C E F", **two_opt_trace(six, [0, 1, 3, 2, 4, 5], names=list("ABCDEF")),
                "names": list("ABCDEF")},
        "twelve-random": {"title": "Twelve cities, a random start tour", **two_opt_trace(twelve, shuffled)},
        "twelve-nn": {"title": "Twelve cities, nearest-neighbour start", **two_opt_trace(twelve, nn)},
    }
    anneal = {
        "hot": {"title": "Hot start: T from 100 down to 0.5", **annealing_trace(twenty, 5, 4000, 100.0, 0.5)},
        "mean": {"title": "T from 46 (the mean edge) down to 0.5", **annealing_trace(twenty, 5, 4000, 46.0, 0.5)},
        "cold": {"title": "Cold start: T from 1 down to 0.5 (nearly plain descent)", **annealing_trace(twenty, 5, 4000, 1.0, 0.5)},
    }
    return {"twoopt": runs, "anneal": anneal}
