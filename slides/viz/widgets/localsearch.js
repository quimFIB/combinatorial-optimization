// Local search and annealing on small TSP instances (unit 26). Needs slides/viz/viz.js and the
// unit's viz-data.js (slides/viz/traces/u26.py).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // Fit city coordinates into an svg area, keeping aspect; returns [x, y] -> svg point.
  function fitter(coords, w, h, pad = 34) {
    const xs = coords.map((c) => c[0]), ys = coords.map((c) => c[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const s = Math.min((w - 2 * pad) / Math.max(x1 - x0, 1), (h - 2 * pad) / Math.max(y1 - y0, 1));
    const ox = (w - s * (x1 - x0)) / 2, oy = (h - s * (y1 - y0)) / 2;
    return (p) => [ox + (p[0] - x0) * s, h - oy - (p[1] - y0) * s];
  }

  function drawTour(svg, coords, tour, at, opts = {}) {
    const g = el("g", {}, svg);
    const n = tour.length;
    for (let i = 0; i < n; i++) {
      const [ax, ay] = at(coords[tour[i]]), [bx, by] = at(coords[tour[(i + 1) % n]]);
      el("line", { x1: ax, y1: ay, x2: bx, y2: by, class: opts.cls || "viz-ls-edge" }, g);
    }
    return g;
  }
  function drawCities(svg, coords, at, names, r = 11) {
    coords.forEach((c, i) => {
      const [x, y] = at(c);
      el("circle", { cx: x, cy: y, r, class: "viz-g-circle" }, svg);
      V.text(svg, x, y + 4, names ? names[i] : String(i), "viz-ls-city");
    });
  }
  const edgeLine = (svg, coords, at, [u, v], cls) => {
    const [ax, ay] = at(coords[u]), [bx, by] = at(coords[v]);
    el("line", { x1: ax, y1: ay, x2: bx, y2: by, class: cls }, svg);
  };

  // ---------------------------------------------------------------- 2-opt stepper
  //   data-runs="six,twelve-random,twelve-nn"   keys into VIZ_DATA.twoopt
  V.register("twoopt", (host) => {
    const all = V.data(host, "twoopt");
    if (!all) return;
    const runs = (host.dataset.runs || Object.keys(all).join(",")).split(",").map((k) => all[k]);
    if (runs.some((r) => !r)) return V.fail(host, "unknown run in data-runs");
    V.stepper(host, {
      runs, width: 520, height: 400, stepWord: "move", label: "2-opt moves on a small tour",
      render(ctx) {
        const { svg, panel, run, k, state } = ctx;
        const at = fitter(run.coords, 520, 400, run.names ? 50 : 34);
        const name = (c) => (run.names ? run.names[c] : String(c));
        drawTour(svg, run.coords, state.tour, at);
        if (state.move) {
          state.removed.forEach((e) => edgeLine(svg, run.coords, at, e, "viz-ls-removed"));
          state.added.forEach((e) => edgeLine(svg, run.coords, at, e, "viz-ls-added"));
        }
        drawCities(svg, run.coords, at, run.names, run.names ? 14 : 11);
        V.text(svg, 510, 20, `length ${state.length}`, "viz-ls-length", "end");

        html("div", { class: "viz-head" }, panel, "tour");
        html("div", { class: "viz-ls-order" }, panel, state.tour.map(name).join(" "));
        html("div", { class: "viz-head" }, panel, "length after each move");
        const rows = run.states.slice(0, k + 1).map((s, i) => [i === 0 ? "start" : `move ${i}`, s.length, i === 0 ? "" : s.length - run.states[i - 1].length]);
        V.table(panel, ["", "length", "change"], rows.slice(-8), (i, j) => (i === Math.min(rows.length, 8) - 1 ? "viz-hl" : j === 2 ? "viz-soft" : ""));
        if (rows.length > 8) html("div", { class: "viz-hint" }, panel, `(last 8 of ${rows.length} rows)`);
      },
    });
  });

  // ---------------------------------------------------------------- annealing run
  //   data-runs="hot,mean,cold"   keys into VIZ_DATA.anneal
  V.register("anneal", (host) => {
    const all = V.data(host, "anneal");
    if (!all) return;
    const keys = (host.dataset.runs || Object.keys(all).join(",")).split(",");
    const runs = keys.map((k) => all[k]);
    if (runs.some((r) => !r)) return V.fail(host, "unknown run in data-runs");
    host.classList.add("viz-anneal");
    V.isolate(host);

    const left = html("div", { class: "viz-left" }, host);
    const tourSvg = V.newSvg(left, 460, 330, "the annealing tour at the chosen iteration");
    const right = html("div", { class: "viz-right" }, host);
    const pick = html("select", { class: "viz-pick", "aria-label": "choose a run" }, html("div", { class: "viz-controls" }, right));
    runs.forEach((r, i) => html("option", { value: i }, pick, r.title));
    const traceSvg = V.newSvg(right, 520, 210, "tour length against iteration, with the temperature");
    const sliders = html("div", {}, right);
    const readout = html("div", { class: "viz-readout" }, right);
    const accept = html("div", { class: "viz-readout viz-cert" }, right);
    let run = runs[0], idx = 0, delta = 4;
    const itSlider = V.slider(sliders, { label: "iteration", min: 0, max: run.snaps.length - 1, step: 1, value: 0,
      format: (v) => String(run.snaps[v] ? run.snaps[v].it : v) }, (v) => { idx = v; draw(); });
    const dSlider = V.slider(sliders, { label: "a move costing Δ", min: 1, max: 40, step: 1, value: 4, format: (v) => `Δ = ${v}` },
      (v) => { delta = v; draw(); });

    function draw() {
      const s = run.snaps[Math.min(idx, run.snaps.length - 1)];
      tourSvg.replaceChildren();
      const at = fitter(run.coords, 460, 330, 24);
      drawTour(tourSvg, run.coords, s.tour, at);
      drawCities(tourSvg, run.coords, at, null, 9);
      V.text(tourSvg, 452, 18, `length ${s.length}`, "viz-ls-length", "end");

      traceSvg.replaceChildren();
      const lens = run.snaps.map((q) => q.length), maxL = Math.max(...lens), minL = Math.min(...lens);
      const P = V.plot(traceSvg, [0, run.iterations, 0, 1], 520, 210, { aspect: "fill", grid: false, pad: 30 });
      const yL = (v) => 0.05 + 0.9 * (v - minL) / Math.max(maxL - minL, 1);
      const yT = (t) => 0.05 + 0.9 * Math.log(t / run.t_end) / Math.max(Math.log(run.snaps[0].T / run.t_end), 1e-9);
      el("polyline", { points: run.snaps.map((q) => `${P.X(q.it)},${P.Y(yT(q.T))}`).join(" "), class: "viz-curve-soft" }, traceSvg);
      el("polyline", { points: run.snaps.map((q) => `${P.X(q.it)},${P.Y(yL(q.length))}`).join(" "), class: "viz-curve" }, traceSvg);
      el("line", { x1: P.X(s.it), y1: P.Y(0), x2: P.X(s.it), y2: P.Y(1), class: "viz-levelline" }, traceSvg);
      el("line", { x1: P.X(0), y1: P.Y(0), x2: P.X(run.iterations), y2: P.Y(0), class: "viz-axis" }, traceSvg);
      V.text(traceSvg, P.X(0) + 4, 16, `tour length, ${minL} to ${maxL}`, "viz-label", "start");
      V.text(traceSvg, P.X(run.iterations), 16, "temperature, log scale (grey)", "viz-label-soft", "end");
      V.text(traceSvg, P.X(run.iterations), 204, `${run.iterations} iterations`, "viz-tick", "end");

      readout.textContent = `iteration ${s.it}: T = ${num(s.T)}, length ${s.length}, best so far ${s.best}; ` +
        `worsening moves accepted so far: ${s.accepted_worse} of ${s.proposed_worse}`;
      const p = Math.exp(-delta / s.T);
      accept.textContent = `at this T, a move costing ${delta} is accepted with probability e^(−${delta}/${num(s.T)}) = ${p < 0.0005 ? p.toExponential(1) : num(p, 3)}`;
    }
    pick.addEventListener("change", () => { run = runs[Number(pick.value)]; itSlider.input.max = run.snaps.length - 1; idx = Math.min(idx, run.snaps.length - 1); itSlider.set(idx); });
    dSlider.set(4);
    draw();
  });
})();
