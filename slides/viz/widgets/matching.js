// Matching figures for unit 15: König's cover, the Hungarian method's potentials, and
// Gale–Shapley's proposals. Needs slides/viz/viz.js and the unit's viz-data.js
// (slides/viz/traces/u15.py).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // ------------------------------------------------------------ König's cover
  //   data-run="konig"
  V.register("konig", (host) => {
    const run = V.data(host, host.dataset.run || "konig");
    if (!run) return;
    const ys = [90, 200, 310];
    V.stepper(host, {
      runs: [run], width: 520, height: 400, stepWord: "step", label: "bipartite graph, matching and cover",
      render({ svg, panel, state: st }) {
        const nodes = [];
        for (let l = 0; l < run.nl; l++) nodes.push({ id: `l${l}`, x: 130, y: ys[l], label: `ℓ${l}` });
        for (let r = 0; r < run.nr; r++) nodes.push({ id: `r${r}`, x: 390, y: ys[r], label: `r${r}` });
        const edges = run.edges.map(([l, r]) => ({ id: `${l}-${r}`, u: `l${l}`, v: `r${r}` }));
        const G = V.graph(svg, { nodes, edges }, { radius: 20 });
        V.text(svg, 130, 40, "left", "viz-label-soft", "middle");
        V.text(svg, 390, 40, "right", "viz-label-soft", "middle");
        const matched = new Set(st.matching.map(([l, r]) => `${l}-${r}`));
        run.edges.forEach(([l, r]) => G.edgeClass(`${l}-${r}`, matched.has(`${l}-${r}`) ? "chosen" : ""));
        if (st.edge) G.edgeClass(`${st.edge[0]}-${st.edge[1]}`, "hot");
        st.reach_l.forEach((l) => G.nodeClass(`l${l}`, "hot"));
        st.reach_r.forEach((r) => G.nodeClass(`r${r}`, "hot"));
        if (st.cover) {
          for (let l = 0; l < run.nl; l++) G.nodeClass(`l${l}`, st.cover.left.includes(l) ? "chosen" : "muted");
          for (let r = 0; r < run.nr; r++) G.nodeClass(`r${r}`, st.cover.right.includes(r) ? "chosen" : "muted");
          run.edges.forEach(([l, r]) => { if (!matched.has(`${l}-${r}`)) G.edgeClass(`${l}-${r}`, "good"); });
          V.text(svg, 260, 380, "filled: the cover · every edge touches it", "viz-label", "middle");
        }
        html("div", { class: "viz-readout" }, panel, `matching: ${st.matching.map(([l, r]) => `ℓ${l}r${r}`).join(", ")}`);
        html("div", { class: "viz-readout" }, panel, `reached: ${[...st.reach_l.map((l) => `ℓ${l}`), ...st.reach_r.map((r) => `r${r}`)].join(", ") || "none yet"}`);
        if (st.cover) html("div", { class: "viz-readout viz-cert" }, panel,
          `cover: ${[...st.cover.left.map((l) => `ℓ${l}`), ...st.cover.right.map((r) => `r${r}`)].join(", ")}`);
        html("div", { class: "viz-hint" }, panel, "Thick: matched edges. Outlined: reached by an alternating path.");
      },
    });
  });

  // ------------------------------------------------------------ Hungarian method
  //   data-run="hungarian"
  V.register("hungarian", (host) => {
    const run = V.data(host, host.dataset.run || "hungarian");
    if (!run) return;
    const n = run.cost.length, left = 130, top = 84, cs = 92;
    V.stepper(host, {
      runs: [run], width: 520, height: 400, stepWord: "step", label: "reduced cost matrix with potentials",
      render({ svg, panel, state: st }) {
        V.text(svg, left + n * cs / 2, 30, "columns j, with potential v", "viz-label-soft", "middle");
        V.text(svg, 20, top - 20, "rows, with u", "viz-label-soft", "start");
        const assigned = new Set(st.assign.map(([i, j]) => `${i},${j}`));
        for (let j = 0; j < n; j++) {
          V.text(svg, left + j * cs + cs / 2, top - 30, `column ${j + 1}`, st.tree_cols.includes(j) ? "viz-label strong-accent" : "viz-label", "middle");
          V.text(svg, left + j * cs + cs / 2, top - 12, `v = ${num(st.v[j])}`, "viz-tick", "middle");
        }
        for (let i = 0; i < n; i++) {
          const y = top + i * cs;
          V.text(svg, left - 16, y + cs / 2 - 4, `row ${i + 1}`, st.tree_rows.includes(i) ? "viz-label strong-accent" : "viz-label", "end");
          V.text(svg, left - 16, y + cs / 2 + 14, `u = ${num(st.u[i])}`, "viz-tick", "end");
          for (let j = 0; j < n; j++) {
            const x = left + j * cs, rc = st.reduced[i][j];
            const inTree = st.tree_rows.includes(i) || st.tree_cols.includes(j);
            const cls = ["viz-hu-cell", rc === 0 ? "tight" : "", inTree ? "tree" : "", assigned.has(`${i},${j}`) ? "assigned" : ""].join(" ");
            el("rect", { x: x + 4, y: y + 4, width: cs - 8, height: cs - 8, rx: 6, class: cls }, svg);
            V.text(svg, x + cs / 2, y + cs / 2 + 8, num(rc), "viz-hu-rc", "middle");
            V.text(svg, x + cs - 12, y + 22, `c=${run.cost[i][j]}`, "viz-tick", "end");
          }
        }
        V.text(svg, left + n * cs / 2, top + n * cs + 28, "big number: reduced cost c − u − v · outlined: assigned", "viz-label-soft", "middle");
        const total = st.assign.reduce((s, [i, j]) => s + run.cost[i][j], 0);
        const dual = st.u.reduce((a, b) => a + b, 0) + st.v.reduce((a, b) => a + b, 0);
        html("div", { class: "viz-readout" }, panel, `assigned: ${st.assign.map(([i, j]) => `row ${i + 1} → column ${j + 1}`).join(", ") || "nothing yet"}`);
        html("div", { class: "viz-readout" }, panel, `cost so far ${total} · Σu + Σv = ${num(dual)}`);
        html("div", { class: "viz-hint" }, panel, "Tinted cells have reduced cost 0 (tight). Highlighted rows and columns are in the current search tree.");
      },
    });
  });

  // ------------------------------------------------------------ Gale–Shapley
  //   data-run="gale"
  V.register("gale-shapley", (host) => {
    const run = V.data(host, host.dataset.run || "gale");
    if (!run) return;
    const ys = [90, 200, 310];
    V.stepper(host, {
      runs: [run], width: 520, height: 400, stepWord: "propose", label: "proposals and held pairs",
      render({ svg, panel, state: st }) {
        const nodes = [
          ...run.proposers.map((p, i) => ({ id: p, x: 130, y: ys[i], label: p, noteDx: -60, noteDy: 5 })),
          ...run.receivers.map((r, i) => ({ id: r, x: 390, y: ys[i], label: r, noteDx: 60, noteDy: 5 })),
        ];
        const edges = [];
        run.proposers.forEach((p) => run.receivers.forEach((r) => edges.push({ id: `${p}${r}`, u: p, v: r })));
        const G = V.graph(svg, { nodes, edges }, { radius: 20 });
        edges.forEach((e) => G.edgeClass(e.id, "muted"));
        Object.entries(st.holder).forEach(([r, p]) => G.edgeClass(`${p}${r}`, "chosen"));
        if (st.proposal) {
          const [p, r] = st.proposal;
          G.edgeClass(`${p}${r}`, st.answer === "reject" ? "warn" : "chosen");
          G.nodeClass(p, "hot");
        }
        st.free.forEach((p) => G.nodeNote(p, "free"));
        V.text(svg, 130, 40, "proposers", "viz-label-soft", "middle");
        V.text(svg, 390, 40, "receivers", "viz-label-soft", "middle");
        const rows = run.proposers.map((p, i) => [p, run.p_prefs[i].map((r, k) => (k < st.next[i] ? `(${r})` : r)).join(" ")])
          .concat(run.receivers.map((r, i) => [r, run.r_prefs[i].join(" ")]));
        V.table(panel, ["", "preferences, best first"], rows, (i, j) => (i >= 0 && st.proposal && rows[i][0] === st.proposal[0] ? "viz-hl" : null));
        html("div", { class: "viz-readout" }, panel, `held: ${Object.entries(st.holder).map(([r, p]) => `${r}–${p}`).join(", ") || "nobody yet"}`);
        html("div", { class: "viz-hint" }, panel, "Brackets: choices already proposed to. Thick: pairs currently held; red: a rejection.");
      },
    });
  });
})();
