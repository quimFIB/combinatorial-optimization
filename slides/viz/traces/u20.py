"""Unit 20's recorded CDCL runs, for units/20-sat-cdcl/explore.html (and unit 21's LCG run).

A subclass of the reference `Solver` that only *observes*: it snapshots the trail, clauses and
watches after every decision, implied literal, conflict, analysis and backjump, then defers to
the reference methods. Decisions can be scripted for the first few levels so a run follows the
deck's example. `uv run co viz 20` writes units/20-sat-cdcl/viz-data.js.
"""

from __future__ import annotations

from colib import ref

SAT = ref.unit("20")


def recorder(base):
    class Recorder(base):
        def setup_recording(self, names, script=()):
            self.names = names
            self.script = list(script)
            self.events = []
            self.pending_implied = []

        def lit_name(self, i):
            v, neg = i >> 1, i & 1
            return ("¬" if neg else "") + self.names(v)

        def dimacs_name(self, d):
            return ("¬" if d < 0 else "") + self.names(abs(d))

        def orig_order(self, ci, c):
            orders = self.__dict__.setdefault("orders", {})
            if ci not in orders:
                learnt = getattr(self, "last_learnt", None)
                orders[ci] = list(learnt) if learnt is not None and sorted(learnt) == sorted(c) else list(c)
            return orders[ci]

        def snapshot(self, kind, note, explain="", **extra):
            trail = []
            for i in self.trail:
                v = i >> 1
                r = self.reason[v]
                trail.append({"lit": self.lit_name(i), "var": v, "level": self.level[v],
                              "reason": r, "decision": r is None and self.level[v] > 0})
            clauses = []
            for ci, c in enumerate(self.clauses):
                if self.deleted[ci]:
                    continue
                # show literals in the order the clause was written or learned; the solver's
                # own order only says which two are watched
                order = self.orig_order(ci, c)
                clauses.append({"id": ci, "lits": [self.lit_name(i) for i in order],
                                "values": [self.lit_value(i) for i in order],
                                "learnt": self.learnt[ci], "watched": [self.lit_name(i) for i in c[:2]]})
            self.events.append({"kind": kind, "note": note, "explain": explain, "trail": trail,
                                "clauses": clauses, "level": self.decision_level(), **extra})

        def enqueue(self, i, reason):
            super().enqueue(i, reason)
            if reason is not None:
                self.pending_implied.append((i, reason))

        def propagate(self):
            confl = super().propagate()
            implied = [(self.lit_name(i), r) for i, r in self.pending_implied]
            self.pending_implied = []
            if implied:
                lines = ", ".join(f"{n} (from clause {r + 1})" for n, r in implied)
                self.snapshot("propagate", f"unit propagation: {lines}",
                              "Each of these clauses had every literal false but one, so that one is forced. The clause becomes the literal's reason.")
            if confl is not None:
                c = self.clauses[confl]
                self.snapshot("conflict", f"conflict: clause {confl + 1} ({' ∨ '.join(self.lit_name(i) for i in self.orig_order(confl, c))}) has every literal false",
                              "Propagation has derived a contradiction at this decision level. Time to analyse it.", conflict=confl)
            return confl

        def analyze(self, confl):
            learnt, back, lbd = super().analyze(confl)
            clause = " ∨ ".join(self.lit_name(i) for i in learnt)
            self.snapshot("analyze", f"learn ({clause}), backjump to level {back}, LBD {lbd}",
                          f"Resolving the conflict clause with the reasons of the latest literals of level {self.decision_level()} until one of them is left: "
                          f"{self.lit_name(learnt[0] ^ 1)} is the first UIP. The clause is asserting: after the backjump it forces {self.lit_name(learnt[0])}.",
                          learned=[self.lit_name(i) for i in learnt], back=back, conflict=confl)
            self.last_learnt = learnt
            return learnt, back, lbd

        def cancel_until(self, lvl):
            if self.decision_level() > lvl:
                super().cancel_until(lvl)
                self.snapshot("backjump", f"backjump to level {lvl}", "Everything assigned above that level is undone; the watches stay where they are.")
            else:
                super().cancel_until(lvl)

        def pick_branch(self):
            while self.script:
                d = self.script.pop(0)
                v = abs(d)
                if self.value[v] is None:
                    lit = 2 * v + (0 if d > 0 else 1)
                    self._announce_decision(lit, scripted=True)
                    return lit
            lit = super().pick_branch()
            if lit is not None:
                self._announce_decision(lit, scripted=False)
            return lit

        def _announce_decision(self, lit, scripted):
            self._next_decision = (lit, scripted)

        def solve(self, conflict_limit=None):
            result = super().solve(conflict_limit)
            if result is True:
                model = ", ".join(self.lit_name(2 * v + (0 if self.value[v] else 1)) for v in range(1, self.n + 1))
                self.snapshot("sat", "satisfiable: every variable assigned, no conflict", f"Model: {model}.")
            elif result is False:
                self.snapshot("unsat", "unsatisfiable: a conflict at decision level 0",
                              "Nothing is left to undo: the learned clauses prove the formula has no model.")
            return result

    # decisions are recorded right after the reference solve loop enqueues them
    orig_enqueue = Recorder.enqueue

    def enqueue(self, i, reason):
        orig_enqueue(self, i, reason)
        nd = getattr(self, "_next_decision", None)
        if reason is None and nd is not None and nd[0] == i:
            self._next_decision = None
            how = "scripted to follow the deck" if nd[1] else "highest activity, saved phase"
            self.snapshot("decide", f"decide {self.lit_name(i)} at level {self.decision_level()}", f"A decision ({how}): no clause forces it.")
        elif reason is None and self.decision_level() == 0 and self.events and self.events[-1]["kind"] == "backjump":
            self.snapshot("assert", f"assert the learned unit {self.lit_name(i)} at level 0",
                          "A one-literal learned clause holds unconditionally: it becomes a fact at the root.")
    Recorder.enqueue = enqueue
    return Recorder


def run(title, nvars, clauses, names, script=(), base=None):
    Rec = recorder(base or SAT.Solver)
    s = Rec.__new__(Rec)
    s.setup_recording(names, script)
    Rec.__init__(s, nvars, clauses)
    s.snapshot("start", "the clauses, before any decision", "Each clause watches its first two literals (underlined).")
    result = s.solve()
    # the recorder never changes a decision the reference would not make once the script is used up,
    # and it must agree with a plain reference run on satisfiability
    plain = SAT.Solver(nvars, clauses).solve()
    assert result == plain, title
    return {"title": title, "names": [names(v) for v in range(1, nvars + 1)], "states": s.events}


def data():
    deck = [[-1, 3], [-2, -3, 4], [-2, -4, 5], [-4, -5]]
    n, ph = SAT.pigeonhole(2)
    pigeon = lambda v: f"p{(v - 1) // 2 + 1}h{(v - 1) % 2 + 1}"
    return {
        "cdcl-deck": run("the deck's four clauses, deciding x1 then x2", 5, deck, lambda v: f"x{v}", script=[1, 2]),
        "cdcl-pigeon": run("three pigeons, two holes (unsatisfiable)", n, ph, pigeon),
    }
