"""Tests for unit 27. Run with `uv run co test 27`. You should not need to edit this."""

import math
import random
import tempfile
from pathlib import Path

import pytest

from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def optimum(sizes, capacity):
    """Exact bin packing by DP over subsets: best[mask] = (bins used, load of the last open bin)."""
    n = len(sizes)
    best = [None] * (1 << n)
    best[0] = (1, 0)
    for mask in range(1 << n):
        if best[mask] is None:
            continue
        bins, load = best[mask]
        for i in range(n):
            if mask >> i & 1:
                continue
            cand = (bins, load + sizes[i]) if load + sizes[i] <= capacity else (bins + 1, sizes[i])
            nxt = mask | 1 << i
            if best[nxt] is None or cand < best[nxt]:
                best[nxt] = cand
    return best[-1][0] if n else 0


def instance(seed, n_low=5, n_high=10, capacity=100):
    r = random.Random(seed)
    return [r.randint(10, 70) for _ in range(r.randint(n_low, n_high))], capacity


def solve(model, seconds=60):
    model.setParam("limits/time", seconds)
    model.optimize()
    assert model.getStatus() == "optimal", model.getStatus()
    return round(model.getObjVal())


def lp_value(model):
    model.optimize()
    return model.getObjVal()


def packing_is_valid(sizes, capacity, bins):
    items = sorted(i for b in bins for i in b)
    return items == list(range(len(sizes))) and all(sum(sizes[i] for i in b) <= capacity for b in bins) and all(bins)


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize("linked", [False, True])
def test_step1_assignment_model_optimum(seed, linked):
    sizes, C = instance(seed)
    m, x, y = lab.assignment_model(sizes, C, len(sizes), linked=linked)
    assert len(x) == len(sizes) ** 2 and len(y) == len(sizes)
    assert solve(m) == optimum(sizes, C)


@pytest.mark.parametrize("seed", range(8))
def test_step1_lp_bounds(seed):
    sizes, C = instance(seed + 20)
    unlinked = lp_value(lab.assignment_model(sizes, C, len(sizes), linked=False, vtype="C")[0])
    linked = lp_value(lab.assignment_model(sizes, C, len(sizes), linked=True, vtype="C")[0])
    assert unlinked == pytest.approx(1.0, abs=1e-6), "x <= y alone lets every y be 1/nbins"
    assert linked == pytest.approx(sum(sizes) / C, abs=1e-6), "linking gives the continuous bound sum/capacity"


def test_step1_row_counts():
    sizes = [30, 40, 50]
    m, _, _ = lab.assignment_model(sizes, 100, 3, linked=False)
    assert m.getNConss() == 3 + 3 + 9
    m, _, _ = lab.assignment_model(sizes, 100, 3, linked=True)
    assert m.getNConss() == 3 + 3


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(10))
def test_step2_symmetry_breaking_keeps_the_optimum(seed):
    sizes, C = instance(seed + 40)
    m, x, y = lab.assignment_model(sizes, C, len(sizes))
    lab.add_symmetry_breaking(m, x, y, len(sizes))
    assert solve(m) == optimum(sizes, C)


def test_step2_symmetric_copies_are_cut_off():
    sizes = [60, 60, 30]
    # item 1 in bin 2 is forbidden (bins 0..1 only); and bin 1 used while bin 0 is empty is forbidden
    m, x, y = lab.assignment_model(sizes, 100, 3)
    lab.add_symmetry_breaking(m, x, y, 3)
    m.addCons(x[1, 2] == 1)
    m.optimize()
    assert m.getStatus() == "infeasible"
    m, x, y = lab.assignment_model(sizes, 100, 3)
    lab.add_symmetry_breaking(m, x, y, 3)
    m.addCons(y[0] == 0)
    m.addCons(y[1] == 1)
    m.optimize()
    assert m.getStatus() == "infeasible"
    m, x, y = lab.assignment_model(sizes, 100, 3)
    lab.add_symmetry_breaking(m, x, y, 3)
    m.addCons(x[0, 0] == 1)
    m.addCons(x[1, 1] == 1)
    m.addCons(x[2, 0] == 1)
    assert solve(m) == 2, "a packing in canonical order is still allowed"


# ---------------------------------------------------------------- step 3 ---

def test_step3_first_fit_decreasing():
    assert lab.first_fit_decreasing([50, 70, 30, 20, 50], 100) == [[1, 2], [0, 4], [3]]
    assert lab.first_fit_decreasing([], 100) == []


@pytest.mark.parametrize("seed", range(20))
def test_step3_ffd_and_l2(seed):
    sizes, C = instance(seed + 60, 4, 11)
    bins = lab.first_fit_decreasing(sizes, C)
    opt = optimum(sizes, C)
    assert packing_is_valid(sizes, C, bins)
    assert len(bins) <= 11 / 9 * opt + 6 / 9 + 1e-9
    l2 = lab.lower_bound_l2(sizes, C)
    assert math.ceil(sum(sizes) / C) <= l2 <= opt


def test_step3_l2_beats_the_continuous_bound():
    # six items just over half a bin: sum/C = 3.06 rounds up to 4, but each needs its own bin
    sizes = [51] * 6
    assert lab.lower_bound_l2(sizes, 100) == 6
    # the J3 term: 2 big items leave 2 * 30 free; six items of 30 need 180 - 60 = 120 more, so 2 more bins
    assert lab.lower_bound_l2([70, 70] + [30] * 6, 100) == 4
    # continuous bound 4, optimum 5: these need alpha > 0, the boundary s = capacity - alpha in J2, and s = alpha in J3
    for sizes in ([90, 80, 80, 45, 45, 40, 10], [80, 80, 60, 55, 45, 45, 20]):
        assert math.ceil(sum(sizes) / 100) == 4 and optimum(sizes, 100) == 5
        assert lab.lower_bound_l2(sizes, 100) == 5


@pytest.mark.parametrize("seed", range(8))
def test_step3_bounded_model(seed):
    sizes, C = instance(seed + 90, 6, 11)
    m, x, y = lab.bounded_model(sizes, C)
    ffd = len(lab.first_fit_decreasing(sizes, C))
    assert len(y) == ffd
    fixed = sum(1 for v in y if v.getLbOriginal() >= 0.5)
    assert fixed == min(ffd, lab.lower_bound_l2(sizes, C))
    assert solve(m) == optimum(sizes, C)


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(6))
def test_step4_mip_start(seed):
    sizes, C = instance(seed + 120, 8, 11)
    bins = lab.first_fit_decreasing(sizes, C)
    m, x, y = lab.bounded_model(sizes, C)
    assert lab.add_start(m, x, y, bins)
    m.setHeuristics(3)                      # SCIP_PARAMSETTING_OFF: no heuristics, so the start must be used
    m.setParam("limits/nodes", 1)
    m.setParam("presolving/maxrounds", 0)
    m.setParam("separating/maxrounds", 0)
    m.setParam("separating/maxroundsroot", 0)
    m.optimize()
    assert m.getNSols() >= 1 and m.getPrimalbound() <= len(bins) + 1e-9


def test_step4_infeasible_start_is_rejected():
    sizes = [60, 60, 30, 30]
    m, x, y = lab.bounded_model(sizes, 100)
    assert not lab.add_start(m, x, y, [[0, 1], [2, 3]]), "an overfull bin"
    m, x, y = lab.assignment_model(sizes, 100, 4)
    assert not lab.add_start(m, x, y, [[0, 2], [1]]), "item 3 unpacked"


def test_step4_start_is_renumbered_for_symmetry_breaking():
    sizes = [60, 60, 30, 30]
    m, x, y = lab.bounded_model(sizes, 100)
    assert lab.add_start(m, x, y, [[1, 3], [0, 2]]), "the bin holding item 0 must become bin 0"


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(10))
def test_step5_arcflow_optimum(seed):
    sizes, C = instance(seed + 150, 5, 11, capacity=60)
    sizes = [min(s, 60) for s in sizes]
    m, z = lab.arcflow_model(sizes, C)
    assert solve(m) == optimum(sizes, C)


@pytest.mark.parametrize("seed", range(8))
def test_step5_arcflow_lp_is_strong(seed):
    sizes, C = instance(seed + 170, 6, 11, capacity=60)
    sizes = [min(s, 60) for s in sizes]
    lp = lp_value(lab.arcflow_model(sizes, C, vtype="C")[0])
    linked = lp_value(lab.assignment_model(sizes, C, len(sizes), vtype="C")[0])
    assert linked - 1e-6 <= lp <= optimum(sizes, C) + 1e-6


def test_step5_arcflow_lp_sees_what_the_assignment_lp_cannot():
    sizes = [51, 51, 51]
    assert lp_value(lab.assignment_model(sizes, 100, 3, vtype="C")[0]) == pytest.approx(1.53)
    assert lp_value(lab.arcflow_model(sizes, 100, vtype="C")[0]) == pytest.approx(3.0), "no path fits two 51s"


def test_step5_arcflow_size():
    m, z = lab.arcflow_model([3, 3, 5], 10)
    # item arcs: size 3 from d = 0..7 (8), size 5 from d = 0..5 (6); loss arcs 10; plus z
    assert m.getNVars() == 8 + 6 + 10 + 1
    # flow out of 0, into 10, conservation at 1..9, one demand constraint per distinct size
    assert m.getNConss() == 2 + 9 + 2
    assert solve(m) == 2


# ---------------------------------------------------------------- step 6 ---

def run_with_statistics(sizes, C, seconds):
    m, x, y = lab.assignment_model(sizes, C, len(sizes) // 2 + 2)
    m.setParam("limits/time", seconds)
    m.optimize()
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "stats.txt"
        m.writeStatistics(str(path))
        return m, path.read_text()


def test_step6_parse_a_live_report():
    r = random.Random(3)
    sizes = [r.randint(20, 60) for _ in range(24)]
    m, text = run_with_statistics(sizes, 100, 2)
    stats = lab.parse_statistics(text)
    assert stats["nodes"] == m.getNTotalNodes()
    assert stats["primal_bound"] == pytest.approx(m.getPrimalbound())
    assert stats["dual_bound"] == pytest.approx(m.getDualbound(), rel=1e-6)
    gap = m.getGap()
    assert (stats["gap_percent"] is None) == math.isinf(gap)
    if stats["gap_percent"] is not None:
        assert stats["gap_percent"] == pytest.approx(100 * gap, abs=0.01)
    assert stats["first_lp_value"] == pytest.approx(sum(sizes) / 100, abs=1e-6)
    if stats["found_by"] is not None and stats["found_by"] in stats["heuristics_best"]:
        assert stats["heuristics_best"][stats["found_by"]] >= 1
    assert all(isinstance(v, int) and v > 0 for v in stats["cuts_applied"].values())


REPORT = """SCIP Status        : problem is solved [optimal solution found]
Separators         :   ExecTime  SetupTime      Calls  RootCalls    Cutoffs    DomReds  FoundCuts ViaPoolAdd  DirectAdd    Applied ViaPoolApp  DirectApp      Conss
  cut pool         :       0.48          -        687         21          -          -       5737      73292          -          -          -          -          -    (maximal pool size:       3339)
  aggregation      :       0.14       0.00         55         11          0          0       2135      47953         17       4597       4591          6          0
  > cmir           :          -          -          -          -          -          -          -      42135          0       3392       3392          0          -
  > flowcover      :          -          -          -          -          -          -          -       4037          0        711        711          0          -
  cgmip            :       0.00       0.00          0          0          0          0          0          0          0          0          0          0          0
  gomory           :       0.68       0.00         55         10          0          0       3703      23304        161        287        287          0          0
Primal Heuristics  :   ExecTime  SetupTime      Calls      Found       Best
  LP solutions     :       0.00          -          -          0          0
  clique           :       0.00       0.00          1          1          1
  crossover        :       0.02       0.00          2          2          0
  shiftandpropagate:       0.01       0.00          1          3          2
B&B Tree           :
  number of runs   :          1
  nodes            :       1347 (1129 internal, 218 leaves)
  nodes (total)    :       1350 (1129 internal, 221 leaves)
Root Node          :
  First LP value   : +1.33400000000000e+01
Solution           :
  Solutions found  :        162 (1 improvements)
  Primal Bound     : +1.40000000000000e+01   (in run 1, after 9 nodes, 0.04 seconds, depth 3, found by <shiftandpropagate>)
  Dual Bound       : +1.40000000000000e+01
  Gap              :       0.00 %
"""


def test_step6_parse_a_fixed_report():
    stats = lab.parse_statistics(REPORT)
    assert stats["nodes"] == 1350, "nodes (total), not nodes"
    assert stats["cuts_applied"] == {"aggregation": 4597, "gomory": 287}
    assert stats["heuristics_best"] == {"clique": 1, "shiftandpropagate": 2}
    assert stats["found_by"] == "shiftandpropagate"
    assert (stats["primal_bound"], stats["dual_bound"], stats["gap_percent"]) == (14.0, 14.0, 0.0)
    assert stats["first_lp_value"] == 13.34


def test_step6_infinite_gap():
    text = REPORT.replace("       0.00 %", "   infinite").replace("found by <shiftandpropagate>)", "found by <relaxation>)")
    stats = lab.parse_statistics(text)
    assert stats["gap_percent"] is None and stats["found_by"] == "relaxation"
