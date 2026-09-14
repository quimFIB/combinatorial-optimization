"""Shared scaffolding for the curriculum.

Everything here is *not the lesson*: instance generators, the reference
brute-force oracle, the differential harness, file formats and the lab runner.
Labs import it so that each unit's hand-written code can stay small and be
about the one algorithm the unit teaches.
"""

from colib.problems import (
    PROBLEMS,
    Assignment,
    BinPacking,
    GraphColouring,
    JobShop,
    Knapsack,
    MaxCut,
    SetCover,
    TSP,
    VertexCover,
)
from colib.oracle import Result, brute_force
from colib.harness import Disagreement, differential, instances

__all__ = [
    "PROBLEMS", "Assignment", "BinPacking", "GraphColouring", "JobShop",
    "Knapsack", "MaxCut", "SetCover", "TSP", "VertexCover",
    "Result", "brute_force", "Disagreement", "differential", "instances",
]
