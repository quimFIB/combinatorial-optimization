// Network-flow figures for unit 14: augmenting paths on the residual graph, and push–relabel
// with nodes drawn at their heights. Needs slides/viz/viz.js and the unit's viz-data.js
// (slides/viz/traces/u14.py).
(function () {
  "use strict";
  const V = window.CoViz;
  const { html, num } = V;

  // Residual edges as graph edges: every direction bends to its own side, so an arc and its
  // reverse never overlap. Classes: on the path "chosen", backward (undo) edges "hot".
  function residualEdges(net, st, onPath) {
    return st.residual.map((r, i) => ({
      id: `r${i}`, u: net.names[r.u], v: net.names[r.v], label: r.cap, directed: true, bend: 16,
      cls: onPath(r) ? "chosen" : r.forward ? "" : "hot",
    }));
  }
  function flowTable(panel, net, st) {
    const rows = net.arcs.map(([u, v, c], k) => [`${net.names[u]} → ${net.names[v]}`, `${st.flow[k]} / ${c}`,
      st.flow[k] === c ? "full" : st.flow[k] > 0 ? "" : "empty"]);
    V.table(panel, ["arc", "flow / capacity", ""], rows, (i, j) => (j === 2 ? "viz-soft" : j === 1 && i >= 0 && rows[i][2] === "full" ? "viz-goodcell" : null));
  }

  // ------------------------------------------------------------ augmenting paths
  //   data-runs="ek,ff"
  V.register("flow-augment", (host) => {
    const d = window.VIZ_DATA;
    if (!d || !d.network) return V.fail(host, "no recorded data: run `uv run co viz 14`");
    const net = d.network;
    const runs = (host.dataset.runs || "ek,ff").split(",").map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    const pos = { s: [70, 200], a: [260, 80], b: [260, 320], t: [450, 200] };
    V.stepper(host, {
      runs, width: 520, height: 400, stepWord: "step", label: "residual graph with the current augmenting path",
      render({ svg, panel, state: st }) {
        const onPath = (r) => st.path && st.path.some((p) => p.u === r.u && p.v === r.v && p.forward === r.forward);
        const edges = residualEdges(net, st, onPath);
        const nodes = net.names.map((n) => ({ id: n, x: pos[n][0], y: pos[n][1], label: n, noteDy: n === "a" ? -26 : n === "b" ? 34 : -26 }));
        const G = V.graph(svg, { nodes, edges }, { radius: 20 });
        edges.forEach((e) => G.edgeClass(e.id, e.cls));
        if (st.cut) {
          net.names.forEach((n, i) => G.nodeClass(n, st.cut.includes(i) ? "good" : ""));
          V.text(svg, 260, 388, `source side of the minimum cut: {${st.cut.map((i) => net.names[i]).join(", ")}}`, "viz-label", "middle");
        }
        V.text(svg, 12, 20, "residual graph: numbers are remaining capacity", "viz-label-soft", "start");
        V.text(svg, 12, 38, "dashed: backward arcs (flow that can be undone)", "viz-label-soft", "start");
        html("div", { class: "viz-big" }, panel, `flow value ${st.value}`);
        flowTable(panel, net, st);
      },
    });
  });

  // ------------------------------------------------------------ push–relabel
  //   data-runs="pr"
  V.register("push-relabel", (host) => {
    const d = window.VIZ_DATA;
    if (!d || !d.network) return V.fail(host, "no recorded data: run `uv run co viz 14`");
    const net = d.network;
    const run = V.data(host, host.dataset.runs || "pr");
    if (!run) return;
    const xs = { s: 80, a: 230, b: 350, t: 470 };
    const dy = { s: 0, a: 0, b: -28, t: 0 };           // b sits a little higher, so a → t never runs through it
    const base = 345, step = 66;
    V.stepper(host, {
      runs: [run], width: 520, height: 400, stepWord: "step", label: "push–relabel: nodes drawn at their heights",
      render({ svg, panel, state: st }) {
        for (let h = 0; h <= 4; h++) {
          V.el("line", { x1: 30, y1: base - h * step, x2: 510, y2: base - h * step, class: "viz-grid" }, svg);
          V.text(svg, 26, base - h * step + 4, `h=${h}`, "viz-tick", "end");
        }
        const nodes = net.names.map((n, i) => ({ id: n, x: xs[n], y: base - st.height[i] * step + dy[n], label: n, noteDy: 34 }));
        // the arc just pushed along: highlight it, or draw it once more if the push used it up
        const a = st.arc, stillThere = a && st.residual.some((r) => r.u === a.u && r.v === a.v);
        const onArc = (r) => !!a && stillThere && r.u === a.u && r.v === a.v;
        const edges = residualEdges(net, st, onArc);
        if (a && !stillThere) edges.push({ id: "pushed", u: net.names[a.u], v: net.names[a.v], label: null, directed: true, bend: 34, cls: "chosen" });
        const G = V.graph(svg, { nodes, edges }, { radius: 18 });
        edges.forEach((e) => G.edgeClass(e.id, e.cls));
        net.names.forEach((n, i) => {
          if (i !== net.s && i !== net.t && st.excess[i] > 0) { G.nodeClass(n, "warn"); G.nodeNote(n, `excess ${st.excess[i]}`); }
          if (i === net.t) G.nodeNote(n, `received ${st.excess[i]}`);
        });
        if (st.active !== null && st.active !== undefined && st.excess[st.active] <= 0 && st.active !== net.t) G.nodeClass(net.names[st.active], "hot");
        const rows = net.names.map((n, i) => [n, st.height[i], st.excess[i]]);
        V.table(panel, ["node", "height", "excess"], rows, (i, j) => (i >= 0 && i === st.active && j > 0 ? "viz-hl" : null));
        flowTable(panel, net, st);
      },
    });
  });
})();
