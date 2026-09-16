// Unit 04 figures: the ellipsoid method replayed ("ellipsoid"), the central path of unit 01's
// polygon under a t slider ("centralpath"), and the one-variable barrier ("barrier1d").
// Needs slides/viz/viz.js; the first two need units/04-ellipsoid-interior-point/viz-data.js.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  const rowText = ([a, b, c]) => {
    const mag = (k, n) => (Math.abs(k) === 1 ? "" : num(Math.abs(k))) + n;
    let lhs = a ? (a < 0 ? "−" : "") + mag(a, "x") : "";
    if (b) lhs += lhs ? ` ${b < 0 ? "−" : "+"} ${mag(b, "y")}` : (b < 0 ? "−" : "") + mag(b, "y");
    return `${lhs || "0"} ≤ ${num(c)}`;
  };
  // Matrix entries span many magnitudes on long runs: small ones in scientific notation.
  const fmtP = (v) => (v !== 0 && Math.abs(v) < 0.01 ? v.toExponential(2).replace("-", "−") : num(v));
  // Boundary of {z : (z - c)^T P^-1 (z - c) <= 1} as a polygon, via the Cholesky factor of P.
  const ellipse = (c, P, n = 96) => {
    const l11 = Math.sqrt(P[0][0]), l21 = P[1][0] / l11, l22 = Math.sqrt(Math.max(P[1][1] - l21 * l21, 0));
    const pts = [];
    for (let i = 0; i < n; i++) {
      const th = (2 * Math.PI * i) / n, u = Math.cos(th), v = Math.sin(th);
      pts.push([c[0] + l11 * u, c[1] + l21 * u + l22 * v]);
    }
    return pts;
  };

  // ---------------------------------------------------------------- ellipsoid method
  //   data-runs="deck,corner,empty"   keys into window.VIZ_DATA (slides/viz/traces/u04.py)
  V.register("ellipsoid", (host) => {
    const keys = (host.dataset.runs || "").split(",").filter(Boolean);
    const runs = keys.map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    let follow = false, stepperApi = null;
    stepperApi = V.stepper(host, {
      runs, width: 480, height: 420, stepWord: "cut", label: "the ellipsoid, the target region and the cut",
      render(ctx) {
        const { svg, panel, run, k } = ctx;
        const st = run.states[k], prev = k > 0 ? run.states[k - 1] : null;
        const R = run.R;
        let box = [-R - 0.6, R + 0.6, -R - 0.6, R + 0.6];
        const cur = ellipse(st.center, st.P);
        let aspect = "equal";
        if (follow) {
          // Zoom each axis to the ellipse separately (never wider than the start view): a needle-thin
          // ellipse stays readable, at the price of unequal axis scales.
          const xs = cur.map((p) => p[0]), ys = cur.map((p) => p[1]);
          const cap = R + 0.6;
          const hx = Math.min(cap, Math.max((Math.max(...xs) - Math.min(...xs)) * 0.65, 0.03 * R));
          const hy = Math.min(cap, Math.max((Math.max(...ys) - Math.min(...ys)) * 0.65, 0.03 * R));
          const cx = st.center[0], cy = st.center[1];
          box = [cx - hx, cx + hx, cy - hy, cy + hy];
          aspect = "fill";
        }
        const P = V.plot(svg, box, 480, 420, { aspect });
        if (follow) V.text(svg, 470, 16, "zoomed: axes scaled separately", "viz-tick", "end");
        const rows = run.rows;
        const target = V.region(rows, box);
        rows.forEach((r) => {
          const seg = V.lineInBox(r, box);
          if (seg) el("line", { x1: P.X(seg[0][0]), y1: P.Y(seg[0][1]), x2: P.X(seg[1][0]), y2: P.Y(seg[1][1]), class: "viz-rowline" }, svg);
        });
        if (target.poly.length >= 3) el("polygon", { points: V.polyPoints(P, target.poly), class: "viz-target" }, svg);
        if (prev) el("polygon", { points: V.polyPoints(P, ellipse(prev.center, prev.P)), class: "viz-ellipse-prev" }, svg);
        el("polygon", { points: V.polyPoints(P, cur), class: "viz-ellipse" }, svg);
        if (!st.feasible && st.row !== null) {
          const [a, b] = rows[st.row];
          const through = a * st.center[0] + b * st.center[1];
          const kept = V.clip(cur, [a, b, through]);
          if (kept.length >= 3) el("polygon", { points: V.polyPoints(P, kept), class: "viz-shade-good" }, svg);
          const seg = V.lineInBox([a, b, through], box);
          if (seg) el("line", { x1: P.X(seg[0][0]), y1: P.Y(seg[0][1]), x2: P.X(seg[1][0]), y2: P.Y(seg[1][1]), class: "viz-cut" }, svg);
        }
        el("circle", { cx: P.X(st.center[0]), cy: P.Y(st.center[1]), r: 5, class: st.feasible ? "viz-vertex-opt" : "viz-dot-warn" }, svg);
        P.raise();

        const ratio = prev ? st.area / prev.area : null;
        V.table(panel, null, [
          ["step", String(k)],
          ["centre", `(${num(st.center[0])}, ${num(st.center[1])})`],
          ["area", `${num(st.area, st.area < 1 ? 4 : 2)}${ratio ? `   (× ${num(ratio, 3)})` : ""}`],
          ["most violated row", st.feasible ? "none: the centre is feasible" : `${rowText(rows[st.row])}, by ${num(st.violation)}`],
          ["P", `[[${fmtP(st.P[0][0])}, ${fmtP(st.P[0][1])}], [${fmtP(st.P[1][0])}, ${fmtP(st.P[1][1])}]]`],
        ], (i, j) => (j === 0 ? "viz-bas" : ""));
        if (st.feasible) {
          st.note = st.note || `feasible centre found after ${k} cut${k === 1 ? "" : "s"}`;
          st.explain = st.explain || "The centre satisfies every row, so the method stops here.";
        } else if (k === run.states.length - 1) {
          st.note = st.note || `still infeasible after ${k} cuts`;
          st.explain = st.explain || `The area is down to ${num(st.area, 4)}. Each step keeps ${num(run.ratio, 3)} of it, so a feasible set holding a ball of radius r would have been found by now for any r above about √(area/π) = ${num(Math.sqrt(st.area / Math.PI), 3)}: past the iteration bound, the method declares the set empty.`;
        } else {
          st.note = st.note || `centre violates ${rowText(rows[st.row])}`;
          st.explain = st.explain || `Shaded: the half of the ellipse on the feasible side of the line through the centre parallel to that row. The next ellipse is the smallest one containing it; in 2-D its area is ${num(run.ratio, 3)} of this one, whatever the cut.`;
        }
      },
    });
    const controls = host.querySelector(".viz-controls");
    if (controls && stepperApi) {
      const lab = html("label", { class: "viz-follow" }, controls);
      const cb = html("input", { type: "checkbox" }, lab);
      html("span", {}, lab, " zoom to the ellipse");
      cb.addEventListener("change", () => { follow = cb.checked; stepperApi.show(); });
    }
  });

  // ---------------------------------------------------------------- central path
  //   data-key="path"   window.VIZ_DATA[key] = {rows, c, points: [{t, x, y, s, gap, Aty, obj}]}
  V.register("centralpath", (host) => {
    const d = V.data(host, host.dataset.key || "path");
    if (!d) return;
    host.classList.add("viz-centralpath");
    V.isolate(host);
    const pts = d.points, rows = d.rows, m = rows.length;
    const left = html("div", { class: "viz-left" }, host);
    const W = 500, H = 420;
    const svg = V.newSvg(left, W, H, "the central path of the polygon and the current point x*(t)");
    const right = html("div", { class: "viz-right" }, host);
    let k = Math.floor(pts.length * 0.45);
    V.slider(right, { label: "t", min: 0, max: pts.length - 1, step: 1, value: k, format: (i) => num(pts[i].t, pts[i].t < 1 ? 3 : pts[i].t < 10 ? 2 : 1) },
      (i) => { k = i; draw(); });
    const read = html("div", {}, right);
    const names = ["−x ≤ 0", "−y ≤ 0", "x + y ≤ 4", "x − y ≤ 1"];

    function draw() {
      const p = pts[k];
      svg.replaceChildren();
      const box = [-0.5, 3.5, -0.5, 4.5];
      const P = V.plot(svg, box, W, H);
      const reg = V.region(rows, box);
      el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-poly" }, svg);
      el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-edge", fill: "none" }, svg);
      el("polyline", { points: pts.map((q) => `${P.X(q.x[0])},${P.Y(q.x[1])}`).join(" "), class: "viz-curve-soft" }, svg);
      el("polyline", { points: pts.slice(0, k + 1).map((q) => `${P.X(q.x[0])},${P.Y(q.x[1])}`).join(" "), class: "viz-curve" }, svg);
      const lvl = V.lineInBox([d.c[0], d.c[1], p.obj], box);
      if (lvl) el("line", { x1: P.X(lvl[0][0]), y1: P.Y(lvl[0][1]), x2: P.X(lvl[1][0]), y2: P.Y(lvl[1][1]), class: "viz-levelline" }, svg);
      for (const v of reg.vertices) el("circle", { cx: P.X(v[0]), cy: P.Y(v[1]), r: 4, class: "viz-vertex" }, svg);
      el("circle", { cx: P.X(p.x[0]), cy: P.Y(p.x[1]), r: 7, class: "viz-vertex-opt" }, svg);
      V.text(svg, P.X(p.x[0]) + 12, P.Y(p.x[1]) - 10, `x*(t) = (${num(p.x[0], 3)}, ${num(p.x[1], 3)})`, "viz-probe-text", "start");
      P.raise();

      read.replaceChildren();
      V.table(read, ["row", "slack s", "y = 1/(t s)", "y · s"], rows.map((r, i) => [names[i], num(p.s[i], 4), num(p.y[i], 4), num(p.y[i] * p.s[i], 4)]),
        (i, j) => (j === 0 ? "viz-bas" : j === 3 ? "viz-soft" : ""));
      V.table(read, null, [
        ["objective 2x + y", num(p.obj, 4), `optimum 6.5, short by ${num(6.5 - p.obj, 4)}`],
        ["Aᵀy", `(${num(p.Aty[0], 3)}, ${num(p.Aty[1], 3)})`, "= c = (2, 1): dual feasible"],
        ["gap bᵀy − cᵀx", num(p.gap, 4), `m/t = 4/${num(p.t, 2)} = ${num(m / p.t, 4)}`],
      ], (i, j) => (j === 0 ? "viz-bas" : j === 2 ? "viz-soft" : ""));
    }
    draw();
  });

  // ---------------------------------------------------------------- one-variable barrier
  //   f_t(x) = −t x − log x − log(1 − x) on (0, 1), computed in the page
  V.register("barrier1d", (host) => {
    host.classList.add("viz-barrier1d");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const W = 520, H = 360;
    const svg = V.newSvg(left, W, H, "the barrier function for one variable and its minimizer");
    const right = html("div", { class: "viz-right" }, host);
    let logt = 0;
    V.slider(right, { label: "log₁₀ t", min: -2, max: 2, step: 0.05, value: 0, format: (v) => `t = ${num(10 ** v, 10 ** v < 1 ? 3 : 1)}` },
      (v) => { logt = v; draw(); });
    const read = html("div", {}, right);
    const xstar = (t) => (t - 2 + Math.sqrt(t * t + 4)) / (2 * t);
    const f = (t, x) => -t * x - Math.log(x) - Math.log(1 - x);

    function draw() {
      const t = 10 ** logt, xs = xstar(t), fmin = f(t, xs);
      svg.replaceChildren();
      const P = V.plot(svg, [0, 1, fmin - 0.5, fmin + 6], W, H, { aspect: "fill", pad: 36 });
      const curve = [];
      for (let i = 1; i < 400; i++) {
        const x = i / 400, y = f(t, x);
        if (y <= fmin + 6.2) curve.push(`${P.X(x)},${P.Y(Math.min(y, fmin + 6))}`);
      }
      el("polyline", { points: curve.join(" "), class: "viz-curve" }, svg);
      el("line", { x1: P.X(xs), y1: P.Y(fmin - 0.5), x2: P.X(xs), y2: P.Y(fmin), class: "viz-levelline" }, svg);
      el("circle", { cx: P.X(xs), cy: P.Y(fmin), r: 7, class: "viz-vertex-opt" }, svg);
      el("circle", { cx: P.X(0.5), cy: P.Y(fmin - 0.5), r: 4, class: "viz-vertex" }, svg);
      V.text(svg, P.X(0.5), P.Y(fmin - 0.5) - 8, "½", "viz-label-soft");
      V.text(svg, P.X(xs) + 10, P.Y(fmin) - 12, `x*(t) = ${num(xs, 4)}`, "viz-probe-text", "start");
      P.raise();
      const y1 = 1 / (t * xs), y2 = 1 / (t * (1 - xs));
      read.replaceChildren();
      V.table(read, null, [
        ["x*(t)", num(xs, 4), "(t − 2 + √(t² + 4)) / 2t"],
        ["dual y", `(${num(y1, 3)}, ${num(y2, 3)})`, `−y₁ + y₂ = ${num(y2 - y1, 4)} = c`],
        ["gap y₂ − x*", num(y2 - xs, 4), `2/t = ${num(2 / t, 4)}`],
        ["true error 1 − x*", num(1 - xs, 4), "never more than the gap"],
      ], (i, j) => (j === 0 ? "viz-bas" : j === 2 ? "viz-soft" : ""));
    }
    draw();
  });
})();
