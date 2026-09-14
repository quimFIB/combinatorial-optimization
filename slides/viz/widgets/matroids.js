// Matroid figures for unit 13: one greedy algorithm run with two independence oracles (forests,
// where it is optimal, and matchings, where it fails), and one augmenting path of matroid
// intersection in the exchange graph. Needs slides/viz/viz.js and the unit's viz-data.js
// (slides/viz/traces/u13.py).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html } = V;

  // ------------------------------------------------------------ greedy with an oracle
  //   data-runs="forest,path"
  V.register("matroid-greedy", (host) => {
    const runs = (host.dataset.runs || "forest,path").split(",").map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    // the deck's drawing for the five-vertex graph, scaled; a straight line for the path
    const layout = (run) => run.n === 5
      ? [[82, 213], [225, 317], [225, 122], [368, 213], [459, 109]]
      : [[80, 200], [200, 200], [320, 200], [440, 200]];
    V.stepper(host, {
      runs, width: 520, height: 400, stepWord: "step", label: "graph with the edges greedy has chosen",
      render({ svg, panel, run, state: st }) {
        const pos = layout(run);
        const nodes = pos.map(([x, y], v) => ({ id: v, x, y, label: v }));
        const edges = run.edges.map(([u, v], e) => ({ id: e, u, v, label: run.weights[e] }));
        const G = V.graph(svg, { nodes, edges }, { radius: 16 });
        const order = run.edges.map((_, e) => e).sort((a, b) => run.weights[b] - run.weights[a] || a - b);
        const seen = st.consider === null ? 0 : order.indexOf(st.consider) + 1;
        const done = st.best !== null;
        order.forEach((e, k) => {
          const past = done || k < seen;
          let cls = st.chosen.includes(e) ? "chosen" : past ? "muted" : "";
          if (st.blocking.includes(e)) cls = "hot";
          if (e === st.consider && st.verdict === "skip") cls = "warn";
          if (done && st.best.includes(e) && !st.chosen.includes(e)) cls = "good";
          G.edgeClass(e, cls);
        });
        V.text(svg, 12, 20, "numbers: edge weights · thick: chosen by greedy", "viz-label-soft", "start");
        if (st.consider !== null && st.verdict === "skip") V.text(svg, 12, 38, "red: rejected · dashed: what it clashes with", "viz-label-soft", "start");
        if (done && st.best.some((e) => !st.chosen.includes(e))) V.text(svg, 12, 38, "green: the better choice greedy never saw", "viz-label-soft", "start");
        html("div", { class: "viz-big" }, panel, `greedy weight ${st.value}`);
        const rows = order.map((e, k) => [`${run.edges[e][0]}${run.edges[e][1]}`, run.weights[e],
          k < seen || done ? (st.chosen.includes(e) ? "take" : "skip") : ""]);
        V.table(panel, ["edge", "weight", "greedy"], rows, (i, j) =>
          (i >= 0 && order[i] === st.consider ? "viz-hl" : j === 2 && i >= 0 && rows[i][2] === "skip" ? "viz-soft" : null));
        if (done) {
          const bestValue = st.best.reduce((s, e) => s + run.weights[e], 0);
          html("div", { class: bestValue === st.value ? "viz-readout viz-cert" : "viz-readout viz-bad" }, panel,
            `best possible (brute force): ${bestValue}`);
        }
      },
    });
  });

  // ------------------------------------------------------------ matroid intersection
  //   data-run="intersection"
  V.register("matroid-intersection", (host) => {
    const run = V.data(host, host.dataset.run || "intersection");
    if (!run) return;
    const side = { l0: [60, 120], l1: [60, 290], r0: [210, 120], r1: [210, 290] };
    const ex = [[322, 300], [405, 115], [488, 300]];
    V.stepper(host, {
      runs: [run], width: 520, height: 400, stepWord: "step", label: "bipartite graph and its exchange graph",
      render({ svg, panel, state: st }) {
        // left: the bipartite graph, edges named e0, e1, e2
        const bn = Object.entries(side).map(([id, [x, y]]) => ({ id, x, y, label: id.replace("l", "ℓ") }));
        const be = run.edges.map(([l, r], e) => ({ id: `e${e}`, u: `l${l}`, v: `r${r}`, label: `e${e}`, labelOffset: e === 1 ? -14 : 14 }));
        const B = V.graph(svg, { nodes: bn, edges: be }, { radius: 18 });
        const flipping = st.path.length > 0 && st.arcs.length > 0;   // the path is shown, not yet flipped
        run.edges.forEach((_, e) => {
          const onPath = st.path.includes(e), inI = st.I.includes(e);
          B.edgeClass(`e${e}`, flipping && onPath ? (inI ? "warn" : "good") : inI ? "chosen" : onPath ? "muted" : "");
        });
        V.text(svg, 135, 50, "the graph", "viz-label", "middle");
        V.text(svg, 135, 68, flipping ? "green: goes in · red: comes out" : "thick: the set I", "viz-label-soft", "middle");
        el("line", { x1: 262, y1: 40, x2: 262, y2: 360, class: "viz-grid" }, svg);
        // right: the exchange graph on the same three edges
        V.text(svg, 405, 50, "exchange graph", "viz-label", "middle");
        const xn = ex.map(([x, y], e) => ({ id: e, x, y, label: `e${e}`, noteDy: e === 1 ? -28 : 40 }));
        const xe = st.arcs.map(([a, b, m]) => ({ id: `${a}-${b}`, u: a, v: b, directed: true, bend: 30, label: m === 1 ? "M1" : "M2" }));
        const X = V.graph(svg, { nodes: xn, edges: xe }, { radius: 20 });
        run.edges.forEach((_, e) => {
          X.nodeClass(e, st.I.includes(e) ? "chosen" : "");
          X.nodeNote(e, st.sources.includes(e) ? "source" : st.sinks.includes(e) ? "sink" : st.I.includes(e) ? "in I" : "");
        });
        st.arcs.forEach(([a, b]) => {
          const i = st.path.indexOf(a);
          X.edgeClass(`${a}-${b}`, i >= 0 && st.path[i + 1] === b ? "chosen" : "");
        });
        if (st.arcs.length) {
          V.text(svg, 390, 368, "M1: the swap keeps one edge per left vertex", "viz-label-soft", "middle");
          V.text(svg, 390, 386, "M2: the swap keeps one edge per right vertex", "viz-label-soft", "middle");
        }
        html("div", { class: "viz-big" }, panel, `|I| = ${st.I.length}`);
        html("div", { class: "viz-readout" }, panel, `I = {${st.I.map((e) => `e${e}`).join(", ")}}`);
        const rows = run.edges.map(([l, r], e) => [`e${e}`, `ℓ${l} r${r}`, st.I.includes(e) ? "in I" : ""]);
        V.table(panel, ["edge", "joins", ""], rows, (i) => (i >= 0 && st.path.includes(i) ? "viz-hl" : null));
        html("div", { class: "viz-hint" }, panel, "M1 allows one edge per left vertex, M2 one per right vertex; a set independent in both is a matching.");
      },
    });
  });

})();
