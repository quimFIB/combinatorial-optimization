"""Tests for unit 00. Run with `uv run co test 00`. You should not need to edit this."""

import itertools

import pytest

from colib import (PROBLEMS, BinPacking, Disagreement, JobShop, Knapsack, Result, SetCover,
                   VertexCover, brute_force as reference, differential, instances)
from colib.spaces import bell
from colib.testing import load_lab

lab = load_lab(__file__)


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(6))
def test_step1_vertex_cover_model_matches_reference(seed):
    inst = VertexCover.random(7, seed=seed)
    for x in inst.space():
        assert lab.vertex_cover_feasible(inst, x) == inst.is_feasible(x), f"x={x}"
        if inst.is_feasible(x):
            assert lab.vertex_cover_objective(inst, x) == inst.objective(x), f"x={x}"


@pytest.mark.parametrize("seed", range(6))
def test_step1_bin_packing_model_matches_reference(seed):
    inst = BinPacking.random(7, seed=seed)
    for x in inst.space():
        assert lab.bin_packing_feasible(inst, x) == inst.is_feasible(x), f"x={x}"
        if inst.is_feasible(x):
            assert lab.bin_packing_objective(inst, x) == inst.objective(x), f"x={x}"


def test_step1_edge_cases():
    empty = VertexCover(3, ())
    assert lab.vertex_cover_feasible(empty, (0, 0, 0))
    too_big = BinPacking((120,), 100)
    assert not lab.bin_packing_feasible(too_big, (0,))


# ---------------------------------------------------------------- step 2 ---

def test_step2_small_cases_exactly():
    assert list(lab.set_partitions(0)) == [()]
    assert list(lab.set_partitions(1)) == [(0,)]
    assert sorted(lab.set_partitions(3)) == [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2)]


@pytest.mark.parametrize("n", range(1, 10))
def test_step2_counts_are_bell_numbers_and_each_partition_appears_once(n):
    seen = set()
    for a in lab.set_partitions(n):
        assert len(a) == n and a[0] == 0
        assert all(a[i] <= 1 + max(a[:i]) for i in range(1, n)), f"not restricted growth: {a}"
        blocks = frozenset(frozenset(i for i in range(n) if a[i] == b) for b in set(a))
        assert blocks not in seen, f"partition {a} listed twice"
        seen.add(blocks)
    assert len(seen) == bell(n)


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("cls", PROBLEMS, ids=lambda c: c.__name__)
def test_step3_agrees_with_reference_on_all_nine_problems(cls):
    n = 3 if cls is JobShop else 6
    for seed in range(5):
        p = cls.random(n, seed=seed)
        got, want = lab.brute_force(p), reference(p)
        assert isinstance(got, Result)
        assert got.value == want.value, f"{p}"
        assert got.solution is not None and p.is_feasible(got.solution)
        assert p.objective(got.solution) == want.value
        assert (got.feasible, got.examined) == (want.feasible, want.examined)


def test_step3_infeasible_instance_returns_none():
    p = SetCover(3, (frozenset({0}), frozenset({1})), (1, 1))   # element 2 is uncoverable
    got = lab.brute_force(p)
    assert got.value is None and got.solution is None and got.feasible == 0 and got.examined == 4


def test_step3_respects_sense():
    # maximise: take everything that fits. A min-solver would return the empty set.
    p = Knapsack((5, 4), (1, 1), 2)
    assert lab.brute_force(p).value == 9


# ---------------------------------------------------------------- step 4 ---

PATH4 = VertexCover(4, ((0, 1), (1, 2), (2, 3)))
TRIANGLE = VertexCover(3, ((0, 1), (1, 2), (0, 2)))


def test_step4_valid_matching_gives_its_size():
    assert lab.matching_lower_bound(PATH4, [(0, 1), (2, 3)]) == 2
    assert lab.matching_lower_bound(PATH4, [(1, 0)]) == 1          # orientation is irrelevant
    assert lab.matching_lower_bound(PATH4, []) == 0


def test_step4_invalid_matchings_are_rejected():
    with pytest.raises(ValueError):
        lab.matching_lower_bound(PATH4, [(0, 1), (1, 2)])           # shares vertex 1
    with pytest.raises(ValueError):
        lab.matching_lower_bound(PATH4, [(0, 3)])                   # not an edge


def test_step4_certificate_on_a_path():
    assert lab.certify_vertex_cover(PATH4, (0, 1, 1, 0), [(0, 1), (2, 3)])
    assert not lab.certify_vertex_cover(PATH4, (0, 1, 1, 1), [(0, 1), (2, 3)])  # cover too big
    assert not lab.certify_vertex_cover(PATH4, (0, 1, 0, 0), [(0, 1)])          # not a cover
    assert not lab.certify_vertex_cover(PATH4, (0, 1, 1, 0), [(0, 1), (1, 2)])  # bad matching


def test_step4_the_triangle_has_no_such_certificate():
    """Optimum is 2 but no matching has 2 edges: this certificate can be too weak.
    Units 03 and 15 are about when it is not."""
    edge_sets = itertools.chain.from_iterable(
        itertools.combinations(TRIANGLE.edges, k) for k in range(4))
    for cover in TRIANGLE.space():
        for m in edge_sets:
            assert not lab.certify_vertex_cover(TRIANGLE, cover, list(m))


# ---------------------------------------------------------------- step 5 ---

def test_step5_heuristic_is_always_feasible():
    for p in instances(VertexCover, sizes=range(1, 11), seeds=range(10)):
        x = lab.plausible_vertex_cover(p)
        assert len(x) == p.n and p.is_feasible(x), f"infeasible on {p}"


def test_step5_the_harness_catches_it():
    with pytest.raises(Disagreement) as caught:
        differential(lab.plausible_vertex_cover,
                     instances(VertexCover, sizes=range(1, 13), seeds=range(40)))
    p = caught.value.problem
    print(f"\nsmallest counterexample found: n={p.n}, edges={p.edges}")
