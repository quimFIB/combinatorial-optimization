// Unit 29 figures: gradient methods on a κ = 10 quadratic, and Frank–Wolfe / projected
// gradient on the simplex. Needs slides/viz/viz.js and units/29-*/viz-data.js.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // ---------------------------------------------------------------- gradient methods, live
  // f(x, y) = ½(λ₁x² + λ₂y²). The page computes every iterate itself, after checking its
  // arithmetic against the reference solution's recorded iterates (viz-data.js "gd").
  V.register("gd-quadratic", (host) => {
    const d = V.data(host, "gd");
    if (!d) return;
    const [l1, l2] = d.eig;
    const grad = ([x, y]) => [l1 * x, l2 * y];
    const f = ([x, y]) => 0.5 * (l1 * x * x + l2 * y * y);
    const run = (method, x0, t, beta, n) => {
      const xs = [x0.slice()];
      let prev = x0.slice();
      for (let k = 0; k < n; k++) {
        const x = xs[xs.length - 1];
        let next;
        if (method === "gd") { const g = grad(x); next = [x[0] - t * g[0], x[1] - t * g[1]]; }
        else if (method === "hb") { const g = grad(x); next = [x[0] - t * g[0] + beta * (x[0] - prev[0]), x[1] - t * g[1] + beta * (x[1] - prev[1])]; }
        else {  // nesterov, as the reference writes it
          const m = (k - 1) / (k + 2), y = [x[0] + m * (x[0] - prev[0]), x[1] + m * (x[1] - prev[1])], g = grad(y);
          next = [y[0] - t * g[0], y[1] - t * g[1]];
        }
        prev = x;
        xs.push(next);
      }
      return xs;
    };
    // agreement with the reference solution, before drawing anything
    const same = (a, b) => a.length === b.length && a.every((p, i) => Math.abs(p[0] - b[i][0]) < 1e-9 && Math.abs(p[1] - b[i][1]) < 1e-9);
    const n0 = d.checks["gd-0.1"].length - 1;
    if (!same(run("gd", d.start, 0.1, 0, n0), d.checks["gd-0.1"]) || !same(run("gd", d.start, 0.19, 0, n0), d.checks["gd-0.19"]) ||
        !same(run("hb", d.start, 0.1, 0.5, n0), d.checks["hb-0.1-0.5"]) || !same(run("nesterov", d.start, 0.1, 0, n0), d.checks["nesterov-0.1"]))
      return V.fail(host, "the page's iterates disagree with the reference solution's");

    host.classList.add("viz-side");
    V.isolate(host);
    const W = 560, H = 430, box = [-1.6, 1.6, -1.3, 1.3];
    const left = html("div", { class: "viz-left" }, host);
    const svg = V.newSvg(left, W, H, "iterates of a gradient method on an elongated quadratic bowl; drag the start point");
    const right = html("div", { class: "viz-right" }, host);
    let state = { method: "gd", t: 0.1, beta: 0.5, x0: d.start.slice(), n: 25 };

    const methodRow = html("div", { class: "viz-controls" }, right);
    const pick = html("select", { class: "viz-pick", "aria-label": "method" }, methodRow);
    for (const [v, lab] of [["gd", "gradient descent"], ["hb", "heavy ball (momentum)"], ["nesterov", "Nesterov"]]) html("option", { value: v }, pick, lab);
    pick.addEventListener("change", () => { state.method = pick.value; betaWrap.style.display = state.method === "hb" ? "" : "none"; draw(); });
    const tSlider = V.slider(right, { label: "step t", min: 0.01, max: 0.25, step: 0.005, value: 0.1, format: (v) => num(v, 3) }, (v) => { state.t = v; draw(); });
    const betaHost = html("div", {}, right);
    const betaWrap = betaHost;
    V.slider(betaHost, { label: "momentum β", min: 0, max: 0.95, step: 0.05, value: 0.5 }, (v) => { state.beta = v; draw(); });
    betaWrap.style.display = "none";
    V.slider(right, { label: "steps", min: 1, max: 60, step: 1, value: 25 }, (v) => { state.n = v; draw(); });
    const presets = html("div", { class: "viz-controls" }, right);
    for (const [lab, t] of [["t = 1/L", 0.1], ["t = 2/(L+μ)", 2 / 11], ["t = 0.19", 0.19], ["t = 0.21", 0.21]]) {
      const b = html("button", { type: "button", class: "viz-btn" }, presets, lab);
      b.addEventListener("click", () => tSlider.set(t));
    }
    const readout = html("div", { class: "viz-readout" }, right);
    const factors = html("div", { class: "viz-readout" }, right);
    const tableHost = html("div", {}, right);
    html("div", { class: "viz-hint" }, right, "Drag the large dot to move the start. The dashed ellipses are level sets of f; the steep direction is y.");

    V.draggable(svg, (t) => t.classList.contains("viz-handle"), (sx, sy) => {
      const [x, y] = P.inv(sx, sy);
      state.x0 = [Math.max(box[0], Math.min(box[1], Math.round(x * 20) / 20)), Math.max(box[2], Math.min(box[3], Math.round(y * 20) / 20))];
      draw();
    });
    let P = null;

    function draw() {
      svg.replaceChildren();
      P = V.plot(svg, box, W, H, { step: [0.5, 0.5] });
      for (const c of [0.02, 0.1, 0.3, 0.7, 1.4, 2.5, 4, 6]) {
        const rx = Math.sqrt(2 * c / l1) * P.sx, ry = Math.sqrt(2 * c / l2) * P.sy;
        el("ellipse", { cx: P.X(0), cy: P.Y(0), rx, ry, class: "viz-curve-soft", "stroke-dasharray": "4 4" }, svg);
      }
      el("circle", { cx: P.X(0), cy: P.Y(0), r: 5, class: "viz-vertex-opt" }, svg);
      const xs = run(state.method, state.x0, state.t, state.beta, state.n);
      const clamp = (p) => [Math.max(box[0] - 0.2, Math.min(box[1] + 0.2, p[0])), Math.max(box[2] - 0.2, Math.min(box[3] + 0.2, p[1]))];
      const pts = xs.map((p) => clamp(p));
      el("polyline", { points: pts.map((p) => `${P.X(p[0])},${P.Y(p[1])}`).join(" "), class: "viz-curve" }, svg);
      pts.forEach((p, i) => { if (i) el("circle", { cx: P.X(p[0]), cy: P.Y(p[1]), r: 3.5, class: "viz-vertex" }, svg); });
      el("circle", { cx: P.X(state.x0[0]), cy: P.Y(state.x0[1]), r: 9, class: "viz-handle" }, svg);
      P.raise();

      const last = xs[xs.length - 1], fl = f(last), f0 = f(state.x0);
      const diverged = !Number.isFinite(fl) || fl > f0 * 1.000001;
      readout.textContent = `start (${num(state.x0[0])}, ${num(state.x0[1])}), f = ${num(f0, 3)};  after ${state.n} steps f = ${Number.isFinite(fl) ? (fl < 1e-4 ? fl.toExponential(2) : num(fl, 4)) : "∞"}` +
        (diverged ? "  — diverging" : "");
      readout.style.color = diverged ? "var(--warn)" : "";
      if (state.method === "gd") {
        const r1 = 1 - state.t * l1, r2 = 1 - state.t * l2;
        factors.textContent = `each step multiplies x by ${num(r1, 3)} and y by ${num(r2, 3)}` +
          (Math.abs(r2) >= 1 ? ": |factor| ≥ 1 in y, so it blows up (t ≥ 2/L = 0.2)" : r2 < 0 ? ": y changes sign every step (zig-zag)" : "");
      } else {
        factors.textContent = state.method === "hb" ? `x_{k+1} = x_k − t·∇f(x_k) + β(x_k − x_{k−1})` : `y_k = x_k + (k−1)/(k+2)·(x_k − x_{k−1}),  x_{k+1} = y_k − t·∇f(y_k)`;
      }
      tableHost.replaceChildren();
      const rows = xs.slice(0, 6).map((p, k) => [k, `(${num(p[0], 3)}, ${num(p[1], 3)})`, Number.isFinite(f(p)) ? num(f(p), 3) : "∞"]);
      V.table(tableHost, ["k", "point", "f"], rows, (i, j) => (j === 1 ? "viz-soft" : ""));
    }
    draw();
  });

  // ---------------------------------------------------------------- Frank–Wolfe and projection
  // The polytope {x ≥ 0, x₁ + x₂ + x₃ ≤ 1} drawn in an oblique projection; iterates recorded
  // from the reference frank_wolfe and projected_gradient (viz-data.js "fw").
  V.register("fw-simplex", (host) => {
    const d = V.data(host, "fw");
    if (!d) return;
    const proj3 = ([a, b, c]) => [a - 0.5 * c, b - 0.42 * c];
    const vec = (v) => `(${v.map((x) => num(x, 3)).join(", ")})`;
    V.stepper(host, {
      runs: [
        { title: "Frank–Wolfe", kind: "fw", states: d.fw },
        { title: "projected gradient", kind: "pg", states: d.pg },
      ],
      width: 520, height: 420, stepWord: "iterate", label: "iterates on the simplex, oblique view",
      render(ctx) {
        const { svg, panel, run, k, state } = ctx;
        const P = V.plot(svg, [-0.75, 1.25, -0.6, 1.2], 520, 420, { grid: false });
        const corner = { o: [0, 0, 0], e1: [1, 0, 0], e2: [0, 1, 0], e3: [0, 0, 1] };
        const at = (v) => { const q = proj3(v); return [P.X(q[0]), P.Y(q[1])]; };
        el("polygon", { points: [corner.o, corner.e1, corner.e2].map((v) => at(v).join(",")).join(" "), class: "viz-poly" }, svg);
        for (const [a, b] of [["o", "e1"], ["o", "e2"], ["o", "e3"], ["e1", "e2"], ["e1", "e3"], ["e2", "e3"]]) {
          const [x1, y1] = at(corner[a]), [x2, y2] = at(corner[b]);
          el("line", { x1, y1, x2, y2, class: a === "o" && b === "e3" ? "viz-edge-open" : "viz-edge" }, svg);
        }
        for (const [name, v, dx, dy] of [["0", corner.o, -14, 14], ["e₁", corner.e1, 12, 14], ["e₂", corner.e2, -8, -10], ["e₃", corner.e3, -14, 16]]) {
          const [x, y] = at(v);
          V.text(svg, x + dx, y + dy, name, "viz-label", "middle");
        }
        const [px, py] = at(d.p);
        el("circle", { cx: px, cy: py, r: 6, class: "viz-dot-warn" }, svg);
        V.text(svg, px, py - 12, "p", "viz-probe-text", "middle");
        const [qx, qy] = at(d.projection);
        el("circle", { cx: qx, cy: qy, r: 7, fill: "none", class: "viz-cut" }, svg);
        V.text(svg, qx - 10, qy - 14, "closest point", "viz-probe-text", "end");
        const path = state.path.map(at);
        el("polyline", { points: path.map((p) => p.join(",")).join(" "), class: "viz-pathline", fill: "none" }, svg);
        path.forEach((p, i) => el("circle", { cx: p[0], cy: p[1], r: i === k ? 7 : 4, class: i === k ? "viz-vertex-opt" : "viz-vertex-seen" }, svg));
        if (run.kind === "fw" && state.s) {
          const [sx, sy] = at(state.s), [xx, xy] = at(state.x);
          el("line", { x1: xx, y1: xy, x2: sx, y2: sy, class: "viz-cut" }, svg);
          el("circle", { cx: sx, cy: sy, r: 9, fill: "none", class: "viz-cut" }, svg);
        }

        const gapToOpt = state.f - d.fstar;
        const rows = [["x", vec(state.x)], ["f(x) = ½‖x − p‖²", num(state.f, 4)], ["f − f*", num(gapToOpt, 4)]];
        if (run.kind === "fw" && state.g) {
          rows.push(["gradient x − p", vec(state.g)], ["oracle vertex s", vec(state.s)], ["gap g·(x − s)", num(state.gap, 4)], ["next step size 2/(k+2)", num(state.step, 3)]);
          state.note = `iterate ${k}: the oracle picks ${vec(state.s)}`;
          state.explain = `The linear oracle minimises g·s over the polytope's corners, so it returns the unit vector with the most negative gradient entry. The gap ${num(state.gap, 3)} is a certificate: f − f* ≤ gap, and indeed ${num(gapToOpt, 3)} ≤ ${num(state.gap, 3)}.`;
        } else if (run.kind === "fw") {
          state.note = `iterate ${k}, after the last recorded step`;
          state.explain = "Frank–Wolfe never leaves the polytope and never projects; it zig-zags between corners toward (0.6, 0.4, 0), slowly.";
        } else {
          if (state.raw) rows.push(["before projecting", vec(state.raw)]);
          state.note = k === 0 ? "start: the projection of the origin onto x₁ + x₂ + x₃ = 1" : `iterate ${k}: step, then project`;
          state.explain = "Each step moves against the gradient and projects back onto the simplex (the reference projects onto the face x₁ + x₂ + x₃ = 1). It reaches the closest point within a few iterates.";
        }
        V.table(panel, null, rows, (i, j) => (j === 0 ? "viz-bas" : ""));
      },
    });
  });
})();
