"""The vehicle routing problem with time windows (the capstone), and Solomon's benchmark.

A VRPTW instance: vertex 0 is the depot, 1..n are customers. Customer i has a demand,
a time window [ready_i, due_i] in which service must *start*, and a service duration.
Vehicles of one capacity leave the depot no earlier than ready_0 and must be back by
due_0. A vehicle arriving early waits. The fleet is unlimited, and the objective is
total distance: the convention of the exact-methods literature (Kallehauge et al.
2005; Baldacci, Mingozzi & Roberti 2011), not the hierarchical "vehicles first, then
distance" objective of the heuristic tables.

Numbers are integers in tenths. Coordinates, windows and service times are scaled by
10, and the distance d_ij = floor(10 * euclid(i, j)) is Euclidean distance truncated to
one decimal. Travel time equals distance. Integer data keeps CP-SAT exact and makes
"equal cost" mean equal. Truncation can break the triangle inequality by up to 0.1;
that is why the set-partitioning models use "= 1", not "≥ 1".

Solomon's instances (1987) come from SINTEF's mirror:

    uv run co data            downloads data/solomon/*.txt (83 KB, checksum verified)
    solomon("R101", 25)       the first 25 customers of R101, as the literature uses them

Classes: C (clustered), R (random), RC (mixed); series 1 has short horizons and tight
windows (short routes, many vehicles), series 2 long horizons and wide windows.
"""

from __future__ import annotations

import hashlib
import io
import math
import random
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "solomon"
SOLOMON_URL = "https://www.sintef.no/globalassets/project/top/vrptw/solomon/solomon-100.zip"
SOLOMON_SHA256 = "8a0a72cbe6b7f8f9988ace4ebde0378ec34943acaaac47f2c408915e41887747"
SOLOMON_NAMES = tuple(
    [f"C1{k:02d}" for k in range(1, 10)] + [f"C2{k:02d}" for k in range(1, 9)]
    + [f"R1{k:02d}" for k in range(1, 13)] + [f"R2{k:02d}" for k in range(1, 12)]
    + [f"RC1{k:02d}" for k in range(1, 9)] + [f"RC2{k:02d}" for k in range(1, 9)])

# SINTEF's best known solutions for the 100-customer instances, as (vehicles, distance).
# Hierarchical objective and untruncated double-precision distances, so a distance-only
# solution in tenths is not directly comparable: it may use more vehicles and less distance.
SINTEF_BEST_100 = {
    "C101": (10, 828.94), "C102": (10, 828.94), "C103": (10, 828.06), "C104": (10, 824.78),
    "C105": (10, 828.94), "C106": (10, 828.94), "C107": (10, 828.94), "C108": (10, 828.94),
    "C109": (10, 828.94), "C201": (3, 591.56), "C202": (3, 591.56), "C203": (3, 591.17),
    "C204": (3, 590.60), "C205": (3, 588.88), "C206": (3, 588.49), "C207": (3, 588.29),
    "C208": (3, 588.32), "R101": (19, 1650.80), "R102": (17, 1486.12), "R103": (13, 1292.68),
    "R104": (9, 1007.31), "R105": (14, 1377.11), "R106": (12, 1252.03), "R107": (10, 1104.66),
    "R108": (9, 960.88), "R109": (11, 1194.73), "R110": (10, 1118.84), "R111": (10, 1096.73),
    "R112": (9, 982.14), "R201": (4, 1252.37), "R202": (3, 1191.70), "R203": (3, 939.50),
    "R204": (2, 825.52), "R205": (3, 994.43), "R206": (3, 906.14), "R207": (2, 890.61),
    "R208": (2, 726.82), "R209": (3, 909.16), "R210": (3, 939.37), "R211": (2, 885.71),
    "RC101": (14, 1696.95), "RC102": (12, 1554.75), "RC103": (11, 1261.67), "RC104": (10, 1135.48),
    "RC105": (13, 1629.44), "RC106": (11, 1424.73), "RC107": (11, 1230.48), "RC108": (10, 1139.82),
    "RC201": (4, 1406.94), "RC202": (3, 1365.65), "RC203": (3, 1049.62), "RC204": (3, 798.46),
    "RC205": (4, 1297.65), "RC206": (3, 1146.32), "RC207": (3, 1061.14), "RC208": (3, 828.14),
}


@dataclass(frozen=True)
class VRPTW:
    name: str
    coords: tuple[tuple[int, int], ...]     # scaled by 10
    demand: tuple[int, ...]                 # demand[0] == 0
    ready: tuple[int, ...]                  # ready[0], due[0]: the depot's opening hours
    due: tuple[int, ...]
    service: tuple[int, ...]                # service[0] == 0
    capacity: int
    dist: tuple[tuple[int, ...], ...]       # travel distance = travel time, in tenths

    @property
    def n(self):
        return len(self.demand) - 1

    @property
    def customers(self):
        return range(1, self.n + 1)

    @classmethod
    def build(cls, name, coords, demand, ready, due, service, capacity):
        dist = tuple(tuple(int(math.dist(a, b)) for b in coords) for a in coords)
        return cls(name, tuple(map(tuple, coords)), tuple(demand), tuple(ready), tuple(due),
                   tuple(service), capacity, dist)

    def route_cost(self, route) -> int:
        path = (0, *route, 0)
        return sum(self.dist[a][b] for a, b in zip(path, path[1:]))

    def cost(self, routes) -> int:
        return sum(self.route_cost(r) for r in routes)

    def arc_possible(self, i: int, j: int) -> bool:
        """Can some feasible route traverse i -> j? Only the two endpoints are looked at:
        leave i as early as its window allows and check j's deadline and the load."""
        if i == j:
            return False
        if 0 not in (i, j) and self.demand[i] + self.demand[j] > self.capacity:
            return False
        return self.ready[i] + self.service[i] + self.dist[i][j] <= self.due[j]

    def arcs(self):
        """Every arc (i, j) that arc_possible allows, depot arcs included, sorted."""
        return [(i, j) for i in range(self.n + 1) for j in range(self.n + 1) if self.arc_possible(i, j)]

    def horizon(self) -> int:
        return self.due[0]

    def series(self) -> str:
        """'C1', 'C2', 'R1', 'R2', 'RC1' or 'RC2' for a Solomon instance, else ''."""
        head = self.name.split(".")[0].rstrip("0123456789")
        return head + self.name[len(head)] if head in ("C", "R", "RC") else ""

    def subset(self, n: int, name: str | None = None) -> "VRPTW":
        """The depot and the first n customers."""
        k = n + 1
        return VRPTW.build(name or f"{self.name}.{n}", self.coords[:k], self.demand[:k], self.ready[:k],
                           self.due[:k], self.service[:k], self.capacity)

    @classmethod
    def random(cls, n: int, seed=0, capacity: int = 60, width: int = 300, horizon: int = 2000,
               service: int = 50, side: int = 400) -> "VRPTW":
        """Uniform customers in a side x side square (tenths) around a central depot, demands 5-25,
        windows `width` wide placed so that serving each customer alone from the depot is feasible."""
        r = random.Random(seed)
        c0 = (side // 2, side // 2)
        coords = [c0] + [(r.randint(0, side), r.randint(0, side)) for _ in range(n)]
        demand, ready, due = [0], [0], [horizon]
        for p in coords[1:]:
            d = int(math.dist(c0, p))
            earliest, latest = d, horizon - service - d
            lo = r.randint(earliest, max(earliest, latest - width // 2))
            demand.append(r.randint(5, 25))
            ready.append(lo)
            due.append(min(latest, lo + width))
        return cls.build(f"rand{n}-{seed}", coords, demand, ready, due, [0] + [service] * n, capacity)


# ---------------------------------------------------------------- Solomon files

def fetch(force: bool = False) -> Path:
    """Download Solomon's 56 instances into data/solomon, verifying the archive's checksum."""
    if DATA.exists() and len(list(DATA.glob("*.txt"))) == len(SOLOMON_NAMES) and not force:
        return DATA
    request = urllib.request.Request(SOLOMON_URL, headers={"User-Agent": "curl/8"})   # the mirror refuses urllib's default
    with urllib.request.urlopen(request, timeout=60) as resp:
        blob = resp.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SOLOMON_SHA256:
        raise RuntimeError(f"checksum mismatch for {SOLOMON_URL}: {digest}")
    DATA.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for info in z.infolist():
            if info.filename.lower().endswith(".txt"):
                (DATA / Path(info.filename).name.lower()).write_bytes(z.read(info))
    return DATA


def parse_solomon(text: str) -> VRPTW:
    lines = [ln.split() for ln in text.splitlines() if ln.strip()]
    name = lines[0][0]
    vehicles_at = next(k for k, ln in enumerate(lines) if ln[0].upper() == "VEHICLE")
    capacity = int(lines[vehicles_at + 2][1])
    rows = [ln for ln in lines if len(ln) == 7 and all(t.lstrip("-").isdigit() for t in ln)]
    rows.sort(key=lambda ln: int(ln[0]))
    coords = [(10 * int(x), 10 * int(y)) for _, x, y, *_ in rows]
    col = lambda k, scale=10: [scale * int(ln[k]) for ln in rows]
    return VRPTW.build(name.upper(), coords, col(3, 1), col(4), col(5), col(6), capacity)


def solomon(name: str, n: int | None = None) -> VRPTW:
    """Solomon instance `name` (e.g. "R101"), restricted to its first n customers if given."""
    path = DATA / f"{name.lower()}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing: run `uv run co data` once to download Solomon's instances")
    inst = parse_solomon(path.read_text())
    return inst if n is None or n >= inst.n else inst.subset(n, f"{inst.name}.{n}")


def have_solomon() -> bool:
    return all((DATA / f"{nm.lower()}.txt").exists() for nm in SOLOMON_NAMES)


# ---------------------------------------------------------------- oracle

def feasible_routes(inst: VRPTW):
    """Every elementary route that respects capacity and windows, with its cost, by depth-first
    extension (waiting allowed). Exponential: for instances of about ten customers."""
    out = []

    def extend(route, load, time):
        last = route[-1] if route else 0
        for j in inst.customers:
            if j in route or load + inst.demand[j] > inst.capacity:
                continue
            start = max(inst.ready[j], time + inst.service[last] + inst.dist[last][j])
            if start > inst.due[j]:
                continue
            if start + inst.service[j] + inst.dist[j][0] > inst.due[0]:
                continue
            new = route + (j,)
            out.append(new)
            extend(new, load + inst.demand[j], start)

    extend((), 0, inst.ready[0])
    return out


def brute_force(inst: VRPTW):
    """Optimal (cost, routes) by enumerating feasible routes and a DP over subsets of customers.
    Routes in the answer are sorted by first customer. For n up to about 10."""
    n = inst.n
    best_route = {}
    for r in feasible_routes(inst):
        mask = sum(1 << (c - 1) for c in r)
        c = inst.route_cost(r)
        if mask not in best_route or c < best_route[mask][0]:
            best_route[mask] = (c, r)
    full = (1 << n) - 1
    INF = math.inf
    f = [INF] * (full + 1)
    choice = [None] * (full + 1)
    f[0] = 0
    by_low = {}
    for mask, (c, r) in best_route.items():
        by_low.setdefault(mask & -mask, []).append((mask, c, r))
    for s in range(1, full + 1):
        low = s & -s
        for mask, c, r in by_low.get(low, ()):
            if mask & s == mask and f[s ^ mask] + c < f[s]:
                f[s] = f[s ^ mask] + c
                choice[s] = (mask, r)
    if f[full] == INF:
        return None
    routes, s = [], full
    while s:
        mask, r = choice[s]
        routes.append(r)
        s ^= mask
    return f[full], sorted(routes)


# ---------------------------------------------------------------- SCIP plumbing

def lazy_cut_handler(model, x, separate, name="capacity"):
    """Attach a SCIP constraint handler that calls `separate` for cuts of the form

        sum of x[a] over arcs a in `arcs`  >=  rhs

    `x` is {arc: SCIP variable}. `separate(values)` gets {arc: value} and returns a list of
    (arcs, rhs) pairs, each violated by those values (it may return an empty list). The handler
    asks at every LP solution (as cutting planes) and at every candidate integer solution (as a
    lazy constraint, so an integer solution is rejected while any cut is violated). Returns the
    handler; its `.added` counts cuts added so far.

    This is the plumbing SCIP needs, not the lesson: the lesson is `separate`."""
    from pyscipopt import SCIP_RESULT, Conshdlr, quicksum

    arcs = list(x)

    class Handler(Conshdlr):
        added = 0

        def _values(self, solution=None):
            return {a: self.model.getSolVal(solution, x[a]) for a in arcs}

        def _add(self, cuts):
            for cut_arcs, rhs in cuts:
                self.model.addCons(quicksum(x[a] for a in cut_arcs) >= rhs, removable=True)
                self.added += 1

        def conscheck(self, constraints, solution, checkintegrality, checklprows, printreason, completely):
            return {"result": SCIP_RESULT.INFEASIBLE if separate(self._values(solution)) else SCIP_RESULT.FEASIBLE}

        def consenfolp(self, constraints, nusefulconss, solinfeasible):
            cuts = separate(self._values())
            if not cuts:
                return {"result": SCIP_RESULT.FEASIBLE}
            self._add(cuts)
            return {"result": SCIP_RESULT.CONSADDED}

        def consenfops(self, constraints, nusefulconss, solinfeasible, objinfeasible):
            return {"result": SCIP_RESULT.INFEASIBLE if separate(self._values()) else SCIP_RESULT.FEASIBLE}

        def conssepalp(self, constraints, nusefulconss):
            cuts = separate(self._values())
            if not cuts:
                return {"result": SCIP_RESULT.DIDNOTFIND}
            self._add(cuts)
            return {"result": SCIP_RESULT.CONSADDED}

        def conslock(self, constraint, locktype, nlockspos, nlocksneg):
            for a in arcs:                                   # a cut can need any arc raised
                self.model.addVarLocks(x[a], nlocksneg, nlockspos)

    h = Handler()
    model.includeConshdlr(h, name, "separates " + name + " cuts", sepapriority=1_000_000, enfopriority=-1,
                          chckpriority=-1, sepafreq=1, needscons=True)
    model.addPyCons(model.createCons(h, name, modifiable=False, initial=False, separate=True,
                                     enforce=True, check=True, propagate=False))
    return h
