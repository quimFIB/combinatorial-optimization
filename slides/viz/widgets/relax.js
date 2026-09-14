// Unit 31 figures: Sinkhorn's plan as the temperature and iteration count change, and
// Gumbel-max samples piling up into the softmax. Recorded from the reference solution
// (units/31-*/viz-data.js).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // ---------------------------------------------------------------- Sinkhorn
  V.register("sinkhorn", (host) => {
    const d = V.data(host, "sinkhorn");
    if (!d) return;
    host.classList.add("viz-side");
    V.isolate(host);
    const W = 520, H = 400;
    const left = html("div", { class: "viz-left" }, host);
    const svg = V.newSvg(left, W, H, "the 2 by 2 transport plan and its convergence");
    const right = html("div", { class: "viz-right" }, host);
    let ei = d.eps.indexOf(1), it = 30;
    V.slider(right, { label: "temperature ε", min: 0, max: d.eps.length - 1, step: 1, value: ei, format: (i) => num(d.eps[i]) }, (i) => { ei = i; draw(); });
    V.slider(right, { label: "iterations", min: 1, max: 30, step: 1, value: it }, (v) => { it = v; draw(); });
    const readout = html("div", {}, right);
    html("div", { class: "viz-hint" }, right, "Costs C = [[1, 3], [2, 5]]: the cheap assignment is the off-diagonal (3 + 2 = 5). Lower ε commits harder.");

    function draw() {
      svg.replaceChildren();
      const plan = Object.values(d.plans)[ei], rec = plan.iters[it - 1], P = rec.P;   // plans are in eps order
      // the plan as a 2x2 grid of shaded cells
      const x0 = 40, y0 = 60, cell = 110;
      V.text(svg, x0 + cell, 36, `plan P after ${it} iteration${it > 1 ? "s" : ""}, ε = ${num(d.eps[ei])}`, "viz-label", "middle");
      for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) {
        const x = x0 + j * cell, y = y0 + i * cell, v = P[i][j];
        el("rect", { x, y, width: cell - 6, height: cell - 6, rx: 6, class: "viz-g-circle", style: `fill: var(--accent); fill-opacity: ${Math.max(0.04, Math.min(1, v))}` }, svg);
        V.text(svg, x + (cell - 6) / 2, y + (cell - 6) / 2 + 2, num(v, 3), "viz-big", "middle").setAttribute("style", `fill: ${v > 0.55 ? "var(--surface)" : "var(--ink)"}; font-size: 20px`);
        V.text(svg, x + (cell - 6) / 2, y + (cell - 6) / 2 + 22, `cost ${num(d.C[i][j])}`, "viz-tick", "middle").setAttribute("style", v > 0.55 ? "fill: var(--surface)" : "");
      }

      // P11 against the iteration count, for this ε
      const pb = [x0 + 2 * cell + 20, 500, 150, 360];
      const iters = plan.iters.map((r) => r.P[0][0]);
      const X = (k) => pb[0] + (k - 1) / 29 * (pb[1] - pb[0]), Y = (v) => pb[3] - v * (pb[3] - pb[2]);
      el("rect", { x: pb[0], y: pb[2], width: pb[1] - pb[0], height: pb[3] - pb[2], fill: "none", class: "viz-dial" }, svg);
      el("line", { x1: pb[0], y1: Y(plan.closed_a), x2: pb[1], y2: Y(plan.closed_a), class: "viz-levelline" }, svg);
      el("polyline", { points: iters.map((v, k) => `${X(k + 1)},${Y(v)}`).join(" "), class: "viz-curve" }, svg);
      el("circle", { cx: X(it), cy: Y(P[0][0]), r: 5, class: "viz-vertex-opt" }, svg);
      V.text(svg, (pb[0] + pb[1]) / 2, pb[3] + 18, "P₁₁ by iteration (dashed: exact limit)", "viz-tick", "middle");
      V.text(svg, pb[0] - 4, Y(1) + 4, "1", "viz-tick", "end");
      V.text(svg, pb[0] - 4, Y(0) + 4, "0", "viz-tick", "end");

      readout.replaceChildren();
      const perm = plan.perm, hard = perm[0] === 1 ? "off-diagonal" : "diagonal";
      V.table(readout, null, [
        ["exact limit of P₁₁", num(plan.closed_a, 4)],
        ["P₁₁ now", num(P[0][0], 4)],
        ["row sums", `${num(rec.rows[0], 3)}, ${num(rec.rows[1], 3)}`],
        ["column sums", `${num(rec.cols[0], 3)}, ${num(rec.cols[1], 3)}`],
        ["greedy rounding", `${hard}, cost ${num(plan.cost)}`],
        ["smooth cost ⟨C, P⟩", num(P[0][0] * d.C[0][0] + P[0][1] * d.C[0][1] + P[1][0] * d.C[1][0] + P[1][1] * d.C[1][1], 3)],
      ], (i, j) => (j === 0 ? "viz-bas" : ""));
      html("div", { class: "viz-explain" }, readout,
        `The exact 2×2 limit has P₁₁ / (1 − P₁₁) = e^(−1/(2ε)). As ε shrinks the plan approaches the permutation; as ε grows it approaches ½ everywhere. At every ε the largest entry still points to the right assignment.`);
    }
    draw();
  });

  // ---------------------------------------------------------------- Gumbel-max
  V.register("gumbel", (host) => {
    const d = V.data(host, "gumbel");
    if (!d) return;
    host.classList.add("viz-side");
    V.isolate(host);
    const W = 520, H = 380;
    const left = html("div", { class: "viz-left" }, host);
    const svg = V.newSvg(left, W, H, "sample frequencies against the softmax");
    const right = html("div", { class: "viz-right" }, host);
    let ci = 0;
    V.slider(right, { label: "samples drawn", min: 0, max: d.checkpoints.length - 1, step: 1, value: 0, format: (i) => String(d.checkpoints[i][0]) }, (i) => { ci = i; draw(); });
    const readout = html("div", {}, right);
    const hand = html("div", {}, right);
    html("div", { class: "viz-head" }, hand, "one sample, by hand (default_rng(3))");
    V.table(hand, ["", "i = 1", "i = 2", "i = 3"], [
      ["uniform U", ...d.hand.u.map((v) => num(v, 3))],
      ["G = −log(−log U)", ...d.hand.g.map((v) => num(v, 3))],
      ["logit + G", ...d.hand.g.map((v, i) => num(v + d.logits[i], 3))],
    ], (i, j) => (i === 2 && j === d.hand.sample + 1 ? "viz-goodcell" : j === 0 ? "viz-bas" : ""));

    function draw() {
      svg.replaceChildren();
      const [n, counts] = d.checkpoints[ci];
      const bx = [70, 500], by = [40, 300], bw = 90;
      const Y = (v) => by[1] - v * (by[1] - by[0]);
      for (const v of [0, 0.25, 0.5, 0.75, 1]) {
        el("line", { x1: bx[0], y1: Y(v), x2: bx[1], y2: Y(v), class: v ? "viz-grid" : "viz-axis" }, svg);
        V.text(svg, bx[0] - 8, Y(v) + 4, num(v), "viz-tick", "end");
      }
      d.logits.forEach((l, i) => {
        const cx = bx[0] + 70 + i * 140, freq = counts[i] / n, sm = d.softmax[i];
        el("rect", { x: cx - bw / 2, y: Y(freq), width: bw, height: by[1] - Y(freq), style: "fill: var(--accent); fill-opacity: .75" }, svg);
        el("line", { x1: cx - bw / 2 - 8, y1: Y(sm), x2: cx + bw / 2 + 8, y2: Y(sm), class: "viz-cut" }, svg);
        V.text(svg, cx, Y(freq) - 8, num(freq, 3), "viz-label", "middle");
        V.text(svg, cx, by[1] + 18, `i = ${i + 1}, logit ${num(l)}`, "viz-tick", "middle");
      });
      V.text(svg, bx[1], 24, "bars: frequency · dashed: softmax", "viz-tick", "end");
      // the first 40 draws as a strip of dots
      const strip = d.first.slice(0, Math.min(40, n));
      strip.forEach((i, k) => el("circle", { cx: bx[0] + 6 + k * 10.8, cy: 350, r: 4, style: `fill: ${["var(--accent)", "var(--good)", "var(--warn)"][i]}` }, svg));
      V.text(svg, bx[0], 334, `first ${strip.length} draws (colour = which i won)`, "viz-tick", "start");

      readout.replaceChildren();
      V.table(readout, ["", "i = 1", "i = 2", "i = 3"], [
        ["count", ...counts.map(String)],
        ["frequency", ...counts.map((c) => num(c / n, 3))],
        ["softmax", ...d.softmax.map((v) => num(v, 3))],
      ], (i, j) => (j === 0 ? "viz-bas" : ""));
      html("div", { class: "viz-explain" }, readout, n < 30
        ? "With a handful of draws the frequencies are rough: any option can win a few times."
        : `After ${n} draws the frequencies sit within about ${num(1.96 * Math.sqrt(0.665 * 0.335 / n), 3)} of the softmax, the size of the sampling noise.`);
    }
    draw();
  });
})();
