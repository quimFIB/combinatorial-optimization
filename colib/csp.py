"""Constraint-satisfaction instance generators (units 19, 20, 21).

Quasigroup completion (QCP): a Latin square of order n with a fraction of its cells
blanked; fill the blanks so every row and column is a permutation. Gomes, Selman and
Crato (1997) used it to exhibit heavy-tailed runtime distributions in backtracking search.
The square here comes from shuffling the rows, columns and symbols of the cyclic group
table, so every instance is satisfiable (the original square is a solution).
"""

from __future__ import annotations

import random


def latin_square(n: int, seed=0):
    r = random.Random(seed)
    rows, cols, syms = list(range(n)), list(range(n)), list(range(n))
    r.shuffle(rows)
    r.shuffle(cols)
    r.shuffle(syms)
    return [[syms[(rows[i] + cols[j]) % n] for j in range(n)] for i in range(n)]


def quasigroup_completion(n: int, holes: float, seed=0):
    """An n x n grid with None in the blanked cells (a fraction `holes` of them)."""
    r = random.Random(seed + 7919)
    square = latin_square(n, seed)
    cells = [(i, j) for i in range(n) for j in range(n)]
    r.shuffle(cells)
    blank = set(cells[:int(round(holes * n * n))])
    return [[None if (i, j) in blank else square[i][j] for j in range(n)] for i in range(n)]
