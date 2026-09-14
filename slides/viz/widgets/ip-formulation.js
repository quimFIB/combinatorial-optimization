// Unit 05 figure: big-M against the tiny facility-location instance ("bigm"). The left plot is
// computed in the page from the rows 0 <= x <= u, 0 <= y <= 1, x <= M y; the right side reads
// the LP bounds HiGHS found on the reference formulations (units/05-formulations/viz-data.js).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  //   data-key="facility"  data-u="3" (the largest possible load: 3 customers)
  V.register("bigm", (host) => {
    const d = V.data(host, host.dataset.key || "facility");
    if (!d) return;
    const u = Number(host.dataset.u || 3);
    const agg = d.aggregated;
    host.classList.add("viz-bigm");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const W = 500, H = 380;
    const svg = V.newSvg(left, W, H, "the relaxation of x <= M y for the current M, against the integer points");
    const right = html("div", { class: "viz-right" }, host);
    let k = 0;
    V.slider(right, { label: "M", min: 0, max: agg.length - 1, step: 1, value: 0, format: (i) => num(agg[i].M) }, (i) => { k = i; draw(); });
    const W2 = 440, H2 = 190;
    const bars = V.newSvg(right, W2, H2, "LP bounds of the two formulations against the integer optimum");
    const read = html("div", {}, right);

    function draw() {
      const M = agg[k].M;
      // ---- one facility: the load x (sum of its x_ij) against its opening y
      svg.replaceChildren();
      const box = [-0.3, u + 0.7, -0.08, 1.12];
      const P = V.plot(svg, box, W, H, { aspect: "fill", pad: 38, step: [1, 0.25] });
      const rows = (m) => [[-1, 0, 0], [0, -1, 0], [0, 1, 1], [1, 0, u], [1, -m, 0]];
      const tight = V.region(rows(u), box), cur = V.region(rows(M), box);
      el("polygon", { points: V.polyPoints(P, cur.poly), class: "viz-shade-warn" }, svg);
      el("polygon", { points: V.polyPoints(P, tight.poly), class: "viz-poly" }, svg);
      el("polygon", { points: V.polyPoints(P, tight.poly), class: "viz-edge", fill: "none" }, svg);
      const seg = V.lineInBox([1, -M, 0], box);
      if (seg) el("line", { x1: P.X(seg[0][0]), y1: P.Y(seg[0][1]), x2: P.X(seg[1][0]), y2: P.Y(seg[1][1]), class: "viz-cut" }, svg);
      // integer-feasible: (0, 0) and the segment y = 1, 0 <= x <= u
      el("line", { x1: P.X(0), y1: P.Y(1), x2: P.X(u), y2: P.Y(1), class: "viz-optedge" }, svg);
      el("circle", { cx: P.X(0), cy: P.Y(0), r: 6, class: "viz-vertex-opt" }, svg);
      el("circle", { cx: P.X(u), cy: P.Y(u / M), r: 6, class: "viz-dot-warn" }, svg);
      V.text(svg, P.X(u) - 10, P.Y(u / M) + 22, `full load, open only ${num(u / M, 3)}`, "viz-probe-text", "end");
      V.text(svg, P.X(0.1), P.Y(1) - 10, "integer: y = 1, any load", "viz-label-soft", "start");
      V.text(svg, P.X(u + 0.6), P.Y(-0.03), "load x", "viz-label-soft", "end");
      V.text(svg, P.X(-0.25), P.Y(1.08), "open y", "viz-label-soft", "start");
      V.text(svg, P.X(u * 0.62), P.Y(0.62) + 4, "M = 3", "viz-label", "start");
      P.raise();

      // ---- the instance: bounds by formulation
      bars.replaceChildren();
      const top = d.ip * 1.15, B = V.plot(bars, [0, top, 0, 3], W2, H2, { aspect: "fill", pad: 26, grid: false });
      const items = [
        { label: `aggregated, M = ${num(M)}`, value: agg[k].value, cls: "viz-bar-warn" },
        { label: "disaggregated", value: d.disaggregated.value, cls: "viz-bar" },
        { label: "integer optimum", value: d.ip, cls: "viz-bar-ink" },
      ];
      items.forEach((it, i) => {
        const y0 = 2.45 - i * 0.95;   // bar top, in plot units; its label sits just above it
        el("rect", { x: B.X(0), y: B.Y(y0), width: Math.max(1, B.X(it.value) - B.X(0)), height: B.Y(y0 - 0.42) - B.Y(y0), class: it.cls }, bars);
        V.text(bars, B.X(0), B.Y(y0) - 5, it.label, "viz-label-soft", "start");
        V.text(bars, B.X(it.value) + 6, B.Y(y0 - 0.21) + 5, num(it.value, 2), "viz-label", "start");
      });
      read.replaceChildren();
      const gap = (d.ip - agg[k].value) / d.ip;
      V.table(read, ["", "aggregated", "disaggregated"], [
        ["LP bound", num(agg[k].value, 3), num(d.disaggregated.value, 3)],
        ["gap to 13", `${num(100 * gap, 1)}%`, `${num(100 * (d.ip - d.disaggregated.value) / d.ip, 1)}%`],
        ["LP opens y", `(${agg[k].y.map((v) => num(v, 3)).join(", ")})`, `(${d.disaggregated.y.map((v) => num(v, 3)).join(", ")})`],
      ], (i, j) => (j === 0 ? "viz-bas" : ""));
      html("p", { class: "viz-explain" }, read,
        `Every customer still goes to its nearest facility, and the aggregated LP pays only for the opening it is forced to: ` +
        `2/M of facility 0 and 1/M of facility 1, so the bound is 3 + 18/M = ${num(3 + 18 / M, 3)}. The disaggregated rows x_ij ≤ y_i ` +
        `don't depend on M, and their LP already reaches the integer optimum.`);
    }
    draw();
  });
})();
