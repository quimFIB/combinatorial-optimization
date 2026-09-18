"""Unit 28 — "Then": auditing two earlier conclusions through your harness.

  1. Unit 07 said, from totals over three instances: strong branching uses the fewest nodes, pseudocost is the
     fastest. Re-run on 24 knapsacks: shifted geometric means, performance profiles, per-instance wins, paired
     Wilcoxon tests with Holm correction, and bootstrap intervals for the time ratios.
  2. Unit 19 said, from one instance and 100 seeds: Luby restarts cut the mean node count on a heavy-tailed
     quasigroup instance from 153.6 to 52.1, and make the median worse. Re-run with bootstrap intervals, then on
     eight more instances of the same family.

Runs are stored in lab/out/bench.sqlite, so a second run of this script re-analyses without re-solving.
Delete the file to measure again.

    uv run co then 28
"""

import math
import random
import statistics
from pathlib import Path

from colib.bb import multi_knapsack
from colib.csp import quasigroup_completion
from colib.ref import unit
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"
bb = unit("07")
cp = unit("17")
search = unit("19")


def branching():
    print("1. Unit 07's branching rules, re-run on 24 multi-dimensional knapsacks (18-22 items, 3 constraints)\n")
    conn = lab.open_store(str(OUT / "bench.sqlite"))
    rules = {"most-fractional": bb.most_fractional, "pseudocost": bb.pseudocost, "strong": bb.strong_branching}
    instances = {f"mk{n}x3#{s}": (n, s) for n in (18, 20, 22) for s in range(8)}
    LIMIT_NODES, TIMEOUT = 20_000, 120.0

    def solver(rule):
        def solve(data, seed, timeout):
            n, s = data
            r = bb.branch_and_bound(multi_knapsack(n, 3, s), rule, "best", node_limit=LIMIT_NODES)
            return {"status": r.status, "value": r.value, "nodes": r.nodes}
        return solve

    done = lab.run_benchmark(conn, "u07-branching", {k: solver(v) for k, v in rules.items()}, instances, [0], TIMEOUT)
    runs = lab.load_runs(conn, "u07-branching")
    print(f"  ({done} new runs; {len(runs)} in the store)")
    names = list(rules)
    by = {s: {r["instance"]: r for r in runs if r["solver"] == s} for s in names}
    insts = sorted(instances)
    print(f"\n  {'rule':>16} {'solved':>7} {'total nodes':>12} {'SGM nodes':>10} {'total s':>8} {'SGM s':>7}"
          f" {'fewest nodes':>13} {'fastest':>8}")
    for s in names:
        nodes = [by[s][i]["nodes"] for i in insts]
        secs = [lab.par_seconds(by[s][i], TIMEOUT) for i in insts]
        fewest = sum(1 for i in insts if by[s][i]["nodes"] == min(by[t][i]["nodes"] for t in names))
        fastest = sum(1 for i in insts if lab.virtual_best([by[t][i] for t in names])[(i, 0)][0] == s)
        print(f"  {s:>16} {sum(by[s][i]['status'] == 'optimal' for i in insts):>4}/24 {sum(nodes):>12} "
              f"{lab.shifted_geometric_mean(nodes, 10):>10.0f} {sum(secs):>8.1f} {lab.shifted_geometric_mean(secs, 0.1):>7.2f}"
              f" {fewest:>13} {fastest:>8}")
    taus = [1, 1.25, 1.5, 2, 3, 5, 10]
    prof = lab.performance_profile(runs, taus)
    print("\n  performance profile on seconds, fraction of instances within tau of the fastest:")
    print("  " + " " * 16 + "".join(f"{t:>7}" for t in taus))
    for s in names:
        print(f"  {s:>16}" + "".join(f"{v:>7.2f}" for v in prof[s]))
    pairs = [("strong", "pseudocost"), ("strong", "most-fractional"), ("pseudocost", "most-fractional")]
    for metric, key, shift in (("nodes", "nodes", 10.0), ("seconds", "seconds", 0.1)):
        tests = [lab.wilcoxon_signed_rank([by[a][i][key] for i in insts], [by[b][i][key] for i in insts]) for a, b in pairs]
        adjusted = lab.holm([p for _, p in tests])
        print(f"\n  paired on {metric}: geometric-mean ratio with 95% bootstrap interval, Wilcoxon p (Holm-adjusted)")
        for (a, b), (_, p), padj in zip(pairs, tests, adjusted):
            ratio, (lo, hi) = lab.geometric_ratio_ci([by[a][i][key] for i in insts], [by[b][i][key] for i in insts],
                                                     random.Random(0), shift=shift)
            print(f"    {a:>10} / {b:<16} {ratio:6.2f}  [{lo:.2f}, {hi:.2f}]   p = {p:.4f} ({padj:.4f})")
    plot_profile(runs, names)


def plot_profile(runs, names):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    taus = [1 + k * 0.05 for k in range(181)]
    prof = lab.performance_profile(runs, taus)
    fig, ax = plt.subplots(figsize=(6, 4))
    for s in names:
        ax.step(taus, prof[s], where="post", label=s)
    ax.set_xlabel("tau (time / fastest time)")
    ax.set_ylabel("fraction of instances")
    ax.set_ylim(0, 1.02)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "profile.png", dpi=130)
    print(f"\n  plot: {OUT / 'profile.png'}")


def restarts():
    print("\n2. Unit 19's restarts, re-run with intervals and on more instances (node cap 3 000)\n")
    CAP = 3000
    conn = lab.open_store(str(OUT / "bench.sqlite"))

    def plain(grid, seed, timeout):
        domains, props = search.qcp_model(grid)
        sols, st = cp.solve(domains, props, choose=search.random_first_fail(random.Random(seed)), node_limit=CAP)
        return {"status": "optimal" if sols else "node_limit", "nodes": st.nodes}

    def luby(grid, seed, timeout):
        domains, props = search.qcp_model(grid)
        sol, st = search.solve_with_restarts(domains, props, search.random_first_fail(random.Random(seed)), base=30,
                                             node_budget=CAP)
        return {"status": "optimal" if sol is not None else "node_limit", "nodes": st.nodes}

    solvers = {"first-fail": plain, "Luby restarts": luby}
    lab.run_benchmark(conn, "u19-original", solvers, {"QCP(12,55%)#0": quasigroup_completion(12, 0.55, 0)},
                      list(range(100)), 1e9)
    runs = lab.load_runs(conn, "u19-original")
    print("  the original instance, 100 seeds: nodes (capped runs count as 3 000)")
    print(f"  {'strategy':>14} {'capped':>7} {'mean':>7} {'95% CI':>18} {'median':>7} {'95% CI':>16}")
    for s in solvers:
        nodes = [r["nodes"] for r in runs if r["solver"] == s]
        m_lo, m_hi = lab.bootstrap_ci(nodes, statistics.mean, random.Random(1))
        d_lo, d_hi = lab.bootstrap_ci(nodes, statistics.median, random.Random(2))
        capped = sum(1 for r in runs if r["solver"] == s and r["status"] != "optimal")
        print(f"  {s:>14} {capped:>7} {statistics.mean(nodes):>7.1f} {f'[{m_lo:.1f}, {m_hi:.1f}]':>18}"
              f" {statistics.median(nodes):>7.1f} {f'[{d_lo:.1f}, {d_hi:.1f}]':>16}")
    plain_nodes = [r["nodes"] for r in runs if r["solver"] == "first-fail"]
    uncapped = [n for n in plain_nodes if n < CAP]
    print(f"  first-fail mean without the capped runs: {statistics.mean(uncapped):.1f} over {len(uncapped)} runs")

    family = {f"QCP(12,55%)#{k}": quasigroup_completion(12, 0.55, k) for k in range(1, 9)}
    lab.run_benchmark(conn, "u19-family", solvers, family, list(range(30)), 1e9)
    runs = lab.load_runs(conn, "u19-family")
    print("\n  eight more instances of the same family, 30 seeds each: mean nodes (capped at 3 000), median, capped runs")
    print(f"  {'instance':>16} {'first-fail mean':>16} {'Luby mean':>10} {'ff median':>10} {'Luby median':>12} {'ff capped':>10} {'Luby capped':>12}")
    means = {s: [] for s in solvers}
    medians = {s: [] for s in solvers}
    for inst in sorted(family):
        row = {}
        for s in solvers:
            rs = [r for r in runs if r["solver"] == s and r["instance"] == inst]
            nodes = [r["nodes"] for r in rs]
            row[s] = (statistics.mean(nodes), statistics.median(nodes), sum(r["status"] != "optimal" for r in rs))
            means[s].append(row[s][0])
            medians[s].append(row[s][1])
        print(f"  {inst:>16} {row['first-fail'][0]:>16.1f} {row['Luby restarts'][0]:>10.1f} {row['first-fail'][1]:>10.1f}"
              f" {row['Luby restarts'][1]:>12.1f} {row['first-fail'][2]:>10} {row['Luby restarts'][2]:>12}")
    _, p_mean = lab.wilcoxon_signed_rank(means["first-fail"], means["Luby restarts"])
    _, p_med = lab.wilcoxon_signed_rank(medians["first-fail"], medians["Luby restarts"])
    better_mean = sum(1 for a, b in zip(means["first-fail"], means["Luby restarts"]) if b < a)
    worse_median = sum(1 for a, b in zip(medians["first-fail"], medians["Luby restarts"]) if b > a)
    print(f"\n  restarts lower the mean on {better_mean}/8 instances (Wilcoxon p = {p_mean:.3f}),"
          f" and raise the median on {worse_median}/8 (p = {p_med:.3f})")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    branching()
    restarts()
