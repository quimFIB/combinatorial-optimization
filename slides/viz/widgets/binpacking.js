// Bin-packing models (unit 27): the arc-flow graph with a flow split into bins, and symmetry
// counted on the running example. Needs slides/viz/viz.js and viz-data.js (traces/u27.py).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // ---------------------------------------------------------------- arc flow
  //   data-instances="example,seven"   keys into VIZ_DATA.arcflow; each gives an integer and an LP run
  V.register("arcflow", (host) => {
    const all = V.data(host, "arcflow");
    if (!all) return;
    const keys = (host.dataset.instances || Object.keys(all).join(",")).split(",");
    const runs = [];
    for (const k of keys) {
      const inst = all[k];
      if (!inst) return V.fail(host, `unknown instance "${k}"`);
      for (const kind of ["integer", "lp"]) {
        const sol = inst.solutions[kind];
        const states = [{ upto: 0, note: `${kind === "lp" ? "LP relaxation" : "integer optimum"}: flow out of node 0 = ${num(sol.value)} bins`,
          explain: kind === "lp"
            ? `Fractional flow is allowed, so bins can be "half used". The value ${num(sol.value)} rounds up to ${Math.ceil(sol.value - 1e-9)}, which proves no packing uses fewer bins.`
            : "Each unit of flow from node 0 to the last node is one bin: its item arcs are its contents, its loss arcs empty space. Step to take the flow apart bin by bin." }];
        sol.paths.forEach((p, i) => states.push({
          upto: i + 1,
          note: `${num(p.amount)} × a bin holding ${p.items.join(" + ") || "nothing"}${p.waste ? `, ${p.waste} unit${p.waste > 1 ? "s" : ""} empty` : ""}`,
          explain: i === sol.paths.length - 1
            ? `All flow accounted for. Items carried per size: ${Object.entries(sol.carried).map(([s, c]) => `size ${s}: ${num(c)} (need ${inst.needed[s]})`).join(", ")}.`
            : "Follow the highlighted path from node 0: every arc on it is one slot of the bin.",
        }));
        runs.push({ title: `${inst.short || inst.title} · ${kind === "lp" ? "LP relaxation" : "integer"}`, inst, sol, states });
      }
    }
    V.stepper(host, {
      runs, width: 520, height: 400, stepWord: "next bin", label: "arc-flow graph with the flow split into bins",
      render(ctx) {
        const { svg, panel, run, state } = ctx;
        const { inst, sol } = run;
        const C = inst.capacity, x0 = 40, dx = (520 - 2 * x0) / C, yLine = 250;
        const X = (d) => x0 + d * dx;
        const flowOf = new Map(sol.flows.map(([a, b, s, v]) => [`${a}-${b}-${s}`, v]));
        const onPath = new Map();
        sol.paths.slice(0, state.upto).forEach((p, i) => p.arcs.forEach(([a, b, s]) => onPath.set(`${a}-${b}-${s}`, i)));
        const current = state.upto > 0 ? sol.paths[state.upto - 1] : null;
        const curSet = new Set(current ? current.arcs.map(([a, b, s]) => `${a}-${b}-${s}`) : []);
        const sizes = [...new Set(inst.arcs.map((a) => a[2]).filter((s) => s > 0))].sort((a, b) => b - a);
        for (const [a, b, s] of inst.arcs) {
          const key = `${a}-${b}-${s}`, f = flowOf.get(key) || 0;
          let cls = f > 0 ? "viz-af-flow" : "viz-af-arc";
          if (onPath.has(key)) cls = "viz-af-done";
          if (curSet.has(key)) cls = "viz-af-current";
          if (s === 0) {
            el("line", { x1: X(a) + 12, y1: yLine, x2: X(b) - 12, y2: yLine, class: cls }, svg);
            if (f > 0 && (state.upto === 0 || curSet.has(key))) V.text(svg, (X(a) + X(b)) / 2, yLine + 22, num(f), "viz-af-flowlabel");
          } else {
            const rank = sizes.indexOf(s);
            const h = 40 + 150 * (sizes.length - rank) / sizes.length;
            const mx = (X(a) + X(b)) / 2, my = yLine - h;
            el("path", { d: `M${X(a)},${yLine - 12} Q${mx},${my} ${X(b)},${yLine - 12}`, class: cls, fill: "none" }, svg);
            if (f > 0 && (state.upto === 0 || curSet.has(key))) V.text(svg, mx, yLine - h / 2 - 8 + 4, num(f), "viz-af-flowlabel");
          }
        }
        for (let d = 0; d <= C; d++) {
          el("circle", { cx: X(d), cy: yLine, r: 12, class: "viz-g-circle" }, svg);
          V.text(svg, X(d), yLine + 5, String(d), "viz-g-nlabel");
        }
        sizes.forEach((s, i) => V.text(svg, 510, 26 + i * 16, `size-${s} arcs`, "viz-label-soft", "end"));
        V.text(svg, 260, 330, "loss arcs (empty space) run along the line", "viz-label-soft");
        V.text(svg, 260, 380, `flow out of 0: ${num(sol.value)}   ·   ${sol.paths.length} path${sol.paths.length > 1 ? "s" : ""}`, "viz-label");

        html("div", { class: "viz-head" }, panel, "bins read off the flow");
        const rows = sol.paths.map((p, i) => [num(p.amount), p.items.join(" + ") || "—", String(p.waste), i < state.upto ? "✓" : ""]);
        V.table(panel, ["amount", "items", "empty", ""], rows, (i) => (i === state.upto - 1 ? "viz-hl" : i >= state.upto && i >= 0 ? "viz-soft" : ""));
      },
    });
  });

  // ---------------------------------------------------------------- symmetry, counted
  //   one grid cell per labelled optimal assignment, grouped by the packing it labels
  V.register("symmetry", (host) => {
    const d = V.data(host, "symmetry");
    if (!d) return;
    host.classList.add("viz-symmetry");
    V.isolate(host);
    const byPacking = [];
    d.assignments.forEach((a) => { (byPacking[a.packing_id] ||= []).push(a); });
    const cols = Math.max(...byPacking.map((g) => g.length));

    const left = html("div", { class: "viz-left" }, host);
    const toggle = html("label", { class: "viz-row viz-sym-toggle" }, left);
    const cb = html("input", { type: "checkbox" }, toggle);
    html("span", {}, toggle, "apply the rule: item i only in bins 0..i, used bins first");
    const W = 520, H = 30 + byPacking.length * 28;
    const svg = V.newSvg(left, W, H, "every labelled optimal assignment, one row per packing");
    const right = html("div", { class: "viz-right" }, host);
    const count = html("div", { class: "viz-big" }, right);
    const sub = html("div", { class: "viz-readout" }, right);
    html("div", { class: "viz-head" }, right, "the assignment under the pointer");
    const code = html("div", { class: "viz-sym-code" }, right);
    const binsSvg = V.newSvg(right, 360, 150, "the three bins of the chosen assignment");
    const why = html("div", { class: "viz-explain" }, right);
    let chosen = d.assignments[0];

    const itemName = (i) => `${d.sizes[i]}${"abcde"[d.sizes.slice(0, i).filter((s) => s === d.sizes[i]).length]}`;
    function draw() {
      svg.replaceChildren();
      const on = cb.checked;
      V.text(svg, 10, 18, "packing", "viz-label-soft", "start");
      V.text(svg, 110 + cols * 64 / 2, 18, "its labellings (bin of each item, in item order)", "viz-label-soft");
      byPacking.forEach((group, r) => {
        const y = 30 + r * 28;
        V.text(svg, 10, y + 16, `#${r + 1}`, "viz-tick", "start");
        group.forEach((a, c) => {
          const x = 70 + c * 72;
          const dim = on && !a.kept;
          const rect = el("rect", { x, y, width: 66, height: 22, rx: 4,
            class: `viz-sym-cell${dim ? " dim" : ""}${a === chosen ? " chosen" : ""}${on && a.kept ? " kept" : ""}` }, svg);
          rect.dataset.i = d.assignments.indexOf(a);
          const t = V.text(svg, x + 33, y + 16, a.bins.join(""), `viz-sym-text${dim ? " dim" : ""}`);
          t.dataset.i = rect.dataset.i;
        });
      });
      const shown = on ? d.kept : d.assignments.length;
      count.textContent = `${shown} assignment${shown === 1 ? "" : "s"}`;
      sub.textContent = on ? `one per packing: the rule keeps exactly ${d.kept} of ${d.assignments.length}` :
        `${d.packings} packings × 3! labellings: the model sees every one`;

      code.textContent = `bins ${chosen.bins.join("")}   ·   packing #${chosen.packing_id + 1}`;
      binsSvg.replaceChildren();
      for (let b = 0; b < d.nbins; b++) {
        const x = 20 + b * 115;
        el("rect", { x, y: 20, width: 90, height: 5 * 22, class: "viz-sym-bin" }, binsSvg);
        V.text(binsSvg, x + 45, 146, `bin ${b}`, "viz-tick");
        let used = 0;
        d.sizes.forEach((s, i) => {
          if (chosen.bins[i] !== b) return;
          el("rect", { x: x + 4, y: 20 + 5 * 22 - (used + s) * 22 + 2, width: 82, height: s * 22 - 4, rx: 3, class: `viz-sym-item s${s}` }, binsSvg);
          V.text(binsSvg, x + 45, 20 + 5 * 22 - (used + s / 2) * 22 + 5, itemName(i), "viz-sym-itemtext");
          used += s;
        });
      }
      const bad = chosen.bins.map((b, i) => (b > i ? `${itemName(i)} (item ${i}) sits in bin ${b} > ${i}` : null)).filter(Boolean);
      why.textContent = chosen.kept ? "Kept: every item i is in a bin numbered at most i." : `Removed by the rule: ${bad.join("; ")}.`;
    }
    const pickAt = (e) => { const i = e.target.dataset && e.target.dataset.i; if (i !== undefined) { chosen = d.assignments[Number(i)]; draw(); } };
    svg.addEventListener("pointermove", pickAt);
    svg.addEventListener("click", pickAt);
    cb.addEventListener("change", draw);
    draw();
  });
})();
