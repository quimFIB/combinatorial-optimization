// Dynamic-programming figures for unit 16: the knapsack table filled cell by cell, and the
// in/out values of a tree DP. Needs slides/viz/viz.js and the unit's viz-data.js
// (slides/viz/traces/u16.py).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html } = V;

  // ------------------------------------------------------------ knapsack table
  //   data-run="knapsack"
  V.register("dp-table", (host) => {
    const run = V.data(host, host.dataset.run || "knapsack");
    if (!run) return;
    const n = run.values.length, C = run.capacity;
    const W = 520, H = 400, left = 90, top = 70, cw = (W - left - 20) / (C + 1), ch = 52;
    const cx = (c) => left + c * cw + cw / 2, cy = (i) => top + i * ch + ch / 2;
    V.stepper(host, {
      runs: [run], width: W, height: H, stepWord: "fill", label: "knapsack DP table",
      render({ svg, panel, state: st }) {
        const defs = el("defs", {}, svg);
        const m = el("marker", { id: `dp-arrow-${svg.dataset.vizId}`, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto" }, defs);
        el("path", { d: "M0,0 L10,5 L0,10 z", class: "viz-arrowhead chosen" }, m);
        V.text(svg, left + (C + 1) * cw / 2, 26, "capacity c", "viz-label-soft", "middle");
        V.text(svg, 16, top - 12, "items", "viz-label-soft", "start");
        for (let c = 0; c <= C; c++) V.text(svg, cx(c), top - 12, String(c), "viz-tick", "middle");
        for (let i = 0; i <= n; i++) {
          V.text(svg, left - 10, cy(i) + 5, i === 0 ? "none" : i === 1 ? "1" : `1–${i}`, "viz-label", "end");
          for (let c = 0; c <= C; c++) {
            const isCell = st.cell && st.cell[0] === i && st.cell[1] === c;
            const isDep = st.deps && st.deps.some(([a, b]) => a === i && b === c);
            const onPath = st.path && st.path.some(([a, b]) => a === i && b === c);
            const cls = isCell ? "viz-dp-cell current" : isDep ? "viz-dp-cell dep" : onPath ? "viz-dp-cell path" : "viz-dp-cell";
            el("rect", { x: left + c * cw + 2, y: top + i * ch + 2, width: cw - 4, height: ch - 4, rx: 4, class: cls }, svg);
            if (st.filled[i][c]) V.text(svg, cx(c), cy(i) + 6, String(st.table[i][c]), isCell ? "viz-dp-num strong" : "viz-dp-num", "middle");
          }
        }
        const arrow = (a, b, cls) => {
          const [i0, c0] = a, [i1, c1] = b;
          const up = i1 < i0;                         // read-back arrows go up, dependency arrows down
          const x0 = cx(c0), y0 = cy(i0) + (up ? -ch / 2 + 2 : ch / 2 - 2), x1 = cx(c1), y1 = cy(i1) + (up ? ch / 2 - 2 : -ch / 2 + 2);
          el("path", { d: `M${x0},${y0} L${x1},${y1}`, class: cls, "marker-end": `url(#dp-arrow-${svg.dataset.vizId})` }, svg);
        };
        if (st.cell && st.deps) for (const d of st.deps) arrow(d, st.cell, "viz-dp-arrow");
        if (st.path) {
          for (const [i, c, took] of st.path) {
            const w = run.weights[i - 1];
            arrow([i, c], [i - 1, took ? c - w : c], took ? "viz-dp-arrow took" : "viz-dp-arrow");
          }
        }
        const cur = st.cell ? st.cell[0] : null;
        const rows = run.values.map((v, k) => [`item ${k + 1}`, run.weights[k], v]);
        V.table(panel, ["", "weight", "value"], rows, (i) => (i >= 0 && i + 1 === cur ? "viz-hl" : null));
      },
    });
  });

  // ------------------------------------------------------------ tree DP
  //   data-run="tree"
  V.register("tree-dp", (host) => {
    const run = V.data(host, host.dataset.run || "tree");
    if (!run) return;
    const pos = [[260, 60], [140, 180], [380, 180], [75, 310], [205, 310], [315, 310], [445, 310]];
    V.stepper(host, {
      runs: [run], width: 520, height: 400, stepWord: "step", label: "tree with in and out values",
      render({ svg, panel, state: st }) {
        // notes sit where no edge runs: above the root, outside the middle vertices, under the leaves
        const place = [[0, -30], [-78, 5], [78, 5], [0, 40], [0, 40], [0, 40], [0, 40]];
        const nodes = run.weights.map((w, v) => ({ id: v, x: pos[v][0], y: pos[v][1], label: v, noteDx: place[v][0], noteDy: place[v][1] }));
        const edges = run.edges.map(([u, v]) => ({ id: `${u}-${v}`, u, v }));
        const G = V.graph(svg, { nodes, edges }, { radius: 20 });
        run.weights.forEach((w, v) => {
          const wAt = [[28, 5, "start"], [26, 26, "start"], [-26, 26, "end"], [24, -20, "start"], [24, -20, "start"], [24, -20, "start"], [24, -20, "start"]][v];
          V.text(svg, pos[v][0] + wAt[0], pos[v][1] + wAt[1], `w=${w}`, "viz-label-soft", wAt[2]);
          const inc = st.inc[v], exc = st.exc[v];
          G.nodeNote(v, inc === null ? "" : `in ${inc} · out ${exc}`);
        });
        if (st.cover) {
          run.weights.forEach((_, v) => G.nodeClass(v, st.cover.includes(v) ? "chosen" : ""));
          run.edges.forEach(([u, v]) => G.edgeClass(`${u}-${v}`, st.cover.includes(u) || st.cover.includes(v) ? "good" : ""));
        }
        if (st.focus !== null && st.focus !== undefined && !(st.cover && st.cover.includes(st.focus))) G.nodeClass(st.focus, "hot");
        const rows = run.weights.map((w, v) => [v, w, st.inc[v] ?? "", st.exc[v] ?? ""]);
        V.table(panel, ["vertex", "w", "in", "out"], rows, (i, j) => (i >= 0 && i === st.focus ? "viz-hl" : null));
        if (st.cover) html("div", { class: "viz-readout" }, panel, `cover so far: {${st.cover.join(", ")}}`);
      },
    });
  });
})();
