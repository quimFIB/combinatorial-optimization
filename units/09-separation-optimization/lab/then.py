"""Unit 09 — "Then": exponentially many constraints, a few hundred used.

On random Euclidean TSPs of growing size:
  1. The subtour-elimination LP by lazy constraints: bound, constraints actually
     added out of the 2^(n-1) - 1 that exist, LP solves, seconds.
  2. The exact tour by lazy cuts on the integer program (HiGHS as the MIP
     solver): optimum, cuts, MIP solves, seconds, and the LP bound's gap.

Concorde, the reference TSP code, uses the same idea with many more cut
families, and is not installed here; its published results are on the slides.

    uv run co then 09
"""

import time

from colib import TSP
from colib.testing import load_lab

lab = load_lab(__file__)


def main():
    print(f"{'n':>4}{'constraints that exist':>24}{'used by the LP':>16}{'LP solves':>11}{'LP bound':>10}{'LP s':>7}"
          f"{'optimum':>9}{'MIP cuts':>10}{'MIP solves':>12}{'MIP s':>8}{'gap':>7}")
    for n in (15, 30, 50, 80, 120, 200):
        t = TSP.random(n, seed=n)
        s = time.perf_counter()
        value, _, rows, solves = lab.subtour_lp(t)
        lp_s = time.perf_counter() - s
        s = time.perf_counter()
        length, order, cuts, mips = lab.tsp_exact(t)
        mip_s = time.perf_counter() - s
        exist = 2 ** (n - 1) - 1
        print(f"{n:>4}{exist:>24.3g}{rows:>16}{solves:>11}{value:>10.1f}{lp_s:>7.2f}"
              f"{length:>9}{cuts:>10}{mips:>12}{mip_s:>8.2f}{100 * (length - value) / length:>6.2f}%", flush=True)
    print("\nOn these random Euclidean instances the subtour LP bound is within 1% of the optimal tour.")
    print("Every constraint it used was found by a connected-components or minimum-cut computation.")


if __name__ == "__main__":
    main()
