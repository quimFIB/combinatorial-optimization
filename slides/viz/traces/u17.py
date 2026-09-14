"""Unit 17's recorded runs, for units/17-constraint-propagation/explore.html.

AC-3: the queue discipline of the reference `ac3`, replayed step by step with the reference
`revise`; every run is checked to end with the same domains and call count as `ac3` itself.
The trail: the reference `Store`, `NotEqual`, `fixpoint`, `mark` and `undo`, snapshotted after
every event. `uv run co viz 17` writes units/17-constraint-propagation/viz-data.js.
"""

from __future__ import annotations

from collections import deque

from colib import ref

L = ref.unit("17")

LT = lambda a, b: a < b
NE = lambda a, b: a != b


def dom_str(d):
    return "".join(str(v) for v in sorted(d)) if d else "∅"


def ac3_run(title, variables, domains, arcs, ops):
    """arcs: list of (x, y, op name); ops maps op name -> (allowed, symbol)."""
    constraints = {(x, y): ops[o][0] for x, y, o in arcs}
    symbol = {(x, y): ops[o][1] for x, y, o in arcs}
    dom = {v: frozenset(domains[v]) for v in variables}
    incoming = {}
    for z, x in constraints:
        incoming.setdefault(x, []).append(z)
    queue, queued = deque(constraints), set(constraints)
    calls = 0
    states = [{"dom": {v: dom_str(dom[v]) for v in variables}, "queue": [list(a) for a in queue],
               "arc": None, "removed": [], "pushed": [], "calls": 0,
               "note": f"start: all {len(queue)} arcs on the queue"}]
    wipeout = False
    while queue:
        arc = queue.popleft()
        queued.discard(arc)
        x, y = arc
        calls += 1
        before = dom[x]
        new = L.revise(dom[x], dom[y], constraints[arc])
        pushed = []
        if new != before:
            if not new:
                wipeout = True
            else:
                dom[x] = new
                for z in incoming.get(x, ()):
                    if (z, x) not in queued:
                        queue.append((z, x))
                        queued.add((z, x))
                        pushed.append([z, x])
        removed = sorted(before - new)
        rel = symbol[arc]
        if wipeout:
            note = f"revise {x} against {y}: no value of {x} has a support, wipeout"
            explain = f"Every value of {x} needs some value of {y} with {x} {rel} {y}; none has one, so the constraints cannot all hold."
        elif removed:
            note = f"revise {x} against {y}: remove {', '.join(map(str, removed))}"
            explain = (f"{', '.join(f'{x} = {a}' for a in removed)} has no {y} with {x} {rel} {y}. "
                       + (f"{x} shrank, so the arcs that read {x} go back on the queue: {', '.join(f'({z},{w})' for z, w in pushed)}."
                          if pushed else f"{x} shrank, but every arc that reads {x} is already queued."))
        else:
            note = f"revise {x} against {y}: nothing to remove"
            explain = f"Every value of {x} still has a support in {y}."
        states.append({"dom": {v: (dom_str(new) if (v == x and wipeout) else dom_str(dom[v])) for v in variables},
                       "queue": [list(a) for a in queue], "arc": [x, y], "removed": removed, "pushed": pushed,
                       "calls": calls, "note": note, "explain": explain, "wipeout": wipeout})
        if wipeout:
            break
    if not wipeout:
        states.append({**states[-1], "arc": None, "removed": [], "pushed": [],
                       "note": f"queue empty after {calls} revise calls: arc consistent",
                       "explain": "Every value left has a support on every arc. "
                                  + ("Each domain is a single value: solved without search." if all(len(d) == 1 for d in dom.values())
                                     else "Some domains still hold several values: consistency alone does not decide this one.")})
    ref_dom, ref_calls = L.ac3({v: set(domains[v]) for v in variables}, constraints)
    if wipeout:
        assert ref_dom is None and ref_calls == calls, (title, ref_calls, calls)
    else:
        assert ref_calls == calls and all(ref_dom[v] == dom[v] for v in variables), title
    return {"title": title, "variables": variables, "arcs": [[x, y, symbol[(x, y)]] for x, y, _ in arcs], "states": states}


def trail_run():
    names = ["x", "y", "z"]
    store = L.Store([{1, 2, 3}] * 3)
    props = [L.NotEqual(0, 1), L.NotEqual(1, 2)]
    watch = L.watches(3, props)
    stats = L.Stats()
    states = []
    marks = {}

    def snap(event, note, explain=""):
        states.append({"event": event, "note": note, "explain": explain,
                       "dom": [dom_str(d) for d in store.dom],
                       "trail": [[names[v], dom_str(old)] for v, old in store.trail],
                       "marks": dict(marks)})

    snap("start", "x, y, z ∈ {1,2,3}, with x ≠ y and y ≠ z", "The trail is empty: nothing has changed yet.")
    marks["m₀"] = store.mark()
    snap("mark m₀", "mark m₀ = 0", "A mark is just the trail's current length.")
    store.assign(0, 1)
    snap("decide x = 1", "decide x = 1", "Before narrowing x, the store pushes (x, its old domain 123).")
    L.fixpoint(store, props, watch, stats, dirty=[0])
    snap("propagate", "propagate: x ≠ y removes 1 from y", "The propagator narrows y, and the store trails (y, 123) first.")
    marks["m₁"] = store.mark()
    snap("mark m₁", f"mark m₁ = {marks['m₁']}", "Remember where the second decision starts.")
    store.assign(1, 2)
    snap("decide y = 2", "decide y = 2", "Trail (y, 23): y's domain just before this change.")
    L.fixpoint(store, props, watch, stats, dirty=[1])
    snap("propagate", "propagate: y ≠ z removes 2 from z", "Trail (z, 123). Four entries for two decisions.")
    store.undo(marks["m₁"])
    snap("undo to m₁", "undo to m₁: pop back to length 2", "Pops (z, 123) then (y, 23), restoring each old domain: exactly the state after the first propagation.")
    store.undo(marks["m₀"])
    snap("undo to m₀", "undo to m₀: back to the root", "Pops (y, 123) then (x, 123), newest first: the original domains and an empty trail.")
    return {"title": "the trail of a store with two decisions", "variables": names, "values": [1, 2, 3], "states": states}


def data():
    ops = {"<": (LT, "<"), "≠": (NE, "≠")}
    chain = ac3_run("x < y < z on {1,2,3}: solved by propagation", ["x", "y", "z"],
                    {"x": {1, 2, 3}, "y": {1, 2, 3}, "z": {1, 2, 3}},
                    [("x", "y", "<"), ("y", "x", ">"), ("y", "z", "<"), ("z", "y", ">")],
                    {"<": (LT, "<"), ">": (lambda a, b: a > b, ">")})
    triangle = ac3_run("x ≠ y ≠ z ≠ x on {0,1}: consistent, yet no solution", ["x", "y", "z"],
                       {"x": {0, 1}, "y": {0, 1}, "z": {0, 1}},
                       [(a, b, "≠") for a, b in [("x", "y"), ("y", "x"), ("y", "z"), ("z", "y"), ("x", "z"), ("z", "x")]], ops)
    cycle = ac3_run("x < y < z < x on {1,2,3}: a wipeout", ["x", "y", "z"],
                    {"x": {1, 2, 3}, "y": {1, 2, 3}, "z": {1, 2, 3}},
                    [("x", "y", "<"), ("y", "x", ">"), ("y", "z", "<"), ("z", "y", ">"), ("z", "x", "<"), ("x", "z", ">")],
                    {"<": (LT, "<"), ">": (lambda a, b: a > b, ">")})
    return {"ac3-chain": chain, "ac3-triangle": triangle, "ac3-cycle": cycle, "trail": trail_run()}
