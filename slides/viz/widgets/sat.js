// SAT and lazy-clause-generation figures: the CDCL stepper (units 20, 21) and the order
// encoding with one precedence's explanations (unit 21). Needs slides/viz/viz.js and cp.css.
// Data: window.VIZ_DATA, recorded by slides/viz/traces/u20.py and u21.py.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html } = V;
  const varOf = (lit) => lit.replace(/^¬/, "");

  // ---------------------------------------------------------------- CDCL stepper
  //   data-runs="cdcl-deck,cdcl-pigeon"
  V.register("cdcl", (host) => {
    const runs = (host.dataset.runs || "").split(",").map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    V.stepper(host, {
      runs, width: 520, height: 430, label: "the implication graph of a CDCL run",
      render({ svg, panel, state }) {
        svg.classList.add("cp-thin");
        // implication graph: one column per decision level, literals in trail order
        const byLevel = new Map();
        state.trail.forEach((t) => { if (!byLevel.has(t.level)) byLevel.set(t.level, []); byLevel.get(t.level).push(t); });
        const levels = [...byLevel.keys()].sort((a, b) => a - b);
        const colW = Math.min(150, 440 / Math.max(1, levels.length + (state.kind === "conflict" || state.kind === "analyze" ? 1 : 0)));
        const pos = {}, nodes = [];
        levels.forEach((lv, c) => {
          const col = byLevel.get(lv), rowH = Math.min(70, 350 / col.length);
          col.forEach((t, r) => {
            // zigzag down the column, so arrows between neighbours in one level stay visible
            const x = 50 + c * colW + (r % 2) * Math.min(66, colW / 2), y = 60 + r * rowH;
            pos[varOf(t.lit)] = [x, y, c, r];
            nodes.push({ id: varOf(t.lit), label: t.lit, x, y });
          });
          V.text(svg, 50 + c * colW + Math.min(33, colW / 4), 26, `level ${lv}`, "sat-level");
        });
        const clauseById = Object.fromEntries(state.clauses.map((c) => [c.id, c]));
        const edges = [];
        for (const t of state.trail) {
          if (t.reason === null) continue;
          const c = clauseById[t.reason];
          if (!c) continue;
          for (const l of c.lits) {
            const v = varOf(l);
            if (v !== varOf(t.lit) && pos[v]) edges.push({ id: `${v}>${varOf(t.lit)}`, u: v, v: varOf(t.lit), directed: true, bend: pos[v][0] === pos[varOf(t.lit)][0] ? 30 : 0 });
          }
        }
        const confl = state.conflict !== undefined ? clauseById[state.conflict] : null;
        if (confl && (state.kind === "conflict" || state.kind === "analyze")) {
          const xs = levels.length ? 60 + levels.length * colW : 60;
          nodes.push({ id: "⊥", label: "⊥", x: Math.min(470, xs), y: 220 });
          for (const l of confl.lits) if (pos[varOf(l)]) edges.push({ id: `${varOf(l)}>⊥`, u: varOf(l), v: "⊥", directed: true });
        }
        const longest = Math.max(0, ...nodes.map((nd) => String(nd.label).length));
        svg.classList.toggle("sat-long", longest > 5);
        const G = V.graph(svg, { nodes, edges }, { radius: longest > 4 ? 25 : 20 });
        for (const t of state.trail) if (t.decision) G.nodeClass(varOf(t.lit), "chosen");
        if (confl && nodes.some((n) => n.id === "⊥")) {
          G.nodeClass("⊥", "warn");
          for (const l of confl.lits) if (pos[varOf(l)]) G.edgeClass(`${varOf(l)}>⊥`, "warn");
        }
        if (state.learned) {
          state.learned.forEach((l, i) => { if (pos[varOf(l)]) G.nodeClass(varOf(l), i === 0 ? "good" : "hot"); });
        }
        const legend = state.learned ? "green: the first UIP; outlined: the learned clause's other literals" : "filled: decisions; arrows: from a reason clause's other literals";
        V.text(svg, 12, 420, legend, "viz-label-soft", "start");

        // clause list with watches and values
        html("div", { class: "viz-head" }, panel, "clauses (watched literals underlined)");
        const list = html("div", { class: "sat-clauses" }, panel);
        const reasons = new Set(state.trail.map((t) => t.reason).filter((r) => r !== null));
        for (const c of state.clauses) {
          const cls = ["sat-clause"];
          if (c.learnt) cls.push("sat-learnt");
          if (confl && c.id === confl.id) cls.push("sat-conflict");
          else if (reasons.has(c.id)) cls.push("sat-reason");
          const row = html("div", { class: cls.join(" ") }, list);
          html("span", { class: "sat-num" }, row, `${c.id + 1}${c.learnt ? "ʟ" : ""}`);
          c.lits.forEach((l, i) => {
            if (i) row.appendChild(document.createTextNode(" ∨ "));
            const lc = ["sat-lit"];
            if (c.values[i] === true) lc.push("sat-true");
            if (c.values[i] === false) lc.push("sat-false");
            if (c.watched.includes(l)) lc.push("sat-watch");
            html("span", { class: lc.join(" ") }, row, l);
          });
          if (!c.lits.length) html("span", { class: "sat-lit" }, row, "(empty)");
        }
        html("div", { class: "viz-hint" }, panel, "ʟ: learned or explanation clause. Dashed outline: the reason of some literal on the trail. Green: true, struck through: false.");
      },
    });
  });

  // ---------------------------------------------------------------- order encoding + precedence
  //   data-key="precedence"
  V.register("precedence", (host) => {
    const T = V.data(host, host.dataset.key || "precedence");
    if (!T) return;
    host.classList.add("viz-side");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const right = html("div", { class: "viz-right" }, host);
    const W = 520, H = 250;
    const svg = V.newSvg(left, W, H, "bounds of x and y under x + 3 ≤ y");
    let lo = 0, hi = 6;
    const controls = html("div", {}, left);
    V.slider(controls, { label: "decide x ≥", min: 0, max: 3, step: 1, value: 0 }, (v) => { lo = v; draw(); });
    V.slider(controls, { label: "decide y ≤", min: 0, max: 6, step: 1, value: 6 }, (v) => { hi = v; draw(); });
    const out = html("div", {}, right);
    const X = (t) => 60 + t * 62;

    function line(y, name, lb, ub, bound, cls) {
      V.text(svg, 30, y + 6, name, "cp-var");
      for (let t = lb; t <= ub; t++) {
        const inside = t >= bound[0] && t <= bound[1];
        el("rect", { x: X(t) - 18, y: y - 14, width: 36, height: 28, rx: 4, class: inside ? "cp-cell" : "cp-cell cp-cell-gone" }, svg);
        V.text(svg, X(t), y + 5, t, inside ? "cp-cell-text" : "cp-cell-text cp-cell-text-gone");
      }
      V.text(svg, X(ub) + 34, y + 5, cls, "viz-label-soft", "start");
    }

    function draw() {
      svg.replaceChildren();
      const R = T[`${lo},${hi}`];
      line(60, "x", 0, 3, R.x, `x ∈ [${R.x[0]}, ${R.x[1]}]`);
      line(150, "y", 0, 6, R.y, `y ∈ [${R.y[0]}, ${R.y[1]}]`);
      V.text(svg, 20, 230, R.conflict ? "conflict: no y is left above x + 3" : "x + 3 ≤ y, x ∈ 0..3, y ∈ 0..6", R.conflict ? "cp-removed" : "viz-label-soft", "start");

      out.replaceChildren();
      html("div", { class: "viz-head" }, out, "decisions");
      html("div", { class: "viz-readout" }, out, R.decisions.length
        ? R.decisions.map((d) => d.skipped ? `${d.lit} (${d.skipped})` : `${d.lit} at level ${d.level}`).join("; ")
        : "none: only what holds at the root");
      html("div", { class: "viz-head" }, out, "explanation clauses the precedence handed over");
      if (!R.explanations.length) html("div", { class: "viz-readout cp-soft" }, out, "none");
      R.explanations.forEach((e) =>
        html("div", { class: "viz-readout" }, out, `level ${e.level}: (${e.clause.join(" ∨ ") || "empty"})${e.result === "conflict" ? " — conflict" : ""}`));
      html("div", { class: "viz-head" }, out, "the order-encoding literals now");
      const tab = html("table", { class: "viz-tab sat-stair" }, out);
      for (const [name, vals] of Object.entries(R.lits)) {
        const tr = html("tr", {}, tab);
        html("td", { class: "viz-bas" }, tr, name);
        vals.forEach((v, i) => html("td", { class: v === true ? "sat-t" : v === false ? "sat-f" : "sat-u" }, tr, `[${name}≤${i}]`));
      }
      html("div", { class: "viz-hint" }, out, "Green: true. Grey: false. Plain: unassigned. Reading left to right, the literals are false up to the lower bound and true from the upper bound on.");
    }
    draw();
  });
})();
