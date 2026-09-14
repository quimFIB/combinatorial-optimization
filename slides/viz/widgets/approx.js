// Part V figures: hardness (unit 22), combinatorial approximation (23), LP rounding and
// primal–dual (24), semidefinite relaxations (25). Needs slides/viz/viz.js; data from
// slides/viz/traces/u22.py … u25.py through each unit's viz-data.js.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // A side-by-side frame for figures that are not steppers: svg on the left, panel on the right.
  const frame = (host, W, H, label) => {
    host.classList.add("viz-side");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const svg = V.newSvg(left, W, H, label);
    const controls = html("div", { class: "viz-controls" }, left);
    const right = html("div", { class: "viz-right" }, host);
    return { left, svg, controls, right };
  };
  // A run picker for non-stepper figures; onPick(index).
  const picker = (parent, runs, onPick) => {
    if (runs.length < 2) return null;
    const s = html("select", { class: "viz-pick", "aria-label": "choose an instance" }, parent);
    runs.forEach((r, i) => html("option", { value: i }, s, r.title));
    s.addEventListener("change", () => onPick(Number(s.value)));
    return s;
  };
  const frac = (s) => { const [a, b] = String(s).split("/").map(Number); return b ? a / b : a; };

  // ---------------------------------------------------------------- 22 · the gadget
  // data-key="gadget". Toggle the variables; the forward rule's vertex set is drawn, with any
  // edge it leaves uncovered.
  V.register("gadget", (host) => {
    const d = V.data(host, host.dataset.key || "gadget");
    if (!d) return;
    const W = 540, H = 330;
    const { svg, controls, right } = frame(host, W, H, "3-SAT to vertex cover gadget with the cover built from an assignment");
    const n = d.nvars, m = d.clauses.length;
    const nodes = [];
    for (let v = 0; v < n; v++) {
      nodes.push({ id: 2 * v, x: 55 + 180 * v, y: 60, label: `x${v + 1}` });
      nodes.push({ id: 2 * v + 1, x: 125 + 180 * v, y: 60, label: `¬x${v + 1}` });
    }
    for (let j = 0; j < m; j++) {
      const cx = W / (m + 1) * (j + 1);
      [[cx - 50, 270], [cx, 190], [cx + 50, 270]].forEach(([x, y], t) =>
        nodes.push({ id: 2 * n + 3 * j + t, x, y, label: String(t + 1), noteDy: 32 }));
    }
    const edges = d.edges.map(([u, v]) => ({ id: `${u}-${v}`, u, v }));
    const bits = d.assignments[0].values.map(() => true);
    const buttons = bits.map((_, v) => {
      const b = html("button", { type: "button", class: "viz-btn" }, controls, "");
      b.addEventListener("click", () => { bits[v] = !bits[v]; draw(); });
      return b;
    });
    const note = html("div", { class: "viz-note" }, right);
    const clauseBox = html("div", {}, right);
    const readout = html("div", { class: "viz-readout" }, right);
    const explain = html("div", { class: "viz-explain" }, right);
    const lit = (l) => (l > 0 ? "x" : "¬x") + Math.abs(l);

    function draw() {
      svg.replaceChildren();
      const g = V.graph(svg, { nodes, edges }, { radius: 17 });
      for (let j = 0; j < m; j++) {
        const cx = W / (m + 1) * (j + 1);
        V.text(svg, cx, 318, d.clauses[j].map(lit).join(" ∨ "), "viz-label-soft");
      }
      const a = d.assignments.find((s) => s.values.every((x, i) => x === bits[i]));
      buttons.forEach((b, v) => { b.textContent = `x${v + 1} = ${bits[v] ? "true" : "false"}`; });
      d.edges.forEach(([u, v]) => {
        const variableEdge = u < 2 * n && v < 2 * n, triangle = u >= 2 * n && v >= 2 * n;
        g.edgeClass(`${u}-${v}`, variableEdge || triangle ? "" : "muted");
      });
      a.cover.forEach((c, id) => g.nodeClass(id, c ? "chosen" : ""));
      a.uncovered.forEach(([u, v]) => { g.edgeClass(`${u}-${v}`, "warn"); g.nodeClass(u, "warn"); g.nodeClass(v, "warn"); });
      note.textContent = a.satisfies ? `Satisfies the formula: a cover of size ${a.size} = k` : "Does not satisfy the formula";
      clauseBox.replaceChildren();
      V.table(clauseBox, ["clause", "true literal?"], d.clauses.map((c, j) => [c.map(lit).join(" ∨ "), a.clauses[j] ? "yes" : "none"]),
        (i, j) => (i >= 0 && j === 1 ? (a.clauses[i] ? "viz-goodcell" : "viz-bad") : null));
      readout.textContent = `k = n + 2m = ${d.k}; the smallest cover of this graph has ${d.min_cover} vertices (brute force over ${2 ** d.n} sets).`;
      explain.textContent = a.satisfies
        ? "Filled: the true literals, and in each triangle every corner but one whose literal is true. That corner's edge upward is covered by the literal. Every edge has a filled end."
        : `No true literal in some clause, so every corner of its triangle points at a false literal. Taking ${d.k} vertices the same way leaves the red edge uncovered, and any cover of this graph with ${d.k} vertices would give a satisfying assignment.`;
    }
    draw();
  });

  // ---------------------------------------------------------------- 22 · the FPTAS
  V.register("fptas", (host) => {
    const d = V.data(host, host.dataset.key || "fptas");
    if (!d) return;
    host.classList.add("viz-stack");
    V.isolate(host);
    const top = html("div", {}, host);
    const idx0 = d.runs.findIndex((r) => Math.abs(r.eps - 0.5) < 1e-9);
    const tableBox = html("div", {}, host);
    const readouts = html("div", {}, host);
    V.slider(top, { label: "ε", min: 0, max: d.runs.length - 1, step: 1, value: idx0, format: (i) => num(d.runs[i].eps) }, (i) => show(i));
    function show(i) {
      const r = d.runs[i];
      tableBox.replaceChildren();
      const rows = d.values.map((v, k) => [`item ${k}`, v, d.weights[k], num(v / r.K), r.scaled[k],
        d.opt_items.includes(k) ? "✓" : "", r.items.includes(k) ? "✓" : ""]);
      V.table(tableBox, ["", "value", "weight", "v / K", "rounded v′", "exact optimum", "FPTAS picks"], rows,
        (a, j) => (a >= 0 && j === 6 && rows[a][6] ? "viz-hl" : a >= 0 && j === 5 && rows[a][5] ? "viz-goodcell" : null));
      readouts.replaceChildren();
      const loss = (d.opt - r.value) / d.opt;
      html("div", { class: "viz-readout" }, readouts,
        `K = ε·v_max / n = ${num(r.eps)} · ${Math.max(...d.values)} / ${d.values.length} = ${num(r.K)}.  Value table: ${r.table_size} entries (exact: ${d.exact_table_size}).`);
      html("div", { class: "viz-readout" }, readouts,
        `FPTAS value ${r.value} (rounded score ${r.rounded_score}) against the optimum ${d.opt}: loss ${num(100 * loss, 1)}%, allowed ${num(100 * Math.min(r.eps, 1), 0)}%.`);
      html("div", { class: "viz-explain" }, readouts,
        `The proof guarantees at least OPT − nK = ${num(r.bound)}. ${r.bound <= 0 ? "At this ε the guarantee is empty. " : ""}` +
        "A larger ε means coarser rounding, a smaller table and a faster DP; the loss can jump up and back down, because rounding decides which ties it can still see.");
    }
    show(idx0);
  });

  // ---------------------------------------------------------------- 23 · greedy set cover
  V.register("greedycover", (host) => {
    const d = V.data(host, host.dataset.key || "setcover");
    if (!d) return;
    V.stepper(host, {
      runs: [{ title: "", states: d.states }], width: 520, height: 330, stepWord: "buy",
      render({ svg, panel, state }) {
        const U = d.universe, S = d.sets.length;
        const ex = (e) => 110 + e * 85, sy = (i) => 110 + i * 52;
        V.text(svg, 50, 62, "element", "viz-label-soft", "middle");
        V.text(svg, 50, 88, "price", "viz-label-soft", "middle");
        for (let e = 0; e < U; e++) {
          const covered = !state.uncovered.includes(e);
          el("circle", { cx: ex(e), cy: 58, r: 15, class: covered ? "viz-dot-good" : "viz-g-circle" }, svg);
          V.text(svg, ex(e), 63, String(e), covered ? "viz-g-nlabel viz-onfill" : "viz-g-nlabel");
          if (state.price[e] !== null) V.text(svg, ex(e), 90, num(state.price[e]), "viz-probe-text");
        }
        d.sets.forEach((s, i) => {
          const bought = state.bought.includes(i), pick = state.pick === i;
          const xs = s.map(ex);
          el("rect", { x: Math.min(...xs) - 22, y: sy(i) - 16, width: Math.max(...xs) - Math.min(...xs) + 44, height: 32, rx: 16,
                       class: bought ? (pick ? "viz-set-pick" : "viz-set-bought") : "viz-set" }, svg);
          for (const e of s) el("circle", { cx: ex(e), cy: sy(i), r: 6, class: state.uncovered.includes(e) ? "viz-vertex" : "viz-vertex-seen" }, svg);
          V.text(svg, 50, sy(i) + 5, `S${i}`, "viz-label", "middle");
        });
        const rows = d.sets.map((s, i) => [`S${i}`, `{${s.join(",")}}`, d.costs[i],
          state.bought.includes(i) ? "bought" : (state.ratios[i] ?? "—")]);
        V.table(panel, ["set", "elements", "cost", "cost / new"], rows,
          (a, j) => (a >= 0 && a === state.pick ? "viz-hl" : a >= 0 && j === 3 && rows[a][3] === "bought" ? "viz-soft" : null));
        const done = !state.uncovered.length;
        state.explain = done
          ? `Greedy paid ${state.paid}, the sum of the prices. The optimum is ${d.opt} (S1 + S2). Price lemma on S2: its prices add to at most H₄·6 = 12.5.`
          : `Paid so far: ${state.paid}. The next purchase is the smallest cost per still-uncovered element (ties to the lower index).`;
      },
    });
  });

  // ---------------------------------------------------------------- 23 · metric TSP
  V.register("tsp", (host) => {
    const d = V.data(host, host.dataset.key || "tsp");
    if (!d) return;
    V.stepper(host, {
      runs: d, width: 520, height: 400, label: "double tree and Christofides step by step",
      render({ svg, panel, run, state }) {
        const pts = run.points;
        const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
        const pad = 40, W = 520, H = 400;
        const sx = (W - 2 * pad) / (Math.max(...xs) - Math.min(...xs) || 1), sy = (H - 2 * pad) / (Math.max(...ys) - Math.min(...ys) || 1);
        const s = Math.min(sx, sy);
        const X = (x) => pad + (x - Math.min(...xs)) * s, Y = (y) => pad + (y - Math.min(...ys)) * s;   // screen y grows down, as in the deck's figure
        const nodes = pts.map((p, i) => ({ id: i, x: X(p[0]), y: Y(p[1]) }));
        const dist = run.dist;
        const edges = [];
        const add = (u, v, id, bend) => edges.push({ id, u, v, label: dist[u][v], bend });
        const show = state.show;
        const tourEdges = (tour) => tour.map((v, i) => [v, tour[(i + 1) % tour.length]]);
        if (show === "tree" || show === "walk" || show === "odd") run.tree.forEach(([u, v]) => add(u, v, `t${u}-${v}`));
        if (show === "matching") { run.tree.forEach(([u, v]) => add(u, v, `t${u}-${v}`)); run.matching.forEach(([u, v]) => add(u, v, `m${u}-${v}`, 18)); }
        if (show === "circuit") {
          run.tree.forEach(([u, v]) => add(u, v, `t${u}-${v}`));
          run.matching.forEach(([u, v]) => add(u, v, `m${u}-${v}`, 18));
        }
        if (show === "tour") tourEdges(run.tourlist).forEach(([u, v], i) => add(u, v, `r${i}`));
        const g = V.graph(svg, { nodes, edges }, { radius: 13 });
        edges.forEach((e) => g.edgeClass(e.id, e.id[0] === "m" ? "warn" : e.id[0] === "r" ? "chosen" : show === "walk" ? "hot" : ""));
        if (show === "odd" || show === "matching") (run.odd || []).forEach((v) => g.nodeClass(v, "warn"));
        const len = (tour) => tourEdges(tour).reduce((a, [u, v]) => a + dist[u][v], 0);
        const rows = [["MST weight (≤ OPT)", run.w_tree]];
        if (run.algo === "Christofides") rows.push(["matching weight (≤ OPT/2)", run.w_matching]);
        if (show === "walk") rows.push(["tree walk", run.walk.join(" ")]);
        if (show === "circuit") rows.push(["Euler circuit", run.circuit.join(" ")]);
        if (show === "tour") rows.push(["tour", `${run.tourlist.join(" ")}`], ["tour length", len(run.tourlist)], ["ratio to OPT", num(len(run.tourlist) / run.opt, 3)]);
        rows.push(["optimum (brute force)", run.opt]);
        V.table(panel, null, rows, (i, j) => (j === 0 ? "viz-bas" : null));
      },
    });
  });

  // ---------------------------------------------------------------- 24 · threshold rounding
  V.register("threshold", (host) => {
    const runs = V.data(host, host.dataset.key || "rounding");
    if (!runs) return;
    const { svg, controls, right } = frame(host, 440, 360, "vertex cover LP values and the cover rounding at a threshold");
    let run = runs[0], t = 0.5;
    picker(controls, runs, (i) => { run = runs[i]; draw(); });
    const sliderBox = html("div", {}, right);
    const note = html("div", { class: "viz-note" }, right);
    const tableBox = html("div", {}, right);
    const explain = html("div", { class: "viz-explain" }, right);
    V.slider(sliderBox, { label: "threshold t", min: 0.05, max: 1, step: 0.05, value: 0.5 }, (v) => { t = v; draw(); });
    function draw() {
      svg.replaceChildren();
      const n = run.n, cx = 220, cy = 180, R = 125;
      const nodes = Array.from({ length: n }, (_, i) => {
        const a = -Math.PI / 2 + 2 * Math.PI * i / Math.min(n, 5);
        const base = i < 5 ? [cx + R * Math.cos(a), cy + R * Math.sin(a)] : [cx + R * Math.cos(-Math.PI / 2 + 2 * Math.PI * 4 / 5) - 80, 60];
        return { id: i, x: base[0], y: base[1], label: String(run.weights[i]), noteDy: -26 };
      });
      const g = V.graph(svg, { nodes, edges: run.edges.map(([u, v]) => ({ u, v, id: `${u}-${v}` })) }, { radius: 18 });
      const cover = run.x.map((x) => (x >= t - 1e-9 ? 1 : 0));
      const weight = cover.reduce((a, c, i) => a + c * run.weights[i], 0);
      const uncovered = run.edges.filter(([u, v]) => !cover[u] && !cover[v]);
      run.x.forEach((x, i) => { g.nodeClass(i, cover[i] ? "chosen" : ""); g.nodeNote(i, `x=${num(x)}`); });
      uncovered.forEach(([u, v]) => g.edgeClass(`${u}-${v}`, "warn"));
      V.text(svg, 220, 350, "circle: vertex weight · note: LP value", "viz-label-soft");
      note.textContent = uncovered.length ? `t = ${num(t)}: not a cover (${uncovered.length} edge${uncovered.length > 1 ? "s" : ""} uncovered)` : `t = ${num(t)}: a cover of weight ${weight}`;
      tableBox.replaceChildren();
      V.table(tableBox, null, [["LP value", num(run.lp)], ["rounded weight", uncovered.length ? "—" : weight],
        ["bound 2·LP", num(2 * run.lp)], ["optimum", `${run.opt} (vertices ${run.opt_set.join(", ")})`]], (i, j) => (j === 0 ? "viz-bas" : null));
      explain.textContent = t > 0.5 + 1e-9
        ? "Above ½ a vertex at exactly ½ is dropped, and an edge with both ends at ½ loses its cover. Rounding at ½ is the largest threshold that always works."
        : "At or below ½ every edge keeps an end: x_u + x_v ≥ 1 forces one of them to be ≥ ½. Each chosen vertex has x ≥ t, so the weight is at most LP / t; t = ½ gives the factor 2.";
    }
    draw();
  });

  // ---------------------------------------------------------------- 24 · primal–dual set cover
  V.register("primaldual", (host) => {
    const d = V.data(host, host.dataset.key || "primaldual");
    if (!d) return;
    V.stepper(host, {
      runs: [{ title: "", states: d.states }], width: 520, height: 340, stepWord: "raise",
      render({ svg, panel, state }) {
        const U = d.universe, cx = 150, cy = 170, R = 95;
        const pos = (e) => [cx + R * Math.cos(-Math.PI / 2 + 2 * Math.PI * e / U), cy + R * Math.sin(-Math.PI / 2 + 2 * Math.PI * e / U)];
        d.sets.forEach((s, j) => {
          const [a, b] = s.map(pos);
          el("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: state.bought[j] ? "viz-set-line-bought" : "viz-set-line" }, svg);
          V.text(svg, (a[0] + b[0]) / 2 * 1.12 - cx * 0.12, (a[1] + b[1]) / 2 * 1.12 - cy * 0.12 + 4, `S${j}`, "viz-label");
        });
        for (let e = 0; e < U; e++) {
          const [x, y] = pos(e);
          el("circle", { cx: x, cy: y, r: 18, class: state.element === e ? "viz-g-circle viz-hot-circle" : state.covered[e] ? "viz-dot-good" : "viz-g-circle" }, svg);
          V.text(svg, x, y + 5, String(e), "viz-g-nlabel");
          V.text(svg, x + (x > cx ? 40 : -40), y + 5, `y=${num(state.y[e])}`, "viz-probe-text");
        }
        // bars: paid / cost per set
        const bx = 310, bw = 180;
        V.text(svg, bx, 40, "paid / cost", "viz-label-soft", "start");
        d.sets.forEach((s, j) => {
          const y = 70 + j * 62, p = frac(state.paid[j]), c = d.costs[j];
          el("rect", { x: bx, y, width: bw, height: 20, class: "viz-bar-bg" }, svg);
          el("rect", { x: bx, y, width: bw * p / c, height: 20, class: state.bought[j] ? "viz-bar-full" : "viz-bar" }, svg);
          V.text(svg, bx, y + 38, `S${j} = {${s.join(",")}}: ${num(state.paid[j])} / ${c}${state.bought[j] ? "  bought" : ""}`, "viz-label", "start");
        });
        const cost = d.costs.reduce((a, c, j) => a + (state.bought[j] ? c : 0), 0);
        const ysum = state.y.reduce((a, v) => a + frac(v), 0);
        V.table(panel, null, [["dual sum Σy (≤ OPT)", num(ysum)], ["cost bought", cost], ["f · Σy", num(d.f * ysum)], ["optimum", d.opt]],
          (i, j) => (j === 0 ? "viz-bas" : null));
        state.explain = state.explain || "A set's elements may pay at most its cost: that is dual feasibility. Raising one element's y until a set is fully paid, then buying it, keeps every bought set tight.";
      },
    });
  });

  // ---------------------------------------------------------------- 24 · Jain–Vazirani clocks
  V.register("jv", (host) => {
    const d = V.data(host, host.dataset.key || "jv");
    if (!d) return;
    host.classList.add("viz-stack");
    V.isolate(host);
    const W = 1000, H = 250;
    const svg = V.newSvg(host, W, H, "Jain-Vazirani dual ascent on a line");
    const bottom = html("div", {}, host);
    const readout = html("div", { class: "viz-readout" }, host);
    const tEnd = Math.max(...d.alpha) + 1;
    const X = (p) => 60 + p * 88;
    const nc = d.clients.length, nf = d.facilities.length;
    const alphaAt = (j, t) => Math.min(t, d.alpha[j]);
    const receipts = (i, t) => d.clients.reduce((a, _, j) => a + Math.max(0, alphaAt(j, t) - d.dist[i][j]), 0);
    function draw(t) {
      svg.replaceChildren();
      el("line", { x1: X(-0.4), y1: 150, x2: X(10.4), y2: 150, class: "viz-axis" }, svg);
      for (let p = 0; p <= 10; p++) V.text(svg, X(p), 172, String(p), "viz-tick");
      d.clients.forEach((c, j) => {
        const a = alphaAt(j, t), frozen = t >= d.alpha[j] - 1e-9;
        el("line", { x1: X(c - a), y1: 150 - 22 - j * 14, x2: X(c + a), y2: 150 - 22 - j * 14, class: frozen ? "viz-reach-frozen" : "viz-reach" }, svg);
        el("circle", { cx: X(c), cy: 150, r: 8, class: "fill-accent viz-client" }, svg);
        V.text(svg, X(c), 150 - 30 - j * 14, `c${j}: α=${num(a)}${frozen ? " (frozen)" : ""}`, "viz-probe-text");
      });
      d.facilities.forEach((f, i) => {
        const open = d.opened_at[i] !== undefined && t >= d.opened_at[i] - 1e-9;
        el("rect", { x: X(f) - 11, y: 139, width: 22, height: 22, class: open ? "viz-fac-open" : "viz-fac" }, svg);
        const r = receipts(i, t);
        el("rect", { x: X(f) - 40, y: 200, width: 80, height: 14, class: "viz-bar-bg" }, svg);
        el("rect", { x: X(f) - 40, y: 200, width: 80 * Math.min(1, r / d.open_cost[i]), height: 14, class: open ? "viz-bar-full" : "viz-bar" }, svg);
        V.text(svg, X(f), 234, `${"AB"[i]}: paid ${num(Math.min(r, d.open_cost[i]))} / ${d.open_cost[i]}${open ? " open" : ""}`, "viz-label");
      });
      const done = t >= Math.max(...d.alpha) - 1e-9;
      readout.textContent = done
        ? `All clients frozen: Σα = ${d.alpha_exact.join(" + ")} = ${num(d.alpha.reduce((a, b) => a + b, 0))}, a lower bound. Kept ${d.kept.map((i) => "AB"[i]).join(", ")}, cost ${d.cost}: optimal (brute force: ${Object.entries(d.brute).map(([k, v]) => `${k} ${v}`).join(", ")}).`
        : `t = ${num(t)}: every active client's α grows with t; once α passes a distance, the client pays the difference toward that facility.`;
    }
    V.slider(bottom, { label: "time t", min: 0, max: tEnd, step: 0.25, value: 0, format: (v) => num(v) }, draw);
    draw(0);
  });

  // ---------------------------------------------------------------- 25 · Goemans–Williamson
  V.register("gw", (host) => {
    const runs = V.data(host, host.dataset.key || "gw");
    if (!runs) return;
    const { svg, controls, right } = frame(host, 440, 440, "SDP vectors with a draggable random hyperplane");
    svg.classList.add("viz-gw-svg");
    let run = runs[0], theta = 10 * Math.PI / 180;
    picker(controls, runs, (i) => { run = runs[i]; draw(); });
    html("span", { class: "viz-count" }, controls, "drag the handle to turn the hyperplane");
    const note = html("div", { class: "viz-note" }, right);
    const tableBox = html("div", {}, right);
    const histSvg = V.newSvg(right, 420, 190, "histogram of cut sizes over recorded random hyperplanes");
    histSvg.classList.add("viz-hist");
    const explain = html("div", { class: "viz-explain" }, right);
    const C = [220, 220], R = 165;
    V.draggable(svg, (t) => t.classList.contains("viz-handle"), (x, y) => { theta = Math.atan2(-(y - C[1]), x - C[0]); draw(); });
    function draw() {
      svg.replaceChildren();
      el("circle", { cx: C[0], cy: C[1], r: R, class: "viz-dial" }, svg);
      const nrm = [Math.cos(theta), Math.sin(theta)];
      const side = run.vectors ? run.vectors.map((v) => (v[0] * nrm[0] + v[1] * nrm[1] >= 0 ? 1 : 0)) : null;
      if (run.vectors) {
        // the hyperplane is the line perpendicular to the normal
        const half = V.clip([[-1.3, -1.3], [1.3, -1.3], [1.3, 1.3], [-1.3, 1.3]], [-nrm[0], -nrm[1], 0]);
        el("polygon", { points: half.map((p) => `${C[0] + p[0] * R},${C[1] - p[1] * R}`).join(" "), class: "viz-halfplane" }, svg);
        el("line", { x1: C[0] - nrm[1] * 210, y1: C[1] - nrm[0] * 210, x2: C[0] + nrm[1] * 210, y2: C[1] + nrm[0] * 210, class: "viz-cut" }, svg);
        run.edges.forEach(([u, v]) => {
          const a = run.vectors[u], b = run.vectors[v];
          el("line", { x1: C[0] + a[0] * R, y1: C[1] - a[1] * R, x2: C[0] + b[0] * R, y2: C[1] - b[1] * R,
                       class: side[u] !== side[v] ? "viz-cutedge" : "viz-samedge" }, svg);
        });
        run.vectors.forEach((v, i) => {
          el("line", { x1: C[0], y1: C[1], x2: C[0] + v[0] * R, y2: C[1] - v[1] * R, class: side[i] ? "viz-vec-a" : "viz-vec-b" }, svg);
          el("circle", { cx: C[0] + v[0] * R, cy: C[1] - v[1] * R, r: 14, class: side[i] ? "viz-vec-dot-a" : "viz-vec-dot-b" }, svg);
          V.text(svg, C[0] + v[0] * R, C[1] - v[1] * R + 5, String(i), side[i] ? "viz-g-nlabel viz-onfill" : "viz-g-nlabel");
        });
        el("line", { x1: C[0], y1: C[1], x2: C[0] + nrm[0] * 70, y2: C[1] - nrm[1] * 70, class: "viz-arrow" }, svg);
        el("circle", { cx: C[0] + nrm[0] * 70, cy: C[1] - nrm[1] * 70, r: 10, class: "viz-handle" }, svg);
      } else {
        V.text(svg, 220, 220, "these vectors need more than two dimensions", "viz-label-soft");
      }
      const cut = side ? run.edges.reduce((a, [u, v], k) => a + (side[u] !== side[v] ? run.weights[k] : 0), 0) : null;
      note.textContent = cut === null ? run.title : `This hyperplane cuts weight ${cut} (optimum ${run.opt})`;
      tableBox.replaceChildren();
      V.table(tableBox, null, [["SDP bound", num(run.sdp, 3)], ["expected rounded cut", num(run.expected, 3)], ["optimum (brute force)", run.opt],
        ["expected / SDP", `${num(run.expected / run.sdp, 3)}  (α_GW ≈ ${num(run.alpha, 4)})`]], (i, j) => (j === 0 ? "viz-bas" : null));
      // histogram
      histSvg.replaceChildren();
      const keys = Object.keys(run.hist).map(Number).sort((a, b) => a - b);
      const lo = Math.min(...keys, run.expected) - 1, hi = Math.max(run.sdp, ...keys) + 1;
      const hx = (v) => 30 + (v - lo) / (hi - lo) * 370, maxc = Math.max(...Object.values(run.hist));
      el("line", { x1: 25, y1: 150, x2: 410, y2: 150, class: "viz-axis" }, histSvg);
      keys.forEach((k) => {
        const h = 120 * run.hist[k] / maxc;
        el("rect", { x: hx(k) - 7, y: 150 - h, width: 14, height: h, class: k === cut ? "viz-bar-full" : "viz-bar" }, histSvg);
        V.text(histSvg, hx(k), 166, String(k), "viz-tick");
      });
      for (const [v, cls, lab] of [[run.expected, "viz-mark-exp", "E"], [run.sdp, "viz-mark-sdp", "SDP"]]) {
        el("line", { x1: hx(v), y1: 20, x2: hx(v), y2: 150, class: cls }, histSvg);
        V.text(histSvg, hx(v), 16, lab, "viz-tick");
      }
      V.text(histSvg, 215, 186, `cut weights over ${run.rounds} recorded random hyperplanes`, "viz-label-soft");
      explain.textContent = keys.length === 1
        ? "Every hyperplane gives the same cut here: on an odd cycle's spread-out vectors any line through the centre splits them into two arcs, cutting all but one edge. The whole loss is between the SDP and the integers."
        : "Different hyperplanes cut different weights. Their average is the expected cut, at least α_GW ≈ 0.878 times the SDP bound, which is itself at least the optimum.";
    }
    draw();
  });

  // ---------------------------------------------------------------- 25 · PSD, 2×2
  V.register("psd2", (host) => {
    const { svg, controls, right } = frame(host, 360, 360, "two unit vectors realising a 2 by 2 matrix");
    const note = html("div", { class: "viz-note" }, right);
    const tableBox = html("div", {}, right);
    const explain = html("div", { class: "viz-explain" }, right);
    const C = [180, 180], R = 140;
    function draw(c) {
      svg.replaceChildren();
      el("circle", { cx: C[0], cy: C[1], r: R, class: "viz-dial" }, svg);
      const ok = Math.abs(c) <= 1 + 1e-12;
      note.textContent = `X = [[1, ${num(c)}], [${num(c)}, 1]]: eigenvalues ${num(1 + c)} and ${num(1 - c)}`;
      tableBox.replaceChildren();
      if (ok) {
        const ang = Math.acos(c);
        const v2 = [Math.cos(ang), Math.sin(ang)];
        el("line", { x1: C[0], y1: C[1], x2: C[0] + R, y2: C[1], class: "viz-vec-a" }, svg);
        el("line", { x1: C[0], y1: C[1], x2: C[0] + v2[0] * R, y2: C[1] - v2[1] * R, class: "viz-vec-b" }, svg);
        const arc = `M${C[0] + 40},${C[1]} A40,40 0 ${ang > Math.PI ? 1 : 0},0 ${C[0] + 40 * v2[0]},${C[1] - 40 * v2[1]}`;
        el("path", { d: arc, class: "viz-curve" }, svg);
        V.text(svg, C[0] + R + 4, C[1] - 8, "v₁", "viz-label", "start");
        V.text(svg, C[0] + v2[0] * (R + 16), C[1] - v2[1] * (R + 16), "v₂", "viz-label");
        V.table(tableBox, null, [["angle", `${num(ang * 180 / Math.PI, 1)}°`], ["v₁", "(1, 0)"], ["v₂", `(${num(v2[0], 3)}, ${num(v2[1], 3)})`], ["v₁ · v₂", num(c, 3)]], (i, j) => (j === 0 ? "viz-bas" : null));
        explain.textContent = "Both eigenvalues are ≥ 0: PSD. The matrix is the Gram matrix of two unit vectors whose inner product is the off-diagonal entry, a cosine.";
      } else {
        V.text(svg, C[0], C[1], "no such unit vectors", "viz-label-soft");
        explain.textContent = `An eigenvalue is negative: not PSD. Two unit vectors have inner product between −1 and 1, never ${num(c)}.`;
      }
    }
    V.slider(controls, { label: "off-diagonal entry", min: -1.5, max: 1.5, step: 0.05, value: -0.5 }, draw);
    draw(-0.5);
  });
})();
