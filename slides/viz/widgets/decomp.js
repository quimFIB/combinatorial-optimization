// Decomposition figures: column generation (unit 10), Lagrangian relaxation and Held–Karp
// (unit 11), Benders (unit 12). Needs slides/viz/viz.js; recorded data from
// slides/viz/traces/u10.py, u11.py, u12.py.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num, text } = V;

  // A small two-series line chart over iterations 0..n-1, drawn up to (and marking) index k.
  // series: [{values, cls, label}]; returns nothing. Lives in the rectangle [x, y, w, h].
  function lineChart(svg, rect, series, k, opts = {}) {
    const [x0, y0, w, h] = rect;
    const all = series.flatMap((s) => s.values.filter((v) => v !== null && Number.isFinite(v)));
    let lo = opts.min ?? Math.min(...all), hi = opts.max ?? Math.max(...all);
    if (hi - lo < 1e-9) { hi += 1; lo -= 1; }
    const pad = (hi - lo) * 0.08; lo -= pad; hi += pad;
    const n = opts.n ?? Math.max(...series.map((s) => s.values.length));
    const X = (i) => x0 + (n <= 1 ? w / 2 : (i / (n - 1)) * w), Y = (v) => y0 + h - ((v - lo) / (hi - lo)) * h;
    el("rect", { x: x0, y: y0, width: w, height: h, class: "viz-chart-bg" }, svg);
    const step = V.niceStep(hi - lo, 4);
    for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) {
      el("line", { x1: x0, y1: Y(t), x2: x0 + w, y2: Y(t), class: "viz-grid" }, svg);
      text(svg, x0 - 6, Y(t) + 4, num(t, opts.digits ?? 2), "viz-tick", "end");
    }
    text(svg, x0 + w / 2, y0 + h + 16, opts.xlabel || "iteration", "viz-tick", "middle");
    for (const s of series) {
      const pts = s.values.slice(0, k + 1).map((v, i) => (v === null || !Number.isFinite(v) ? null : [X(i), Y(v)])).filter(Boolean);
      if (pts.length > 1) el("polyline", { points: pts.map((p) => p.join(",")).join(" "), class: s.cls }, svg);
      pts.forEach((p, i) => el("circle", { cx: p[0], cy: p[1], r: i === pts.length - 1 ? 4.5 : 2.5, class: s.dot }, svg));
    }
    series.forEach((s, i) => {
      const lx = x0 + w - 200;                                  // legend in the top-right corner
      el("line", { x1: lx, y1: y0 + 12 + i * 16, x2: lx + 18, y2: y0 + 12 + i * 16, class: s.cls }, svg);
      text(svg, lx + 23, y0 + 16 + i * 16, s.label, "viz-label-soft", "start");
    });
    return { X, Y };
  }

  // ---------------------------------------------------------------- unit 10: the loop
  //   data-key="small"  (window.VIZ_DATA.small from traces/u10.py)
  V.register("colgen", (host) => {
    const d = V.data(host, host.dataset.key || "small");
    if (!d) return;
    const pieceCls = ["viz-piece-a", "viz-piece-b", "viz-piece-c", "viz-piece-d"];
    V.stepper(host, {
      runs: [{ title: d.title, states: d.states }], width: 520, height: 420, stepWord: "iterate",
      label: "column generation: patterns as rolls, and the bounds so far",
      render({ svg, panel, run, k, state: st }) {
        // patterns as rolls, each bar W wide, split into its pieces; x_p to the right
        const left = 20, barW = 300, unit = barW / d.W, rowH = 30;
        text(svg, left, 22, "patterns in the restricted master", "viz-label-soft", "start");
        text(svg, left + barW + 16, 22, "rolls x", "viz-label-soft", "start");
        const rows = st.patterns.concat(st.done ? [] : [st.pricing]);
        rows.forEach((p, r) => {
          const y = 34 + r * rowH, isNew = !st.done && r === rows.length - 1;
          let x = left;
          p.forEach((cnt, i) => {
            for (let c = 0; c < cnt; c++) {
              el("rect", { x, y, width: d.widths[i] * unit - 2, height: rowH - 8, class: `${pieceCls[i % 4]}${isNew ? " viz-piece-new" : ""}` }, svg);
              text(svg, x + d.widths[i] * unit / 2 - 1, y + rowH / 2 + 1, String(d.widths[i]), "viz-piece-label", "middle");
              x += d.widths[i] * unit;
            }
          });
          el("rect", { x: left, y, width: barW - 2, height: rowH - 8, class: isNew ? "viz-roll viz-roll-new" : "viz-roll" }, svg);
          text(svg, left + barW + 16, y + rowH / 2 + 1, isNew ? "new: enters" : num(st.x[r]), isNew ? "viz-label viz-accent-text" : "viz-label", "start");
        });
        // bounds chart
        const top = 34 + (d.states[d.states.length - 1].patterns.length + 1) * rowH + 18;
        lineChart(svg, [60, top, 420, 400 - top - 10], [
          { values: run.states.map((s) => s.value), cls: "viz-curve", dot: "viz-vertex-opt", label: "master LP value (upper)" },
          { values: run.states.map((s) => s.best), cls: "viz-curve-bound", dot: "viz-dot-good", label: "best Farley bound (lower)" },
        ], k, { digits: 2 });

        V.table(panel, ["piece width", ...d.widths.map(String)], [
          ["demand", ...d.demands], ["dual y", ...st.duals.map((v) => num(v, 3))],
          ["pricing picks", ...st.pricing],
        ], (i, j) => (i === 2 && j > 0 ? "viz-hl" : j === 0 ? "viz-bas" : ""));
        V.table(panel, null, [
          ["master value", num(st.value, 3)],
          ["pattern's worth y·a", num(st.price_value, 3)],
          ["reduced cost 1 − y·a", num(st.reduced_cost, 3)],
          ["Farley bound (master value ÷ worth)", num(st.farley, 3)],
        ], (i, j) => (j === 0 ? "viz-bas" : i === 2 ? (st.done ? "viz-goodcell" : "viz-bad") : ""));
        st.note = st.done ? `No pattern is worth more than one roll: optimal at ${num(st.value, 3)}` :
          `Pricing finds a pattern worth ${num(st.price_value, 3)} rolls: it enters`;
        st.explain = st.done
          ? `The Farley bound has met the master value: ${num(st.best, 3)} rolls is the LP optimum over all patterns, and the solution here happens to be integral.`
          : `The duals price each piece in rolls. The pricing knapsack fills one roll of ${d.W} with the most valuable pieces; if they are worth more than 1, the pattern improves the master.`;
      },
    });
  });

  // ---------------------------------------------------------------- unit 10: smoothing
  //   data-key="smoothing"
  V.register("cgsmooth", (host) => {
    const d = V.data(host, host.dataset.key || "smoothing");
    if (!d) return;
    host.classList.add("viz-side");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const W = 560, H = 400;
    const svg = V.newSvg(left, W, H, "master value and best lower bound per iteration, for three smoothing weights");
    const controls = html("div", { class: "viz-controls" }, left);
    const buttons = d.runs.map((r, i) => {
      const b = html("button", { type: "button", class: "viz-btn" }, controls, `α = ${r.alpha}`);
      b.addEventListener("click", () => { pick = i; draw(); });
      return b;
    });
    const right = html("div", { class: "viz-right" }, host);
    html("div", { class: "viz-runtitle" }, right, d.title);
    const readout = html("div", { class: "viz-panel-body" }, right);
    let pick = 0, at = null;
    const maxIt = Math.max(...d.runs.map((r) => r.master.length));
    const sl = V.slider(right, { label: "iteration", min: 1, max: maxIt, step: 1, value: maxIt }, (v) => { at = v; draw(); });
    html("div", { class: "viz-explain" }, right,
      "α = 0 prices at the master's own duals. Larger α prices at a blend with the best duals so far, which damps the jumps. The gap closes in fewer iterations; each iteration may cost a second pricing call.");
    function draw() {
      svg.replaceChildren();
      buttons.forEach((b, i) => b.classList.toggle("viz-btn-on", i === pick));
      const r = d.runs[pick];
      const k = Math.min((at ?? maxIt) - 1, r.master.length - 1);
      const lo = Math.min(...d.runs.map((q) => q.bound[0])), hi = Math.max(...d.runs.map((q) => q.master[0]));
      const ch = lineChart(svg, [70, 20, 470, 340], [
        { values: r.master, cls: "viz-curve", dot: "viz-vertex-opt", label: "master LP value" },
        { values: r.bound, cls: "viz-curve-bound", dot: "viz-dot-good", label: "best Farley bound" },
      ], k, { min: lo, max: hi, digits: 1, n: maxIt });
      text(svg, 70 + 470, 376, `${r.master.length} iterations`, "viz-tick", "end");
      readout.replaceChildren();
      V.table(readout, ["α", "iterations to optimal"], d.runs.map((q) => [String(q.alpha), String(q.master.length)]),
        (i, j) => (i === pick ? "viz-hl" : ""));
      V.table(readout, null, [
        ["at iteration", String(k + 1)],
        ["master value", num(r.master[k], 2)],
        ["best lower bound", num(r.bound[k], 2)],
        ["gap", num(r.master[k] - r.bound[k], 2)],
      ], (i, j) => (j === 0 ? "viz-bas" : ""));
    }
    draw();
  });

  // ---------------------------------------------------------------- unit 11: L(u), draggable
  //   data-key="example"   (costs, weights, right-hand side, upper bound)
  const lag = (c, w, b, u) => {
    const x = c.map((ci, i) => (ci - u * w[i] < 0 ? 1 : 0));
    return { x, value: u * b + c.reduce((s, ci, i) => s + (ci - u * w[i]) * x[i], 0), g: b - w.reduce((s, wi, i) => s + wi * x[i], 0) };
  };
  function lagPlot(svg, ex, box, W, H) {
    const P = V.plot(svg, box, W, H, { aspect: "fill", pad: 40 });
    const pts = [];
    for (let i = 0; i <= 240; i++) { const u = box[0] + (box[1] - box[0]) * i / 240; pts.push([P.X(u), P.Y(lag(ex.c, ex.w, ex.b, u).value)]); }
    const z = V.lineInBox([0, 1, ex.upper], box);
    if (z) el("line", { x1: P.X(z[0][0]), y1: P.Y(ex.upper), x2: P.X(z[1][0]), y2: P.Y(ex.upper), class: "viz-cut" }, svg);
    text(svg, P.X(box[1]) - 4, P.Y(ex.upper) - 6, `z = ${ex.upper}`, "viz-label-soft", "end");
    el("polyline", { points: pts.map((p) => p.join(",")).join(" "), class: "viz-curve" }, svg);
    text(svg, P.X(box[1]) - 4, P.Y(box[2]) - 8, "u", "viz-label", "end");
    return P;
  }

  V.register("lagrangian", (host) => {
    const ex = V.data(host, host.dataset.key || "example");
    if (!ex) return;
    host.classList.add("viz-side");
    V.isolate(host);
    const W = 520, H = 400, box = [0, 2.4, 0, 8];
    const left = html("div", { class: "viz-left" }, host);
    const svg = V.newSvg(left, W, H, "L(u) with a draggable price u");
    const right = html("div", { class: "viz-right" }, host);
    const panel = html("div", { class: "viz-panel-body" }, right);
    let u = 1.0;
    const sl = V.slider(right, { label: "price u", min: 0, max: 2.4, step: 0.01, value: u }, (v) => { u = v; draw(); });
    html("div", { class: "viz-hint" }, right, "Drag the dot along the curve, or use the slider.");
    const drag = V.draggable(svg, (t) => t.classList.contains("viz-handle"), (x) => {
      u = Math.max(box[0], Math.min(box[1], Math.round(P.inv(x, 0)[0] * 100) / 100));
      sl.input.value = u; sl.input.dispatchEvent(new Event("input"));
    });
    let P = null;
    function draw() {
      svg.replaceChildren();
      P = lagPlot(svg, ex, box, W, H);
      const r = lag(ex.c, ex.w, ex.b, u);
      // the tangent piece at u: the affine function of the current x, slope g
      const aff = (v) => r.value + r.g * (v - u);
      el("line", { x1: P.X(box[0]), y1: P.Y(aff(box[0])), x2: P.X(box[1]), y2: P.Y(aff(box[1])), class: "viz-curve-soft" }, svg);
      el("line", { x1: P.X(u), y1: P.Y(0), x2: P.X(u), y2: P.Y(r.value), class: "viz-rowline" }, svg);
      el("circle", { cx: P.X(u), cy: P.Y(r.value), r: 9, class: "viz-handle" }, svg);
      text(svg, P.X(u) + 12, P.Y(r.value) - 12, `L(${num(u)}) = ${num(r.value)}`, "viz-probe-text", "start");
      P.raise();
      panel.replaceChildren();
      html("div", { class: "viz-note" }, panel, `L(${num(u)}) = ${num(r.value)}  ≤  ${ex.upper}`);
      V.table(panel, ["item", "cost c", "weight w", "c − u·w", "buy?"],
        ex.c.map((c, i) => [String(i + 1), String(c), String(ex.w[i]), num(c - u * ex.w[i]), r.x[i] ? "yes" : "no"]),
        (i, j) => (i >= 0 && j === 4 && r.x[i] ? "viz-goodcell" : i >= 0 && j === 3 && ex.c[i] - u * ex.w[i] < 0 ? "viz-hl" : ""));
      V.table(panel, null, [
        [`L(u) = ${ex.b}u + Σ bought (c − u·w)`, num(r.value)],
        ["subgradient g = b − w·x", num(r.g)],
        ["the price should", r.g > 0 ? "rise (row not covered)" : r.g < 0 ? "fall (row over-covered)" : "stay (row met exactly)"],
      ], (i, j) => (j === 0 ? "viz-bas" : ""));
      html("div", { class: "viz-explain" }, panel,
        "The faint line is the affine piece of the items bought at this u; L is the lowest such piece everywhere, so it is concave, and its kinks are where an item changes from not worth buying to worth it.");
    }
    draw();
  });

  // ---------------------------------------------------------------- unit 11: subgradient steps
  //   data-key="subgradient"  (runs), data-example="example"
  V.register("subgrad", (host) => {
    const runs = V.data(host, host.dataset.key || "subgradient");
    const ex = V.data(host, host.dataset.example || "example");
    if (!runs || !ex) return;
    const box = [0, 2.4, 0, 8];
    V.stepper(host, {
      runs, width: 520, height: 400, stepWord: "step", label: "subgradient steps on L(u)",
      render({ svg, panel, run, k, state: st }) {
        const P = lagPlot(svg, ex, box, 520, 400);
        const path = run.states.slice(0, k + 1);
        for (let i = 1; i < path.length; i++) {
          const a = path[i - 1], b = path[i];
          el("line", { x1: P.X(a.u), y1: P.Y(a.L), x2: P.X(b.u), y2: P.Y(b.L), class: "viz-pathline-thin" }, svg);
        }
        path.forEach((s, i) => el("circle", { cx: P.X(s.u), cy: P.Y(s.L), r: i === k ? 8 : 4, class: i === k ? "viz-vertex-opt" : "viz-vertex-seen" }, svg));
        el("line", { x1: P.X(box[0]), y1: P.Y(st.best), x2: P.X(box[1]), y2: P.Y(st.best), class: "viz-levelline" }, svg);
        text(svg, P.X(box[0]) + 6, P.Y(st.best) - 6, `best so far ${num(st.best)}`, "viz-label-soft", "start");
        P.raise();
        const prev = k > 0 ? run.states[k - 1] : null;
        V.table(panel, ["k", "u", "L(u)", "g", "best"],
          run.states.slice(Math.max(0, k - 7), k + 1).map((s, i, arr) => [String(Math.max(0, k - 7) + i), num(s.u, 3), num(s.L, 3), num(s.g), num(s.best, 3)]),
          (i, j, v) => (i >= 0 && Math.max(0, k - 7) + i === k ? "viz-hl" : ""));
        const down = prev && st.L < prev.L - 1e-9;
        st.note = down ? `L fell from ${num(prev.L, 3)} to ${num(st.L, 3)}: not an ascent method` : `L(${num(st.u, 3)}) = ${num(st.L, 3)}`;
        st.explain = `Each step moves u by t·g with the Polyak step t = λ (${ex.upper} − L(u)) / g², from unit 11's reference subgradient_ascent. ` +
          "Only the best value matters: every L(u) is a valid lower bound, including the ones that went down.";
      },
    });
  });

  // ---------------------------------------------------------------- unit 11: Held–Karp 1-trees
  //   data-key="heldkarp"
  V.register("heldkarp", (host) => {
    const runs = V.data(host, host.dataset.key || "heldkarp");
    if (!runs) return;
    V.stepper(host, {
      runs, width: 500, height: 420, stepWord: "step", label: "minimum 1-trees under the vertex penalties",
      render({ svg, panel, run, k, state: st }) {
        // Clustered city coordinates make an unreadable drawing: place the cities on a circle in
        // the angular order they have around their centre, so the shape is kept and labels breathe.
        const pts = run.points, n0 = pts.length;
        const cx = pts.reduce((t, p) => t + p[0], 0) / n0, cy = pts.reduce((t, p) => t + p[1], 0) / n0;
        const order = pts.map((p, i) => [Math.atan2(p[1] - cy, p[0] - cx), i]).sort((p, q) => p[0] - q[0]).map(([, i]) => i);
        const pos = [];
        order.forEach((i, r) => { const ang = -Math.PI / 2 + (2 * Math.PI * r) / n0; pos[i] = [250 + 160 * Math.cos(ang), 210 + 160 * Math.sin(ang)]; });
        const nodes = pts.map((_, i) => ({ id: i, x: pos[i][0], y: pos[i][1], label: String(i),
          noteDx: (pos[i][0] - 250) * 0.22, noteDy: (pos[i][1] - 210) * 0.22 - 3 }));
        const n = pts.length, inTree = new Set(st.edges.map(([a, b]) => `${a}-${b}`));
        const edges = [];
        for (let a = 0; a < n; a++) for (let b = a + 1; b < n; b++)
          if (inTree.has(`${a}-${b}`) || n <= 5) edges.push({ id: `${a}-${b}`, u: a, v: b, label: inTree.has(`${a}-${b}`) || n <= 5 ? String(run.dist[a][b]) : null });
        const G = V.graph(svg, { nodes, edges }, { radius: 15 });
        for (const e of edges) G.edgeClass(e.id, inTree.has(e.id) ? (e.u === 0 ? "good" : "chosen") : "muted");
        st.degrees.forEach((deg, v) => {
          G.nodeClass(v, deg === 2 ? "" : deg > 2 ? "warn" : "hot");
          G.nodeNote(v, `π ${num(st.pi[v], 1)}`);
        });
        text(svg, 10, 412, "thick: the 1-tree (green: its two edges at vertex 0) · numbers on edges: distances", "viz-label-soft", "start");
        V.table(panel, ["vertex", "π", "degree", "g = deg − 2"], st.degrees.map((deg, v) => [String(v), num(st.pi[v], 2), String(deg), num(deg - 2)]),
          (i, j, v) => (i >= 0 && j === 3 && Number(String(v).replace("−", "-")) !== 0 ? "viz-bad" : ""));
        V.table(panel, null, [
          ["L(π), this 1-tree", num(st.L, 2)], ["best bound so far", num(st.best, 2)], ["optimal tour", String(run.optimum)],
        ], (i, j) => (j === 0 ? "viz-bas" : i === 1 && Math.abs(st.best - run.optimum) < 1e-6 ? "viz-goodcell" : ""));
        st.note = st.tour ? `Every degree is 2: the 1-tree is a tour, and L = ${num(st.L, 2)} proves it optimal`
          : `1-tree of modified cost ${num(st.L, 2)}; degrees off 2 at ${st.degrees.filter((dg) => dg !== 2).length} vertices`;
        st.explain = "Edge costs become d + π_u + π_v. A vertex with too many tree edges (red) gets a higher penalty, a leaf (outlined) a lower one, so the next tree spreads out. The bound L can go down on a step; the best one counts.";
      },
    });
  });

  // ---------------------------------------------------------------- unit 12: Benders
  //   data-key="runs"
  V.register("benders", (host) => {
    const runs = V.data(host, host.dataset.key || "runs");
    if (!runs) return;
    V.stepper(host, {
      runs, width: 540, height: 400, stepWord: "iterate", label: "what the Benders master believes each choice costs",
      render({ svg, panel, run, k, state: st }) {
        const b = st.belief, n = b.length;
        const vals = b.flatMap((c) => [c.true, c.estimate]).filter((v) => v !== null);
        const top = Math.max(...vals) * 1.08;
        // one huge bar ("open nothing") would flatten the rest: cap the axis at 1.6× the second-largest true cost
        const trues = b.map((c) => c.true).filter((v) => v !== null).sort((p, q) => q - p);
        const cap = trues.length > 1 ? Math.min(top, trues[1] * 1.6) : top;
        const X0 = 60, X1 = 470, Y0 = 30, Y1 = 330, bw = (X1 - X0) / n;
        const Y = (v) => Y1 - Math.min(v, cap) / cap * (Y1 - Y0);
        const step = V.niceStep(cap, 5);
        for (let t = 0; t <= cap; t += step) {
          el("line", { x1: X0, y1: Y(t), x2: X1, y2: Y(t), class: "viz-grid" }, svg);
          text(svg, X0 - 6, Y(t) + 4, num(t, 0), "viz-tick", "end");
        }
        b.forEach((c, i) => {
          const x = X0 + i * bw + bw * 0.18, w = bw * 0.64;
          const isMaster = c.y.every((v, j) => v === st.master_y[j]);
          if (c.true !== null) el("rect", { x, y: Y(c.true), width: w, height: Y1 - Y(c.true), class: "viz-bar-true" }, svg);
          if (c.estimate !== null) el("rect", { x: x + w * 0.2, y: Y(c.estimate), width: w * 0.6, height: Y1 - Y(c.estimate), class: isMaster ? "viz-bar-est viz-bar-pick" : "viz-bar-est" }, svg);
          else text(svg, x + w / 2, Y1 - 8, "cut off", "viz-label-soft", "middle");
          if (c.true !== null && c.true > cap) text(svg, x + w / 2, Y0 - 6, `${num(c.true, 0)} ↑`, "viz-tick", "middle");
          text(svg, x + w / 2, Y1 + 16, c.y.map((v, j) => (v ? run.facilities[j] : "")).join("") || "none", isMaster ? "viz-label viz-accent-text" : "viz-label", "middle");
        });
        el("line", { x1: X0, y1: Y(st.lower), x2: X1, y2: Y(st.lower), class: "viz-levelline" }, svg);
        text(svg, X1 + 6, Y(st.lower) + 4, `LB ${num(st.lower, 1)}`, "viz-label-soft", "start");
        if (st.best !== null) {
          el("line", { x1: X0, y1: Y(st.best), x2: X1, y2: Y(st.best), class: "viz-cut" }, svg);
          text(svg, X1 + 6, Y(st.best) + (Math.abs(Y(st.best) - Y(st.lower)) < 14 ? -8 : 4), `UB ${num(st.best, 1)}`, "viz-label-soft", "start");
        }
        text(svg, X0, Y1 + 36, "outline: true cost of opening that set · filled: the master's estimate from its cuts", "viz-label-soft", "start");
        text(svg, X0, Y1 + 52, "which facilities are open", "viz-tick", "start");

        const fac = (y) => y.map((v, j) => (v ? run.facilities[j] : "")).join("") || "none";
        V.table(panel, null, [
          ["master picks", fac(st.master_y)], ["lower bound (master value)", num(st.lower, 2)],
          ["this choice's true cost", st.upper === null ? "infeasible" : num(st.upper, 2)], ["best upper bound", st.best === null ? "—" : num(st.best, 2)],
        ], (i, j) => (j === 0 ? "viz-bas" : ""));
        const linear = (c) => {
          let s = num(c.const, 2);
          c.coef.forEach((a, j) => { if (Math.abs(a) > 1e-9) s += ` ${a < 0 ? "−" : "+"} ${num(Math.abs(a), 2)}·y${run.facilities[j]}`; });
          return s;
        };
        const cuts = st.new_opt.map((c) => [`θ${c.s + 1} ≥`, linear(c)]).concat(st.new_feas.map((c) => ["feasibility:", `${linear(c)} ≤ 0`]));
        if (cuts.length) { html("div", { class: "viz-head" }, panel, "cuts this iteration adds"); V.table(panel, null, cuts, (i, j) => (j === 0 ? "viz-bas" : "")); }
        const closed = st.best !== null && st.best - st.lower <= 1e-6;
        st.note = closed ? `LB = UB = ${num(st.best, 2)}: optimal, open ${fac(st.master_y)}` : `Master picks ${fac(st.master_y)}; gap ${st.best === null ? "open" : num(st.best - st.lower, 2)}`;
        st.explain = "The master only knows the cuts so far, so its estimates (filled) sit below the true costs (outlines). It picks the cheapest estimate; solving the scenarios there gives a true cost (an upper bound) and new cuts that lift the estimates of that choice and its neighbours.";
      },
    });
  });
})();
