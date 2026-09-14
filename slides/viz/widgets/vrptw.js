// Capstone figure: a route of the four-customer VRPTW on a map and on a time axis, and each
// way of inserting customer 4. Recorded from the reference schedule, latest_starts and
// insertion_delta (units/capstone-cvrptw/viz-data.js).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, num } = V;

  V.register("vrptw-insert", (host) => {
    const d = V.data(host, "tiny");
    if (!d) return;
    const states = [];
    states.push({ kind: "base", route: d.base.route, times: d.base.starts, back: d.base.back, feasible: true, latest: d.base.latest,
      note: `route 0 → 1 → 2 → 3 → 0: distance ${d.base.cost}, back at ${d.base.back}`,
      explain: `Start times by the recurrence t = max(ready, previous start + service + travel). Latest starts, computed backwards: ${d.base.latest.join(", ")}. Customer 2 starts at 80 but may start as late as 100: that is all the slack anything inserted before it can use.` });
    const between = ["the depot and 1", "1 and 2", "2 and 3", "3 and the depot"];
    for (const o of d.insert) {
      const feasible = o.schedule !== null;
      const late = feasible ? null : o.route.findIndex((c, k) => o.times[k] > d.due[c]);
      const lateBack = feasible || late >= 0 ? null : o.back > d.due[0];
      states.push({ kind: "insert", route: o.route, times: o.times, back: o.back, feasible, late, lateBack, inserted: 4,
        note: feasible ? `insert 4 between ${between[o.pos]}: feasible, extra distance ${o.delta}` : `insert 4 between ${between[o.pos]}: infeasible`,
        explain: feasible
          ? `insertion_delta gives ${o.delta} (= d(prev, 4) + d(4, next) − d(prev, next)); the route's distance becomes ${o.cost}.`
          : `Customer ${o.route[late]} would start at ${o.times[late]}, after its window closes at ${d.due[o.route[late]]}. The constant-time test sees this from one comparison with the latest start, without rescheduling the rest. (Rows after the first late customer just continue the recurrence, unchecked.)` });
    }
    states.push({ kind: "opt", route: d.optimum.route, times: d.optimum.starts, back: d.optimum.back, feasible: true,
      note: `the optimum: 0 → 1 → 2 → 4 → 3 → 0, distance ${d.optimum.cost}`,
      explain: "The cheapest feasible insertion is the optimum here. Customer 3 starts at 190 with only 10 to spare before its window closes at 200." });

    V.stepper(host, {
      runs: [{ title: "the four-customer instance", states }], width: 600, height: 440, stepWord: "next", label: "route map and time windows",
      render(ctx) {
        const { svg, panel, state } = ctx;
        // the map
        const mx = (x) => 150 + x * 4.2, my = (y) => 150 - y * 3.2;
        const path = [0, ...state.route, 0];
        const nodes = d.coords.map(([x, y], i) => ({ id: i, x: mx(x), y: my(y), label: i === 0 ? "D" : i }));
        // bend an arc when it would run straight through another customer (0, 3 and 4 are collinear)
        const through = (a, b) => nodes.some((n) => {
          if (n.id === a.id || n.id === b.id) return false;
          const dx = b.x - a.x, dy = b.y - a.y, t = ((n.x - a.x) * dx + (n.y - a.y) * dy) / (dx * dx + dy * dy);
          return t > 0 && t < 1 && Math.hypot(a.x + t * dx - n.x, a.y + t * dy - n.y) < 18;
        });
        const edges = path.slice(1).map((v, k) => ({ id: `e${k}`, u: path[k], v, directed: true, bend: through(nodes[path[k]], nodes[v]) ? 34 : 0 }));
        const G = V.graph(svg, { nodes, edges }, { radius: 13 });
        edges.forEach((e) => G.edgeClass(e.id, state.feasible ? "chosen" : "warn"));
        if (state.inserted) G.nodeClass(state.inserted, state.feasible ? "good" : "warn");
        if (!state.route.includes(4)) G.nodeClass(4, "muted");
        V.text(svg, 590, 20, "map (distances in tenths)", "viz-tick", "end");

        // the time axis
        const t0 = 200, tx = (t) => 120 + t * 1.17, rowH = 42;
        for (let t = 0; t <= 400; t += 50) {
          el("line", { x1: tx(t), y1: t0 - 8, x2: tx(t), y2: t0 + rowH * 5 - 10, class: "viz-grid" }, svg);
          V.text(svg, tx(t), t0 + rowH * 5 + 6, String(t), "viz-tick", "middle");
        }
        V.text(svg, tx(400), t0 - 14, "time", "viz-tick", "end");
        state.route.forEach((c, k) => {
          const y = t0 + k * rowH, start = state.times[k], late = start > d.due[c];
          V.text(svg, 108, y + 14, `customer ${c}`, "viz-label", "end");
          el("rect", { x: tx(d.ready[c]), y, width: tx(d.due[c]) - tx(d.ready[c]), height: 20, rx: 3, class: "viz-shade-good" }, svg);
          el("rect", { x: tx(start), y: y + 3, width: tx(start + d.service[c]) - tx(start), height: 14, rx: 2,
                       style: `fill: ${late ? "var(--warn)" : "var(--accent)"}` }, svg);
          V.text(svg, tx(start + d.service[c]) + 6, y + 15, late ? `starts ${start} > ${d.due[c]}` : `starts ${start}`, late ? "viz-g-note" : "viz-tick", "start")
            .setAttribute("style", late ? "fill: var(--warn)" : "");
          if (state.latest && state.latest[k] !== undefined)
            el("line", { x1: tx(state.latest[k]), y1: y - 3, x2: tx(state.latest[k]), y2: y + 23, class: "viz-cut" }, svg);
        });
        const yb = t0 + state.route.length * rowH;
        V.text(svg, 108, yb + 14, "depot", "viz-label", "end");
        el("rect", { x: tx(0), y: yb, width: tx(d.due[0]) - tx(0), height: 20, rx: 3, class: "viz-shade-good" }, svg);
        el("circle", { cx: tx(state.back), cy: yb + 10, r: 6, style: "fill: var(--accent)" }, svg);
        V.text(svg, tx(state.back) + 10, yb + 15, `back at ${state.back}`, "viz-tick", "start");

        const rows = state.route.map((c, k) => [c, `[${d.ready[c]}, ${d.due[c]}]`, state.times[k], state.latest ? state.latest[k] : "",
                                               state.times[k] > d.due[c] ? "late" : "ok"]);
        V.table(panel, ["customer", "window", "start", state.latest ? "latest start" : "", ""], rows,
          (i, j, v) => (j === 4 && v === "late" ? "viz-bad" : j === 4 ? "viz-goodcell" : ""));
        if (state.latest) V.html("div", { class: "viz-hint" }, panel, "Dashed ticks on the time axis: each customer's latest start.");
      },
    });
  });
})();
