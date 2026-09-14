"""Unit 21's recorded data, for units/21-lazy-clause-generation/explore.html.

Explanations: for every choice of decisions x >= lo and y <= hi, the reference `Model`,
`IntVar`, `Precedence` and `LCGSolver` propagate x + 3 <= y (x in 0..3, y in 0..6), and the
page looks up the bounds, the literal values and each explanation clause.
The learned clause: unit 20's recording solver (slides/viz/traces/u20.py) wrapped around the
reference `LCGSolver`, on the deck's two tasks with an order Boolean.
`uv run co viz 21` writes units/21-lazy-clause-generation/viz-data.js.
"""

from __future__ import annotations

from colib import ref

from . import u20

LCG = ref.unit("21")
SAT = ref.unit("20")


def names_for(ints, bools):
    """Readable names: [x ≤ v] for order literals, the given name for Booleans."""
    table = {}
    for iv in ints:
        for v in range(iv.lb, iv.ub):
            table[iv.le(v)] = f"[{iv.name}≤{v}]"
    table.update(bools)
    return lambda var: table[var]


def lit_text(name, lit):
    return ("¬" if lit < 0 else "") + name(abs(lit))


def precedence_table():
    out = {}
    for lo in range(0, 4):
        for hi in range(0, 7):
            m = LCG.Model()
            x, y = m.int_var(0, 3, "x"), m.int_var(0, 6, "y")
            m.propagators.append(LCG.Precedence(x, 3, y))
            name = names_for([x, y], {})
            s = LCG.LCGSolver(m)
            log = []
            orig = s._add_explanation

            def spy(clause, orig=orig, s=s):
                result = orig(clause)
                if result in ("implied", "conflict"):
                    log.append({"clause": [lit_text(name, l) for l in clause], "result": result, "level": s.decision_level()})
                return result
            s._add_explanation = spy
            conflict = s.propagate() is not None
            decisions = []
            for lit in ([x.ge(lo)] if lo > 0 else []) + ([y.le(hi)] if hi < 6 else []):
                if conflict:
                    break
                i = SAT.to_internal(lit)
                val = s.lit_value(i)
                if val is True:
                    decisions.append({"lit": lit_text(name, lit), "skipped": "already true"})
                    continue
                if val is False:
                    decisions.append({"lit": lit_text(name, lit), "skipped": "already false: conflict"})
                    conflict = True
                    break
                s.trail_lim.append(len(s.trail))
                s.enqueue(i, None)
                decisions.append({"lit": lit_text(name, lit), "level": s.decision_level()})
                conflict = s.propagate() is not None
            lits = {}
            for iv in (x, y):
                lits[iv.name] = [None if s.value[iv.le(v)] is None else bool(s.value[iv.le(v)]) for v in range(iv.lb, iv.ub)]
            out[f"{lo},{hi}"] = {"decisions": decisions, "explanations": log, "conflict": conflict,
                                 "x": list(x.bounds(s)), "y": list(y.bounds(s)), "lits": lits}
    return out


def learned_run():
    m = LCG.Model()
    a, c = m.int_var(0, 4, "a"), m.int_var(0, 4, "c")
    b = m.bool_var()
    m.propagators += [LCG.Precedence(a, 3, c, enabled=b), LCG.Precedence(c, 3, a, enabled=-b)]
    name = names_for([a, c], {b: "b"})
    Rec = u20.recorder(LCG.LCGSolver)
    s = Rec.__new__(Rec)
    s.setup_recording(name, script=[a.ge(2), b])
    orig = Rec._add_explanation

    def spy(self, clause):
        result = orig(self, clause)
        if result in ("implied", "conflict"):
            text = " ∨ ".join(lit_text(name, l) for l in clause) or "(empty)"
            self.snapshot("explain", f"a propagator explains itself: ({text})",
                          "The precedence narrowed a bound and handed CDCL a clause that forces it"
                          + (" — here every literal is already false, so it is a conflict." if result == "conflict" else "."))
        return result
    Rec._add_explanation = spy
    Rec.__init__(s, m)
    s.snapshot("start", "tasks a, c ∈ 0..4 of length 3 on one machine; b means a before c",
               "Order literals [a≤v] and [c≤v], a Boolean b, and two precedences switched by b and ¬b.")
    result = s.solve()
    assert result is True
    return {"title": "two tasks, an order Boolean: deciding a ≥ 2, then b", "names": [name(v) for v in range(1, m.nvars + 1)], "states": s.events}


def data():
    return {"precedence": precedence_table(), "lcg-learned": learned_run()}
