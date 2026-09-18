// Unit 03 figures: the value function z*(b) with its prices and ranges ("valuefn"), and the
// dual simplex after a cut, replayed from the reference solution ("dualsimplex").
// Needs slides/viz/viz.js; "dualsimplex" needs units/03-duality/viz-data.js.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // Optimum of max c·x over rows (2-D, bounded), by comparing corners. Returns
  // {x, z, pair, weights} where weights are the multipliers of the two tight rows that write c
  // as a nonnegative combination (the duals of those rows), or null if infeasible.
  function solve(rows, c) {
    const { vertices } = V.region(rows, [-1, 60, -1, 60]);
    if (!vertices.length) return null;
    let best = vertices[0];
    for (const v of vertices) if (c[0] * v[0] + c[1] * v[1] > c[0] * best[0] + c[1] * best[1] + 1e-9) best = v;
    const z = c[0] * best[0] + c[1] * best[1];
    const tight = V.tightRows(rows, best);
    for (let i = 0; i < tight.length; i++)
      for (let j = i + 1; j < tight.length; j++) {
        const ri = rows[tight[i]], rj = rows[tight[j]];
        const y = V.solve2([ri[0], rj[0], c[0]], [ri[1], rj[1], c[1]]);
        if (y && y[0] >= -1e-9 && y[1] >= -1e-9) {
          const weights = rows.map(() => 0);
          weights[tight[i]] = Math.max(0, y[0]); weights[tight[j]] = Math.max(0, y[1]);
          return { x: best, z, pair: [tight[i], tight[j]], weights };
        }
      }
    return { x: best, z, pair: tight.slice(0, 2), weights: rows.map(() => 0) };
  }

  // ---------------------------------------------------------------- value function
  //   data-c="3,2" data-rows='[[1,1,4],[2,1,6]]' (the two resource rows; x, y >= 0 are added)
  //   data-b1="0,8"  slider range for the first right-hand side
  V.register("valuefn", (host) => {
    const c = (host.dataset.c || "3,2").split(",").map(Number);
    const base = JSON.parse(host.dataset.rows || "[[1,1,4],[2,1,6]]");
    const [lo, hi] = (host.dataset.b1 || "0,8").split(",").map(Number);
    const sign = [[-1, 0, 0], [0, -1, 0]];
    let b = base.map((r) => r[2]);
    const rowsFor = (bb) => sign.concat(base.map((r, i) => [r[0], r[1], bb[i]]));

    host.classList.add("viz-valuefn");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const W = 460, H = 400;
    const svg = V.newSvg(left, W, H, "the feasible region for the current right-hand sides, and its optimum");
    const right = html("div", { class: "viz-right" }, host);
    const sliders = html("div", {}, right);
    const s1 = V.slider(sliders, { label: "b₁ in x + y ≤ b₁", min: lo, max: hi, step: 0.25, value: b[0] }, (v) => { b[0] = v; draw(); });
    const s2 = V.slider(sliders, { label: "b₂ in 2x + y ≤ b₂", min: 2, max: 10, step: 0.25, value: b[1] }, (v) => { b[1] = v; draw(); });
    const W2 = 440, H2 = 210;
    const curve = V.newSvg(right, W2, H2, "the optimum as a function of b1");
    const read = html("div", { class: "viz-readouts" }, right);

    function draw() {
      const rows = rowsFor(b);
      const sol = solve(rows, c);
      svg.replaceChildren();
      const box = [-0.5, 5.5, -0.5, 8.5];
      const P = V.plot(svg, box, W, H);
      const reg = V.region(rows, box);
      base.forEach((_, i) => {
        const seg = V.lineInBox(rows[2 + i], box);
        if (seg) el("line", { x1: P.X(seg[0][0]), y1: P.Y(seg[0][1]), x2: P.X(seg[1][0]), y2: P.Y(seg[1][1]), class: "viz-rowline" }, svg);
      });
      if (reg.poly.length >= 3) {
        el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-poly" }, svg);
        el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-edge", fill: "none" }, svg);
      }
      if (sol) {
        const lvl = V.lineInBox([c[0], c[1], sol.z], box);
        if (lvl) el("line", { x1: P.X(lvl[0][0]), y1: P.Y(lvl[0][1]), x2: P.X(lvl[1][0]), y2: P.Y(lvl[1][1]), class: "viz-levelline" }, svg);
        for (const v of reg.vertices) el("circle", { cx: P.X(v[0]), cy: P.Y(v[1]), r: 4, class: "viz-vertex" }, svg);
        el("circle", { cx: P.X(sol.x[0]), cy: P.Y(sol.x[1]), r: 8, class: "viz-vertex-opt" }, svg);
        V.text(svg, P.X(sol.x[0]) + 12, P.Y(sol.x[1]) - 10, `(${num(sol.x[0])}, ${num(sol.x[1])})  z* = ${num(sol.z)}`, "viz-probe-text", "start");
      }
      V.text(svg, P.X(0.2), P.Y(8.6), `max ${num(c[0])}x + ${num(c[1])}y`, "viz-label", "start");
      P.raise();

      // value function of b1, with b2 fixed; shade where the current pair of tight rows stays optimal
      curve.replaceChildren();
      const samples = [];
      for (let v = lo; v <= hi + 1e-9; v += 0.05) {
        const s = solve(rowsFor([v, b[1]]), c);
        samples.push({ b1: v, z: s ? s.z : NaN, key: s ? s.pair.join(",") + "|" + s.weights.map((w) => w.toFixed(3)).join(",") : "" });
      }
      const zs = samples.map((s) => s.z).filter(Number.isFinite);
      const Q = V.plot(curve, [lo, hi, 0, Math.max(...zs, 1) * 1.1], W2, H2, { aspect: "fill", pad: 30 });
      if (sol) {
        // The current prices hold while the corner where the same two rows meet stays feasible
        // (the weights don't depend on b). Find that interval of b1 exactly, by bisection.
        const [pi, pj] = sol.pair;
        const cornerOk = (v) => {
          const rs = rowsFor([v, b[1]]);
          const p = V.solve2(rs[pi], rs[pj]);
          return p && V.feasible(rs, p, 1e-9);
        };
        const edge = (inside, outside) => {
          if (cornerOk(outside)) return outside;
          for (let it = 0; it < 50; it++) { const mid = (inside + outside) / 2; if (cornerOk(mid)) inside = mid; else outside = mid; }
          return inside;
        };
        const ra = edge(b[0], lo), rz = edge(b[0], hi);
        el("rect", { x: Q.X(ra), y: Q.Y(Q.box[3]), width: Math.max(1, Q.X(rz) - Q.X(ra)),
                     height: Q.Y(Q.box[2]) - Q.Y(Q.box[3]), class: "viz-shade-good" }, curve);
        // the linear prediction z* + u (b1' - b1)
        const y1 = sol.weights[2];
        el("line", { x1: Q.X(lo), y1: Q.Y(sol.z + y1 * (lo - b[0])), x2: Q.X(hi), y2: Q.Y(sol.z + y1 * (hi - b[0])), class: "viz-levelline" }, curve);
        read.replaceChildren();
        const rng = `[${num(ra)}, ${num(rz)}]${ra <= lo + 1e-9 || rz >= hi - 1e-9 ? " (at least)" : ""}`;
        V.table(read, ["", "value", "reading"], [
          ["optimum", `z* = ${num(sol.z)}`, `at (${num(sol.x[0])}, ${num(sol.x[1])})`],
          ["price of constraint 1", `u = ${num(sol.weights[2])}`, sol.weights[2] ? "one more unit of b₁ adds this much" : "constraint 1 has slack: worth nothing"],
          ["price of constraint 2", `v = ${num(sol.weights[3])}`, sol.weights[3] ? "one more unit of b₂ adds this much" : "constraint 2 has slack: worth nothing"],
          ["range of b₁", rng, "shaded: the same prices hold"],
          ["check", `${num(b[0])}·${num(sol.weights[2])} + ${num(b[1])}·${num(sol.weights[3])}`, `= ${num(b[0] * sol.weights[2] + b[1] * sol.weights[3])}, equal to z*`],
        ], (i, j) => (j === 0 ? "viz-bas" : j === 2 ? "viz-soft" : ""));
      }
      const pts = samples.filter((s) => Number.isFinite(s.z)).map((s) => `${Q.X(s.b1)},${Q.Y(s.z)}`).join(" ");
      el("polyline", { points: pts, class: "viz-curve" }, curve);
      if (sol) el("circle", { cx: Q.X(b[0]), cy: Q.Y(sol.z), r: 6, class: "viz-vertex-opt" }, curve);
      V.text(curve, Q.X(lo) + 6, 16, "z*(b₁), with b₂ fixed; dashed: the linear prediction from the current price", "viz-label-soft", "start");
      Q.raise();
    }
    draw();
    void s1; void s2;
  });

  // ---------------------------------------------------------------- dual simplex replay
  //   data-runs="cut-x,cut-y,..."   keys into window.VIZ_DATA (slides/viz/traces/u03.py)
  V.register("dualsimplex", (host) => {
    const lp = V.data(host, "lp");
    if (!lp) return;
    const keys = (host.dataset.runs || "").split(",").filter(Boolean);
    const runs = keys.map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    V.stepper(host, {
      runs, width: 460, height: 400, stepWord: "pivot", label: "the feasible region, the cut, and the dual simplex's point",
      render(ctx) {
        const { svg, panel, run, k } = ctx;
        const st = run.states[k];
        const box = [-0.5, 4.5, -0.5, 6.5];
        const P = V.plot(svg, box, 460, 400);
        const rows = [[-1, 0, 0], [0, -1, 0]].concat(lp.A.map((r, i) => [r[0], r[1], lp.b[i]]));
        const reg = V.region(rows, box);
        el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-poly" }, svg);
        if (k > 0) {
          const [a, beta] = run.cut;
          const cutRow = [a[0], a[1], beta];
          const kept = V.region(rows.concat([cutRow]), box);
          const removed = V.clip(reg.poly, [-a[0], -a[1], -beta]);
          if (removed.length >= 3) el("polygon", { points: V.polyPoints(P, removed), class: "viz-shade-warn" }, svg);
          if (kept.poly.length >= 3) el("polygon", { points: V.polyPoints(P, kept.poly), class: "viz-edge", fill: "none" }, svg);
          const seg = V.lineInBox(cutRow, box);
          if (seg) el("line", { x1: P.X(seg[0][0]), y1: P.Y(seg[0][1]), x2: P.X(seg[1][0]), y2: P.Y(seg[1][1]), class: "viz-cut" }, svg);
          if (seg) V.text(svg, P.X(seg[1][0]) - 6, P.Y(seg[1][1]) + 16, run.cut_text, "viz-probe-text", "end");
        } else {
          el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-edge", fill: "none" }, svg);
        }
        for (let i = 1; i <= k; i++) {
          const p = run.states[i - 1].point, q = run.states[i].point;
          if (Math.hypot(p[0] - q[0], p[1] - q[1]) > 1e-9)
            el("line", { x1: P.X(p[0]), y1: P.Y(p[1]), x2: P.X(q[0]), y2: P.Y(q[1]), class: "viz-pathline" }, svg);
        }
        const feasibleNow = !st.infeasible && !st.tableau.slice(0, -1).some((r) => r[r.length - 1].startsWith("-"));
        el("circle", { cx: P.X(st.point[0]), cy: P.Y(st.point[1]), r: 8, class: feasibleNow ? "viz-vertex-opt" : "viz-dot-warn" }, svg);
        V.text(svg, P.X(st.point[0]) + 12, P.Y(st.point[1]) - 10,
          `(${st.point_exact.join(", ")})  z = ${st.z}${feasibleNow ? "" : "  infeasible"}`, "viz-probe-text", "start");
        P.raise();

        const cols = ["x", "y", "s1", "s2", "s3"].slice(0, st.tableau[0].length - 1);
        const header = ["basis", ...cols, "rhs"];
        const last = st.tableau.length - 1;
        const rowsT = st.tableau.map((r, i) => [i === last ? "z" : st.basis[i], ...r]);
        if (st.ratios) rowsT.push(["ratio", ...st.ratios.slice(0, cols.length).map((v) => v ?? ""), ""]);
        V.table(panel, header, rowsT, (i, j, v) => {
          const cls = [];
          if (j === 0) cls.push("viz-bas");
          if (i === last) cls.push("viz-objrow");
          if (i === rowsT.length - 1 && st.ratios) cls.push("viz-ratio");
          if (i >= 0 && i < last && j === header.length - 1 && String(v).startsWith("-")) cls.push("viz-neg");
          if (st.leave !== null && i === st.leave) cls.push("viz-row-leave");
          if (st.enter !== null && j === st.enter + 1 && i >= 0) cls.push("viz-col-enter");
          if (st.leave !== null && i === st.leave && st.enter !== null && j === st.enter + 1) cls.push("viz-pivot");
          return cls.join(" ");
        });
        html("div", { class: "viz-readout" }, panel,
          `duals (slack columns of the objective row): ${st.duals.map((d, i) => `y${i + 1} = ${num(d)}`).join(", ")}`);
      },
    });
  });
})();
