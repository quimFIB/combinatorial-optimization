// Constraint-programming figures: AC-3 and the trail (unit 17), Régin's filter and the
// cumulative profile (unit 18), Luby cutoffs and LNS (unit 19). Needs slides/viz/viz.js and
// cp.css. All data comes from window.VIZ_DATA, recorded by slides/viz/traces/u17-u19.py.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // A row of value cells under a point: present, removed earlier, or removed in this step.
  function valueCells(svg, cx, y, all, now, justRemoved) {
    const w = 26, x0 = cx - (all.length * w) / 2;
    all.forEach((v, i) => {
      const present = now.includes(v), fresh = justRemoved.includes(v);
      const cls = fresh ? "cp-cell cp-cell-fresh" : present ? "cp-cell" : "cp-cell cp-cell-gone";
      el("rect", { x: x0 + i * w, y, width: w - 3, height: 24, rx: 3, class: cls }, svg);
      V.text(svg, x0 + i * w + (w - 3) / 2, y + 17, v, present ? "cp-cell-text" : "cp-cell-text cp-cell-text-gone");
      if (!present || fresh) el("line", { x1: x0 + i * w + 3, y1: y + 21, x2: x0 + i * w + w - 6, y2: y + 3, class: "cp-strike" }, svg);
    });
  }
  const chars = (s) => (s === "∅" ? [] : s.split(""));

  // ---------------------------------------------------------------- unit 17: AC-3
  //   data-runs="ac3-chain,ac3-triangle,ac3-cycle"
  V.register("ac3", (host) => {
    const runs = (host.dataset.runs || "").split(",").map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    const pos = { x: [260, 110], y: [110, 260], z: [410, 260] };
    V.stepper(host, {
      runs, width: 520, height: 350, stepWord: "revise", label: "AC-3 on three variables",
      render({ svg, panel, run, k, state }) {
        const init = run.states[0].dom;
        const pairs = new Map();
        for (const [a, b, rel] of run.arcs) {
          const key = [a, b].sort().join("");
          if (!pairs.has(key)) pairs.set(key, { u: a, v: b, label: rel === ">" ? "<" : rel, rel, a, b });
        }
        const nodes = run.variables.map((v) => ({ id: v, x: pos[v][0], y: pos[v][1] }));
        const edges = [...pairs.values()].map((p) => {
          // label reads left to right as the constraint between u and v
          const lab = p.rel === ">" ? `${p.b} < ${p.a}` : `${p.a} ${p.rel} ${p.b}`;
          return { id: p.u + p.v, u: p.u, v: p.v, label: lab, labelOffset: 22 };
        });
        if (state.arc) edges.push({ id: "active", u: state.arc[1], v: state.arc[0], directed: true, bend: 34 });
        const G = V.graph(svg, { nodes, edges }, { radius: 20 });
        if (state.arc) {
          G.edgeClass("active", state.wipeout ? "warn" : state.removed.length ? "chosen" : "hot");
          G.nodeClass(state.arc[0], state.wipeout ? "warn" : "hot");
        }
        for (const v of run.variables) {
          const justRemoved = state.arc && state.arc[0] === v ? state.removed.map(String) : [];
          const now = chars(state.dom[v]);
          valueCells(svg, pos[v][0], v === "x" ? pos[v][1] - 52 : pos[v][1] + 28, chars(init[v]), now, state.wipeout && state.arc[0] === v ? chars(run.states[k - 1].dom[v]) : justRemoved);
        }
        V.text(svg, 12, 336, state.arc ? `arrow: ${state.arc[0]} checks its values against ${state.arc[1]}` : "", "viz-label-soft", "start");

        html("div", { class: "viz-head" }, panel, `queue (${state.queue.length} arcs)`);
        const q = html("div", { class: "cp-chips" }, panel);
        if (!state.queue.length) html("span", { class: "cp-chip cp-chip-empty" }, q, "empty");
        state.queue.forEach(([a, b]) => {
          const pushed = state.pushed.some(([c, d]) => c === a && d === b);
          html("span", { class: pushed ? "cp-chip cp-chip-new" : "cp-chip" }, q, `(${a},${b})`);
        });
        html("div", { class: "viz-head" }, panel, "domains");
        V.table(panel, ["", ...run.variables], [["now", ...run.variables.map((v) => state.dom[v])]], (i, j) => (j === 0 ? "viz-bas" : ""));
        html("div", { class: "viz-readout" }, panel, `revise calls so far: ${state.calls}`);
      },
    });
  });

  // ---------------------------------------------------------------- unit 17: the trail
  //   data-run="trail"
  V.register("trail", (host) => {
    const run = V.data(host, host.dataset.run || "trail");
    if (!run) return;
    V.stepper(host, {
      runs: [run], width: 520, height: 300, label: "a store's domains and its trail",
      render({ svg, panel, run, k, state }) {
        const prev = k ? run.states[k - 1] : state;
        const values = run.values.map(String);
        run.variables.forEach((v, i) => {
          const y = 40 + i * 80;
          V.text(svg, 60, y + 18, v, "cp-var", "middle");
          const now = chars(state.dom[i]), before = chars(prev.dom[i]);
          const fresh = before.filter((a) => !now.includes(a));
          const back = now.filter((a) => !before.includes(a));
          valueCells(svg, 200, y, values, now, fresh);
          if (back.length) V.text(svg, 310, y + 17, `restored ${back.join(", ")}`, "cp-restored", "start");
          else if (fresh.length) V.text(svg, 310, y + 17, `removed ${fresh.join(", ")}`, "cp-removed", "start");
        });
        const marks = Object.entries(state.marks);
        V.text(svg, 20, 285, marks.length ? `marks: ${marks.map(([m, n]) => `${m} = ${n}`).join(", ")}` : "no marks yet", "viz-label-soft", "start");

        html("div", { class: "viz-head" }, panel, `trail (${state.trail.length} entries)`);
        const grew = state.trail.length > prev.trail.length;
        const rows = state.trail.map(([v, old], i) => [String(i), v, old]);
        if (!rows.length) html("div", { class: "viz-readout cp-soft" }, panel, "empty");
        else V.table(panel, ["#", "variable", "old domain"], rows, (i, j) => {
          const cls = [];
          if (i >= 0 && grew && i >= prev.trail.length) cls.push("viz-hl");
          if (i >= 0 && marks.some(([, n]) => n === i)) cls.push("cp-markrow");
          if (j === 0) cls.push("viz-soft");
          return cls.join(" ");
        });
        if (state.trail.length < prev.trail.length)
          html("div", { class: "viz-readout" }, panel, `popped ${prev.trail.length - state.trail.length} entries, newest first: ${prev.trail.slice(state.trail.length).reverse().map(([v, o]) => `(${v}, ${o})`).join(", ")}`);
      },
    });
  });

  // ---------------------------------------------------------------- unit 18: Régin
  //   data-runs="regin-deck,regin-free"
  V.register("regin", (host) => {
    const runs = (host.dataset.runs || "").split(",").map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    V.stepper(host, {
      runs, width: 520, height: 400, label: "Régin's alldifferent filter on the value graph",
      render({ svg, panel, run, state }) {
        svg.classList.add("cp-thin");
        const n = run.n, values = state.values;
        const nodes = [
          ...Array.from({ length: n }, (_, i) => ({ id: `x${i + 1}`, x: 120, y: 40 + (i + 0.5) * (330 / n) })),
          ...values.map((v, i) => ({ id: `v${v}`, label: v, x: 400, y: 40 + (i + 0.5) * (330 / values.length) })),
        ];
        const matched = new Set((state.matching || []).map(([i, v]) => `x${i}-v${v}`));
        const removed = new Set((state.removed || []).map((r) => `x${r.x}-v${r.value}`));
        const sccOf = {};
        (state.sccs || []).forEach((g, gi) => g.forEach((nd) => { sccOf[nd] = gi; }));
        const reach = new Set(state.reach || []);
        let edges;
        if (state.arcs) {
          edges = state.arcs.map(([a, b]) => ({ id: a.startsWith("x") ? `${a}-${b}` : `${b}-${a}`, u: a, v: b, directed: true }));
        } else {
          edges = state.edges.map(([i, v]) => ({ id: `x${i}-v${v}`, u: `x${i}`, v: `v${v}` }));
        }
        const G = V.graph(svg, { nodes, edges }, { radius: 18 });
        for (const e of edges) {
          const id = e.id, [xs, vs] = id.split("-");
          let cls = "";
          if (matched.has(id)) cls = "chosen";
          if (state.stage === "scc" || state.stage === "filter") {
            const inside = sccOf[xs] !== undefined && sccOf[xs] === sccOf[vs];
            const toFree = reach.has(vs);
            if (!matched.has(id) && !inside && !toFree) cls = state.stage === "filter" ? "warn" : "muted";
            else if (!matched.has(id)) cls = "good";
          }
          G.edgeClass(id, cls);
        }
        (state.sccs || []).forEach((g) => g.forEach((nd) => G.nodeClass(nd, "good")));
        if (state.stage === "scc" || state.stage === "filter") for (const nd of reach) if (sccOf[nd] === undefined) G.nodeClass(nd, "hot");
        V.text(svg, 120, 24, "variables", "viz-label-soft");
        V.text(svg, 400, 24, "values", "viz-label-soft");
        const legend = { graph: "", matching: "thick: matched", orient: "matched: value → variable; others: variable → value",
                         scc: "green: inside a strongly connected component; grey: candidates for removal",
                         filter: "red: removed" }[state.stage];
        V.text(svg, 12, 392, legend, "viz-label-soft", "start");

        const rows = state.domains.map((d, i) => [`x${i + 1}`, `{${d.join(",")}}`, state.result ? `{${state.result[i].join(",")}}` : "…"]);
        V.table(panel, ["variable", "domain", "after the filter"], rows, (i, j, v) =>
          j === 0 ? "viz-bas" : (j === 2 && i >= 0 && state.result && state.result[i].length < state.domains[i].length ? "viz-goodcell" : ""));
        if (state.removed && state.removed.length) {
          html("div", { class: "viz-head" }, panel, "each removal, and the Hall set behind it");
          V.table(panel, ["removed", "Hall set", "its values"], state.removed.map((r) =>
            [`x${r.x} = ${r.value}`, r.hall ? `{${r.hall.map((j) => "x" + j).join(", ")}}` : "—", r.hall_values ? `{${r.hall_values.join(",")}}` : "—"]));
        }
      },
    });
  });

  // ---------------------------------------------------------------- unit 18: cumulative
  //   data-key="cumulative"
  V.register("cumulative", (host) => {
    const D = V.data(host, host.dataset.key || "cumulative");
    if (!D) return;
    host.classList.add("viz-side");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const right = html("div", { class: "viz-right" }, host);
    const W = 520, H = 400, T = 9;
    const svg = V.newSvg(left, W, H, "three tasks, their start windows, compulsory parts and the resource profile");
    const win = D.start.map((s) => s.split("-").map(Number));
    html("div", { class: "viz-head" }, right, "start windows (earliest, latest)");
    const sliders = [];
    D.names.forEach((name, i) => {
      const [a, b] = D.horizon[i];
      const lo = V.slider(right, { label: `${name} earliest`, min: a, max: b, step: 1, value: win[i][0] }, (v) => {
        win[i][0] = v; if (win[i][1] < v) { win[i][1] = v; sliders[i].hi.input.value = v; } draw();
      });
      const hi = V.slider(right, { label: `${name} latest`, min: a, max: b, step: 1, value: win[i][1] }, (v) => {
        win[i][1] = v; if (win[i][0] > v) { win[i][0] = v; sliders[i].lo.input.value = v; } draw();
      });
      sliders.push({ lo, hi });
    });
    const out = html("div", {}, right);
    const X = (t) => 70 + t * 48;

    function draw() {
      svg.replaceChildren();
      for (const s of sliders) { s.lo.input.nextSibling.textContent = s.lo.input.value; s.hi.input.nextSibling.textContent = s.hi.input.value; }
      const key = win.map(([lo, hi]) => `${lo}-${hi}`).join(",");
      const R = D.table[key];
      for (let t = 0; t <= T; t++) {
        el("line", { x1: X(t), y1: 30, x2: X(t), y2: 370, class: "viz-grid" }, svg);
        V.text(svg, X(t), 390, t, "viz-tick");
      }
      D.names.forEach((name, i) => {
        const y = 40 + i * 70, d = D.durations[i], [lo, hi] = win[i];
        V.text(svg, 40, y + 22, name, "cp-var");
        el("rect", { x: X(lo), y: y + 4, width: X(hi + d) - X(lo), height: 28, rx: 4, class: "cp-window" }, svg);
        const part = R.parts[i];
        if (part.length) el("rect", { x: X(part[0]), y: y + 4, width: X(part[part.length - 1] + 1) - X(part[0]), height: 28, rx: 4, class: "cp-part" }, svg);
        for (let t = lo; t <= hi; t++) {
          const kept = !R.fail && R.keep[i].includes(t);
          el("circle", { cx: X(t), cy: y + 44, r: 5, class: kept ? "viz-dot-good" : "viz-dot-warn" }, svg);
        }
      });
      // profile of compulsory parts
      const base = 360, unit = 36;
      V.text(svg, 40, base - 40, "profile", "viz-label-soft", "middle");
      const prof = Array(T + 1).fill(0);
      R.parts.forEach((p, i) => p.forEach((t) => { prof[t] += D.demands[i]; }));
      prof.forEach((h, t) => {
        if (!h) return;
        el("rect", { x: X(t) + 2, y: base - h * unit, width: 44, height: h * unit, class: h > D.capacity ? "cp-over" : "cp-bar" }, svg);
      });
      el("line", { x1: X(0), y1: base - D.capacity * unit, x2: X(T), y2: base - D.capacity * unit, class: "viz-cut" }, svg);
      V.text(svg, X(T), base - D.capacity * unit - 6, `capacity ${D.capacity}`, "viz-label-soft", "end");
      el("line", { x1: X(0), y1: base, x2: X(T), y2: base, class: "viz-axis" }, svg);

      out.replaceChildren();
      if (R.fail) {
        html("div", { class: "viz-note cp-bad" }, out, "fail: the compulsory parts alone overload the resource, or a task loses every start");
      } else {
        V.table(out, ["task", "starts", "compulsory", "after filtering"], D.names.map((name, i) => {
          const [lo, hi] = win[i], p = R.parts[i];
          return [name, `${lo}–${hi}`, p.length ? `[${p[0]}, ${p[p.length - 1] + 1})` : "none", `{${R.keep[i].join(",")}}`];
        }), (i, j) => (j === 3 && i >= 0 && R.keep[i].length < win[i][1] - win[i][0] + 1 ? "viz-goodcell" : j === 0 ? "viz-bas" : ""));
      }
    }
    draw();
  });

  // ---------------------------------------------------------------- unit 19: Luby
  //   data-key="luby"
  V.register("luby", (host) => {
    const L = V.data(host, host.dataset.key || "luby");
    if (!L) return;
    host.classList.add("viz-stack");
    V.isolate(host);
    const W = 1120, H = 300;
    const svg = V.newSvg(host, W, H, "Luby restart cutoffs as bars");
    const controls = html("div", { class: "cp-controls" }, host);
    let n = 15, base = 30;
    V.slider(controls, { label: "runs", min: 1, max: 63, step: 1, value: n }, (v) => { n = v; draw(); });
    V.slider(controls, { label: "base cutoff", min: 10, max: 100, step: 10, value: base }, (v) => { base = v; draw(); });
    const out = html("div", { class: "cp-luby-out" }, host);

    function draw() {
      svg.replaceChildren();
      const terms = L.slice(0, n), maxT = Math.max(...terms);
      const bw = Math.min(72, (W - 80) / n), top = 30, bottom = 250, scale = (bottom - top) / maxT;
      const wide = bw > 30, pow = (m) => ((m + 1) & m) === 0;   // m = 2^k - 1
      terms.forEach((t, i) => {
        const x = 50 + i * bw, h = t * scale;
        el("rect", { x, y: bottom - h, width: bw - 3, height: h, class: t === maxT ? "cp-bar-top" : "cp-bar" }, svg);
        // narrow bars: label only each cutoff's first appearance and the runs 2^k - 1, where it ends
        if (wide || L.indexOf(t) === i) V.text(svg, x + (bw - 3) / 2, bottom - h - 5, t * base, "viz-tick");
        if (wide || pow(i + 1)) V.text(svg, x + (bw - 3) / 2, bottom + 16, i + 1, "viz-tick");
      });
      el("line", { x1: 46, y1: bottom, x2: 50 + n * bw, y2: bottom, class: "viz-axis" }, svg);
      V.text(svg, 50, 290, `run number; bar height = cutoff in nodes (luby(i) × ${base})`, "viz-label-soft", "start");
      const bySize = new Map();
      terms.forEach((t) => bySize.set(t, (bySize.get(t) || 0) + 1));
      const total = terms.reduce((a, b) => a + b, 0) * base;
      out.replaceChildren();
      V.table(out, ["cutoff", ...[...bySize.keys()].sort((a, b) => a - b).map((t) => t * base)],
        [["runs", ...[...bySize.keys()].sort((a, b) => a - b).map((t) => bySize.get(t))],
         ["total effort", ...[...bySize.keys()].sort((a, b) => a - b).map((t) => bySize.get(t) * t * base)]],
        (i, j) => (j === 0 ? "viz-bas" : ""));
      html("div", { class: "viz-readout" }, out, `${n} runs, ${total} nodes in all, largest cutoff ${maxT * base}.`);
    }
    draw();
  });

  // ---------------------------------------------------------------- unit 19: LNS
  //   data-runs="lns-deck,lns-6x4"
  V.register("lns", (host) => {
    const runs = (host.dataset.runs || "").split(",").map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    V.stepper(host, {
      runs, width: 560, height: 380, label: "LNS on a job-shop, one destroy-and-repair step at a time", stepWord: "iterate",
      render({ svg, panel, run, k, state }) {
        const M = run.machines, span = Math.max(...run.states.map((s) => s.makespan)) + 1;
        const X = (t) => 50 + t * (490 / span), rowH = Math.min(52, 250 / M);
        for (let m = 0; m < M; m++) {
          const y = 20 + m * rowH;
          V.text(svg, 22, y + rowH / 2 + 4, `M${m}`, "viz-tick");
          el("line", { x1: X(0), y1: y + rowH - 2, x2: X(span), y2: y + rowH - 2, class: "viz-grid" }, svg);
        }
        const freed = new Set(state.freed);
        for (const [j, kk, m, s, d] of state.ops) {
          const y = 20 + m * rowH + 4;
          const cls = `cp-op cp-job${j % 6}${freed.has(j) ? " cp-op-freed" : state.freed.length ? " cp-op-kept" : ""}`;
          el("rect", { x: X(s), y, width: X(s + d) - X(s) - 1, height: rowH - 10, rx: 3, class: cls }, svg);
          if (X(s + d) - X(s) > 22) V.text(svg, (X(s) + X(s + d)) / 2, y + rowH / 2, `J${j}`, "cp-op-text");
        }
        el("line", { x1: X(state.makespan), y1: 14, x2: X(state.makespan), y2: 20 + M * rowH, class: "viz-cut" }, svg);
        V.text(svg, X(state.makespan) + 4, 14, `makespan ${state.makespan}`, "viz-label-soft", "start");
        for (let t = 0; t <= span; t += span > 30 ? 10 : 5) V.text(svg, X(t), 32 + M * rowH, t, "viz-tick");
        // makespan so far
        const tr = state.trace, top = 290, bottom = 355;
        const all = run.states.map((s) => s.makespan), mx = Math.max(...all), mn = Math.min(...all);
        const px = (i) => 50 + i * (490 / Math.max(1, run.states.length - 1));
        const py = (v) => bottom - (mx === mn ? 0 : (v - mn) / (mx - mn)) * (bottom - top);
        el("polyline", { points: tr.map((v, i) => `${px(i)},${py(v)}`).join(" "), class: "viz-curve" }, svg);
        tr.forEach((v, i) => el("circle", { cx: px(i), cy: py(v), r: i === tr.length - 1 ? 5 : 3, class: "viz-vertex-opt" }, svg));
        V.text(svg, 50, 378, `incumbent makespan per iteration: ${tr.length > 4 ? `${tr[0]} → … → ${tr[tr.length - 1]}` : tr.join(" → ")}`, "viz-label-soft", "start");

        html("div", { class: "viz-big" }, panel, `makespan ${state.makespan}`);
        html("div", { class: "viz-readout" }, panel, state.freed.length ? `freed: ${state.freed.map((j) => "J" + j).join(", ")} (bright); kept jobs keep their order on every machine (faded)` : "no job freed yet");
        V.table(panel, ["job", "operations (machine, duration)"], run.jobs.map((job, j) => [`J${j}`, job.map(([m, d]) => `M${m} ${d}`).join(", ")]),
          (i, j2) => (i >= 0 && freed.has(i) ? "viz-hl" : j2 === 0 ? "viz-bas" : ""));
      },
    });
  });
})();
