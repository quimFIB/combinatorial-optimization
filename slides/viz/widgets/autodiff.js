// Unit 30 figure: forward and reverse mode on the computational graph of f = x·y + sin x,
// replayed from the reference Dual and Var classes (units/30-*/viz-data.js).
(function () {
  "use strict";
  const V = window.CoViz;
  const { num } = V;

  V.register("autodiff-graph", (host) => {
    const d = V.data(host, "graph");
    if (!d) return;
    const runs = ["forward-x", "forward-y", "reverse"].map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    const ops = Object.fromEntries(d.nodes.map((n) => [n.id, n.op]));
    const order = d.nodes.map((n) => n.id);

    V.stepper(host, {
      runs, width: 520, height: 380, label: "computational graph of f = xy + sin x",
      render(ctx) {
        const { svg, panel, run, state } = ctx;
        const nodes = d.nodes.map((n) => ({ ...n, noteDy: -30 }));
        const G = V.graph(svg, { nodes, edges: d.edges.map(([u, v]) => ({ u, v, directed: true })) }, { radius: 20 });
        for (const n of d.nodes) V.text(svg, n.x, n.y + 40, n.op, "viz-label-soft", "middle");
        const seen = new Set(Object.keys(state.values));

        if (run.mode === "forward") {
          for (const id of order) {
            if (!seen.has(id)) { G.nodeClass(id, "muted"); continue; }
            G.nodeNote(id, `${num(state.values[id], 4)} + ${num(state.tangents[id], 4)}ε`);
            G.nodeClass(id, id === state.active ? "chosen" : "");
          }
          for (const u of state.inputs) G.edgeClass(`${u}-${state.active}`, "hot");
          d.edges.forEach(([u, v]) => { if (!seen.has(v)) G.edgeClass(`${u}-${v}`, "muted"); });
          const rows = order.filter((id) => seen.has(id)).map((id) => [id, ops[id], num(state.values[id], 4), num(state.tangents[id], 4)]);
          V.table(panel, ["node", "operation", "value", "ε part"], rows, (i, j) => (rows[i] && rows[i][0] === state.active ? "viz-hl" : j === 1 ? "viz-soft" : ""));
        } else {
          const recording = state.phase === "record";
          for (const id of order) {
            if (!seen.has(id)) { G.nodeClass(id, "muted"); continue; }
            const adj = state.adjoints[id];
            G.nodeNote(id, recording ? num(state.values[id], 4) : `${num(state.values[id], 4)} · adj ${num(adj ?? 0, 4)}`);
            G.nodeClass(id, id === state.active ? (recording ? "chosen" : "warn") : "");
          }
          if (recording) {
            d.edges.forEach(([u, v]) => { if (!seen.has(v)) G.edgeClass(`${u}-${v}`, "muted"); else if (v === state.active) G.edgeClass(`${u}-${v}`, "hot"); });
          } else {
            for (const [u, v] of state.edges || []) {
              G.edgeClass(`${u}-${v}`, "warn");
              const local = (state.locals[v] || []).find(([p]) => p === u);
              if (local) V.text(svg, (d.nodes.find((n) => n.id === u).x + d.nodes.find((n) => n.id === v).x) / 2,
                                  (d.nodes.find((n) => n.id === u).y + d.nodes.find((n) => n.id === v).y) / 2 - 8,
                                  `× ${num(local[1], 4)}`, "viz-g-note", "middle");
            }
          }
          const rows = order.filter((id) => seen.has(id)).map((id) => {
            const locals = (state.locals[id] || []).map(([p, l]) => `∂/∂${p} = ${num(l, 4)}`).join(", ");
            return [id, ops[id], num(state.values[id], 4), locals || "—", recording ? "" : num(state.adjoints[id] ?? 0, 4)];
          });
          V.table(panel, ["node", "operation", "value", "local derivatives", "adjoint"], rows,
            (i, j) => (rows[i] && rows[i][0] === state.active ? "viz-hl" : j === 3 ? "viz-soft" : ""));
        }
      },
    });
  });
})();
