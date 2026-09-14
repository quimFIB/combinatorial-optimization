"""Unit 00 — "Then": find the wall.

Unit 00 has no solver to compare against; the thing to measure is the oracle
itself. This times *your* brute_force on three spaces — 2^n, (n-1)!, B(n) —
until each takes a few seconds, then extrapolates how large n can get in a
minute, an hour, and a year. Those three numbers are the budget every later
unit's small-instance testing lives inside.

    uv run co then 00             # your lab
    uv run co then 00 --solution  # the reference
"""

import math
import time
from pathlib import Path

from colib import TSP, BinPacking, VertexCover
from colib.spaces import bell
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"
BUDGET = 3.0      # seconds; stop growing n once one solve takes this long

FAMILIES = [
    ("vertex cover   2^n", VertexCover, lambda n: 2 ** n, range(4, 30)),
    ("TSP        (n-1)!", TSP, lambda n: math.factorial(n - 1), range(4, 14)),
    ("bin packing  B(n)", BinPacking, bell, range(4, 16)),
]


def main():
    OUT.mkdir(exist_ok=True)
    print(__doc__.split("\n\n")[1] + "\n")
    print(f"{'space':<20}{'n':>4}{'candidates':>16}{'seconds':>10}{'µs/cand':>10}")
    results = {}
    for label, cls, size, ns in FAMILIES:
        pts = []
        for n in ns:
            p = cls.random(n, seed=0)
            t = time.perf_counter()
            lab.brute_force(p)
            dt = time.perf_counter() - t
            pts.append((n, size(n), dt))
            print(f"{label:<20}{n:>4}{size(n):>16,}{dt:>10.3f}{1e6 * dt / size(n):>10.2f}")
            if dt > BUDGET:
                break
        results[label] = pts

    print("\nlargest n that fits in …  (extrapolated from µs/candidate at the last size)")
    print(f"{'space':<20}{'1 minute':>10}{'1 hour':>10}{'1 year':>10}")
    for label, cls, size, _ in FAMILIES:
        n, cands, dt = results[label][-1]
        per = dt / cands
        row = []
        for budget in (60, 3600, 3600 * 24 * 365):
            m = n
            while size(m + 1) * per <= budget:
                m += 1
            while m > 1 and size(m) * per > budget:
                m -= 1
            row.append(m)
        print(f"{label:<20}" + "".join(f"{m:>10}" for m in row))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6.5, 4))
        for label, pts in results.items():
            ax.semilogy([p[0] for p in pts], [p[2] for p in pts], "o-", label=label.split()[0] + " " + label.split()[-1])
        ax.axhline(BUDGET, color="grey", ls=":", lw=1)
        ax.set_xlabel("n")
        ax.set_ylabel("seconds (log)")
        ax.set_title("The wall: brute force on three spaces")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "wall.png", dpi=130)
        print(f"\nplot: {(OUT / 'wall.png').relative_to(Path.cwd())}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
