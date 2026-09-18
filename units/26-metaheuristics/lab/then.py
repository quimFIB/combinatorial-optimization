"""Unit 26 — "Then": what the speed-ups buy, equal time budgets, time-to-target, and CVRP.

  1. TSP, n = 1000: 2-opt with full neighbour lists, with 10 per city, with don't-look bits, then Or-opt.
  2. TSP, n = 200, ten instances, a 3-second budget each: multi-start local search, simulated annealing,
     iterated local search (double-bridge kicks), and OR-Tools' routing solver with guided local search.
  3. Time-to-target (n = 150) over 30 seeds for four heuristics built from your lab; Mann-Whitney verdicts;
     out/ttt.png.
  4. CVRP, n = 60: your ALNS against OR-Tools routing, both with 10 seconds.

LKH is the reference heuristic for TSP. It isn't a dependency of this course; if the `elkai` package is
installed, section 2 tries to add it (that code path hasn't been run here, so check elkai's API first).

    uv run co then 26
"""

import math
import random
import statistics
import time
from pathlib import Path

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from colib.colgen import CVRP
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"


def uniform_tsp(n, seed, side=10_000):
    """n uniform points in a side x side square with rounded distances. (TSP.random uses a 100 x 100 square,
    where at n = 1000 most nearby distances round to 1 or 2 and the instance fills up with ties.)"""
    r = random.Random(seed)
    pts = [(r.uniform(0, side), r.uniform(0, side)) for _ in range(n)]
    return tuple(tuple(int(math.dist(a, b) + 0.5) for b in pts) for a in pts)


def timed(f, *a, **kw):
    t = time.perf_counter()
    out = f(*a, **kw)
    return out, time.perf_counter() - t


def speedups():
    print("1. 2-opt on a random uniform TSP (10 000 x 10 000 square), n = 1000, from the nearest-neighbour tour\n")
    dist = uniform_tsp(1000, 1)
    start = lab.nearest_neighbour_tour(dist)
    full, t_full_nl = timed(lab.neighbour_lists, dist, 999)
    nl10, t_nl = timed(lab.neighbour_lists, dist, 10)
    print(f"  nearest neighbour: {lab.tour_length(dist, start)}   (neighbour lists: k = 999 {t_full_nl:.1f} s, k = 10 {t_nl:.1f} s)")
    rows = [("full lists, sweep", lambda: lab.two_opt(dist, start, full, dont_look=False)),
            ("k = 10, sweep", lambda: lab.two_opt(dist, start, nl10, dont_look=False)),
            ("k = 10, don't-look bits", lambda: lab.two_opt(dist, start, nl10, dont_look=True))]
    for name, run in rows:
        tour, t = timed(run)
        print(f"  {name:>29}: {lab.tour_length(dist, tour):>6}   {t:6.2f} s")
    tour, t = timed(lab.or_opt, dist, lab.two_opt(dist, start, nl10), nl10)
    print(f"  {'+ Or-opt (k = 10)':>29}: {lab.tour_length(dist, tour):>6}   {t:6.2f} s")
    rand = list(range(1000))
    random.Random(0).shuffle(rand)
    tour, t = timed(lab.two_opt, dist, rand, nl10, dont_look=True)
    print(f"  {"don't-look bits, random start":>29}: {lab.tour_length(dist, tour):>6}   {t:6.2f} s")


def double_bridge(tour, rng):
    n = len(tour)
    a, b, c = sorted(rng.sample(range(1, n), 3))
    return tour[:a] + tour[b:c] + tour[a:b] + tour[c:]


def descend(dist, tour, nl):
    return lab.or_opt(dist, lab.two_opt(dist, tour, nl, dont_look=True), nl)


def multistart(dist, nl, rng, budget, target=None):
    t0, best, best_len = time.perf_counter(), None, math.inf
    while time.perf_counter() - t0 < budget:
        tour = list(range(len(dist)))
        rng.shuffle(tour)
        tour = descend(dist, tour, nl)
        length = lab.tour_length(dist, tour)
        if length < best_len:
            best, best_len = tour, length
            if target is not None and best_len <= target:
                return best_len, time.perf_counter() - t0
    return (best_len, None) if target is not None else best_len


def ils(dist, nl, rng, budget, target=None):
    t0 = time.perf_counter()
    best = descend(dist, lab.nearest_neighbour_tour(dist, rng.randrange(len(dist))), nl)
    best_len = lab.tour_length(dist, best)
    while time.perf_counter() - t0 < budget:
        if target is not None and best_len <= target:
            return best_len, time.perf_counter() - t0
        cand = descend(dist, double_bridge(best, rng), nl)
        length = lab.tour_length(dist, cand)
        if length <= best_len:
            best, best_len = cand, length
    if target is not None:
        return best_len, (time.perf_counter() - t0 if best_len <= target else None)
    return best_len


SA_START = 0.5      # starting temperature as a fraction of the mean edge; tune_annealing() sets it


def tune_annealing(budget):
    """Pick the starting temperature on a separate training instance, never on the test instances."""
    global SA_START
    dist = uniform_tsp(200, 999)
    nl = lab.neighbour_lists(dist, 10)
    scores = {}
    for frac in (0.05, 0.2, 0.8, 3.2):
        SA_START = frac
        scores[frac] = statistics.mean(annealing(dist, nl, random.Random(s), budget) for s in range(2))
    SA_START = min(scores, key=scores.get)
    print("  annealing start temperature tuned on a training instance (fraction of mean edge: mean length): "
          + ", ".join(f"{f}: {v:.0f}" for f, v in scores.items()) + f"  ->  {SA_START}")


def annealing(dist, nl, rng, budget, target=None, chunks=20):
    """One geometric cooling schedule from SA_START to SA_START / 1000 of the mean edge, sized to the budget
    by a short calibration run and split into chunks; after each chunk the best tour so far is polished with
    2-opt and Or-opt (which is when the target is checked)."""
    t0 = time.perf_counter()
    n = len(dist)
    cur = lab.nearest_neighbour_tour(dist, rng.randrange(n))
    mean_edge = lab.tour_length(dist, cur) / n
    _, t_cal = timed(lab.simulated_annealing, dist, cur, random.Random(0), 2000, 1.0, 1.0)
    per = max(1000, int(2000 * 0.8 * budget / t_cal / chunks))
    hot, cold = SA_START * mean_edge, SA_START * mean_edge / 1000
    best, best_len = cur, lab.tour_length(dist, cur)
    for k in range(chunks):
        ta, tb = hot * (cold / hot) ** (k / chunks), hot * (cold / hot) ** ((k + 1) / chunks)
        cur, _ = lab.simulated_annealing(dist, cur, rng, per, ta, tb)
        polished = descend(dist, cur, nl)
        length = lab.tour_length(dist, polished)
        if length < best_len:
            best, best_len = polished, length
        if target is not None and best_len <= target:
            return best_len, time.perf_counter() - t0
        if time.perf_counter() - t0 > budget:
            break
    return (best_len, None) if target is not None else best_len


def ortools_tsp(dist, seconds):
    n = len(dist)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    model = pywrapcp.RoutingModel(manager)
    cost = model.RegisterTransitCallback(lambda i, j: dist[manager.IndexToNode(i)][manager.IndexToNode(j)])
    model.SetArcCostEvaluatorOfAllVehicles(cost)
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = seconds
    return model.SolveWithParameters(params).ObjectiveValue()


def equal_budget():
    budget = 3
    print(f"\n2. TSP, n = 200, 10 instances, {budget} s each: % above the best tour any method found\n")
    tune_annealing(budget)
    try:
        import elkai
    except ImportError:
        elkai = None
    methods = {"multi-start 2-opt+Or": multistart, "annealing": annealing, "ILS (double bridge)": ils}
    results = {name: [] for name in list(methods) + ["OR-Tools GLS"] + (["LKH (elkai)"] if elkai else [])}
    for seed in range(10):
        dist = uniform_tsp(200, seed + 1000)
        nl = lab.neighbour_lists(dist, 10)
        row = {name: f(dist, nl, random.Random(seed), budget) for name, f in methods.items()}
        row["OR-Tools GLS"] = ortools_tsp(dist, budget)
        if elkai:
            tour = elkai.DistanceMatrix([list(r) for r in dist]).solve_tsp()
            row["LKH (elkai)"] = lab.tour_length(dist, tour[:-1])
        best = min(row.values())
        for name, v in row.items():
            results[name].append(100 * (v - best) / best)
    for name, gaps in results.items():
        wins = sum(1 for g in gaps if g == 0)
        print(f"  {name:>22}: mean {statistics.mean(gaps):5.2f}%   worst {max(gaps):5.2f}%   best on {wins}/10")
    if not elkai:
        print("  (LKH not installed; the elkai hook above is untested)")


def ttt():
    cap, seeds = 4.0, 30
    dist = uniform_tsp(150, 77)
    nl = lab.neighbour_lists(dist, 10)
    reference = min(ils(dist, nl, random.Random(s), 5) for s in range(3))
    target = math.floor(1.005 * reference)
    print(f"\n3. Time to target: n = 150, target {target} (0.5% above {reference}, the best of three 5-second ILS runs),"
          f" {seeds} seeds, cap {cap:.0f} s\n")
    nl6 = lab.neighbour_lists(dist, 6)
    runs = {"multi-start": multistart, "annealing": annealing, "ILS": ils,
            "ILS, k = 6": lambda d, _nl, rng, budget, target: ils(d, nl6, rng, budget, target)}
    times = {}
    for name, f in runs.items():
        times[name] = [f(dist, nl, random.Random(1000 + s), cap, target)[1] for s in range(seeds)]
        done = [t for t in times[name] if t is not None]
        med = statistics.median(done) if done else float("nan")
        print(f"  {name:>12}: reached target {len(done):>2}/{seeds}   median {med:5.2f} s   "
              f"quartiles {statistics.quantiles(done, n=4)[0]:.2f}–{statistics.quantiles(done, n=4)[2]:.2f} s"
              if len(done) >= 2 else f"  {name:>12}: reached target {len(done):>2}/{seeds}")
    print("\n  Mann-Whitney on run times (failures counted as the cap), alpha = 0.05:")
    names = list(runs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = [t if t is not None else cap for t in times[names[i]]]
            b = [t if t is not None else cap for t in times[names[j]]]
            _, p = lab.mann_whitney(a, b)
            v = lab.verdict(a, b)
            winner = names[i] if v == "a" else names[j] if v == "b" else "no winner declared"
            print(f"    {names[i]:>12} vs {names[j]:<12} p = {p:.4f}   {winner}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        OUT.mkdir(exist_ok=True)
        fig, ax = plt.subplots(figsize=(6, 4))
        for name in names:
            pts = lab.ttt_points(times[name])
            if pts:
                ax.step([0] + [x for x, _ in pts], [0] + [y for _, y in pts], where="post", label=name)
        ax.set_xlabel("seconds to reach target")
        ax.set_ylabel("probability")
        ax.set_xlim(0, cap)
        ax.set_ylim(0, 1)
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "ttt.png", dpi=130)
        print(f"\n  plot: {OUT / 'ttt.png'}")
    except ImportError:
        pass


def ortools_cvrp(cv, seconds):
    n = cv.n
    manager = pywrapcp.RoutingIndexManager(n + 1, n, 0)
    model = pywrapcp.RoutingModel(manager)
    cost = model.RegisterTransitCallback(lambda i, j: cv.dist[manager.IndexToNode(i)][manager.IndexToNode(j)])
    model.SetArcCostEvaluatorOfAllVehicles(cost)
    demand = model.RegisterUnaryTransitCallback(lambda i: cv.demand[manager.IndexToNode(i)])
    model.AddDimensionWithVehicleCapacity(demand, 0, [cv.capacity] * n, True, "load")
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = seconds
    return model.SolveWithParameters(params).ObjectiveValue()


def cvrp():
    budget = 10
    print(f"\n4. CVRP, n = 60, capacity 30, {budget} s each (5 instances)\n")
    print(f"  {'seed':>4} {'greedy insertion':>17} {'ALNS':>6} {'iterations':>11} {'ALNS s':>9} {'OR-Tools GLS':>13}")
    for seed in range(5):
        cv = CVRP.random(60, seed=seed, capacity=30)
        greedy = lab.solution_cost(cv, lab.greedy_insertion(cv, [], list(range(1, 61))))
        # calibrate iterations to the budget with a short run
        _, t = timed(lab.alns, cv, 50, random.Random(seed))
        iters = max(50, int(50 * budget / t))
        (_, cost, _), secs = timed(lab.alns, cv, iters, random.Random(seed))
        print(f"  {seed:>4} {greedy:>17} {cost:>6} {iters:>11} {secs:>9.1f} {ortools_cvrp(cv, budget):>13}")


if __name__ == "__main__":
    speedups()
    equal_budget()
    ttt()
    cvrp()
