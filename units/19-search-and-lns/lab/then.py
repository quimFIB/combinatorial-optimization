"""Unit 19 — "Then": runtime distributions, LNS, and what CP-SAT and OR-Tools routing do.

  1. 100 seeds of randomised first-fail on a heavy-tailed and a light-tailed quasigroup
     completion instance: plain, Luby restarts, and dom/wdeg with restarts. Histograms.
  2. LNS against branch and bound with the same node budget, on random job-shops.
  3. CP-SAT on a 30 x 15 job-shop for 10 seconds: 8 workers with LNS, 8 without, 1 worker.
  4. OR-Tools' routing solver (guided local search) on CVRP against unit 10's LP bound.

    uv run co then 19
"""

import random
import time

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from ortools.sat.python import cp_model

from colib.colgen import CVRP
from colib.csp import quasigroup_completion
from colib.problems import JobShop
from colib.ref import unit
from colib.testing import load_lab

lab = load_lab(__file__)
cp = unit("17")
gc = unit("18")
SEEDS = 100
CAP = 3000


def histogram(samples, bins=(1, 16, 32, 64, 128, 256, 512, 1024, 2048, CAP, CAP + 1)):
    counts = [0] * (len(bins) - 1)
    for nodes, _ in samples:
        for b in range(len(bins) - 1):
            if bins[b] <= nodes < bins[b + 1]:
                counts[b] += 1
                break
    labels = [f"{bins[b]}–{bins[b + 1] - 1}" if b < len(bins) - 2 else f"cap {CAP}" for b in range(len(bins) - 1)]
    return "\n".join(f"      {lab_:>10} {'█' * c}{' ' + str(c) if c else ''}" for lab_, c in zip(labels, counts))


def distributions():
    print(f"1. Runtime distributions: {SEEDS} seeds, node cap {CAP}\n")
    for name, grid in (("heavy: QCP(12, 55%, #0)", quasigroup_completion(12, 0.55, 0)),
                       ("light: QCP(12, 58%, #3)", quasigroup_completion(12, 0.58, 3))):
        domains, props = lab.qcp_model(grid)

        def plain(s):
            sols, st = cp.solve(domains, props, choose=lab.random_first_fail(random.Random(s)), node_limit=CAP)
            return bool(sols), st.nodes

        def luby(s):
            sol, st = lab.solve_with_restarts(domains, props, lab.random_first_fail(random.Random(s)), base=30,
                                              node_budget=CAP)
            return sol is not None, st.nodes

        def wdeg(s):
            h = lab.DomWDeg(props, random.Random(s))
            sol, st = lab.solve_with_restarts(domains, props, h.choose, h.on_failure, base=30, node_budget=CAP)
            return sol is not None, st.nodes

        print(f"  {name}")
        for label, run in (("random first-fail", plain), ("  + Luby restarts (base 30)", luby),
                           ("dom/wdeg + Luby restarts", wdeg)):
            t = time.perf_counter()
            samples = lab.runtime_distribution(run, range(SEEDS))
            s = lab.summarise(samples)
            print(f"    {label:<28} solved {s['solved']:>5.0%}  mean {s['mean']:>7.1f}  median {s['median']:>5}"
                  f"  p90 {s['p90']:>5}  max {s['max']:>5}  p90/median {s['tail']:>5.1f}  ({time.perf_counter() - t:.1f} s)")
            if label in ("random first-fail", "  + Luby restarts (base 30)"):
                print(histogram(samples))
        print()


def lns_vs_bb():
    print("2. LNS vs branch and bound, same node budget (150 iterations x 150 nodes)\n")
    print(f"  {'instance':<22} {'greedy':>6} {'LNS':>5} {'s':>6} | {'B&B':>5} {'s':>6}")
    for n, machines, seed in ((8, 4, 0), (10, 5, 1), (12, 6, 2)):
        shop = JobShop.random(n, seed=seed, machines=machines)
        horizon = sum(d for job in shop.jobs for _, d in job)
        t = time.perf_counter()
        best, starts, trace = lab.lns_jobshop(shop, horizon, iterations=150, node_limit=150, seed=0)
        tl = time.perf_counter() - t
        t = time.perf_counter()
        bb, _, stats, _ = gc.minimise(*gc.jobshop(shop, horizon, True), node_limit=150 * 150)
        tb = time.perf_counter() - t
        print(f"  {f'{n} jobs x {machines} machines':<22} {trace[0][1]:>6} {best:>5} {tl:>6.1f} |"
              f" {bb if bb is not None else '—':>5} {tb:>6.1f}")


def cpsat_jobshop():
    print("\n3. CP-SAT on a 30 x 15 Taillard-style job-shop (durations 1–99), 10 seconds each\n")
    r = random.Random(11)
    jobs = []
    for _ in range(30):
        order = list(range(15))
        r.shuffle(order)
        jobs.append(tuple((m, r.randint(1, 99)) for m in order))
    shop = JobShop(tuple(jobs))
    for label, workers, use_lns in (("8 workers, LNS on", 8, True), ("8 workers, LNS off", 8, False),
                                    ("1 worker", 1, True)):
        m = cp_model.CpModel()
        H = sum(d for job in shop.jobs for _, d in job)
        per, ends = {k: [] for k in range(shop.machines)}, []
        for job in shop.jobs:
            prev = None
            for mach, d in job:
                s = m.new_int_var(0, H, "")
                per[mach].append(m.new_interval_var(s, d, s + d, ""))
                if prev is not None:
                    m.add(s >= prev)
                prev = s + d
            ends.append(prev)
        for ivs in per.values():
            m.add_no_overlap(ivs)
        mk = m.new_int_var(0, H, "")
        m.add_max_equality(mk, ends)
        m.minimize(mk)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        solver.parameters.num_workers = workers
        solver.parameters.use_lns = use_lns
        status = solver.solve(m)
        print(f"  {label:<20} makespan {solver.objective_value:>5.0f}  bound {solver.best_objective_bound:>5.0f}"
              f"  {'optimal' if status == cp_model.OPTIMAL else 'not proven'}")


def routing():
    print("\n4. CVRP: OR-Tools routing (guided local search, 5 s) against unit 10's LP bound\n")
    u10 = unit("10")
    print(f"  {'n':>3} {'LP bound':>9} {'routing':>8} {'gap':>6}")
    for n in (12, 16, 20):
        cv = CVRP.random(n, seed=n, capacity=20)
        lp, _, _ = u10.vrp_column_generation(cv)
        manager = pywrapcp.RoutingIndexManager(n + 1, n, 0)
        model = pywrapcp.RoutingModel(manager)
        cost = model.RegisterTransitCallback(lambda i, j: cv.dist[manager.IndexToNode(i)][manager.IndexToNode(j)])
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        demand = model.RegisterUnaryTransitCallback(lambda i: cv.demand[manager.IndexToNode(i)])
        model.AddDimensionWithVehicleCapacity(demand, 0, [cv.capacity] * n, True, "load")
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        params.time_limit.seconds = 5
        sol = model.SolveWithParameters(params)
        value = sol.ObjectiveValue()
        print(f"  {n:>3} {lp:>9.2f} {value:>8} {100 * (value - lp) / value:>5.1f}%")


if __name__ == "__main__":
    distributions()
    lns_vs_bb()
    cpsat_jobshop()
    routing()
