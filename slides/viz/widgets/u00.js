// Unit 00: the brute-force oracle replayed, and a cover-and-matching certificate you build.
(function () {
  "use strict";
  const V = window.CoViz;
  const { html } = V;

  // The running example's drawing, shared by both figures (svg units).
  const POS = { 0: [90, 70], 1: [90, 250], 2: [240, 160], 3: [390, 160] };

  // ---------------------------------------------------------------- oracle stepper
  //   data-run="oracle"   recorded by slides/viz/traces/u00.py
  V.register("oracle", (host) => {
    const run = V.data(host, host.dataset.run || "oracle");
    if (!run) return;
    V.stepper(host, {
      runs: [run], width: 480, height: 330, stepWord: "next candidate", label: "brute force over the 16 candidates",
      render({ svg, panel, state, k, run }) {
        const g = V.graph(svg, {
          nodes: Object.entries(POS).map(([id, [x, y]]) => ({ id, x, y })),
          edges: run.edges.map(([u, v]) => ({ id: `${u}${v}`, u: String(u), v: String(v) })),
        }, { radius: 20 });
        state.x.forEach((b, i) => g.nodeClass(String(i), b ? "chosen" : ""));
        run.edges.forEach(([u, v]) => {
          const bad = state.uncovered.some(([a, b]) => a === u && b === v);
          g.edgeClass(`${u}${v}`, bad ? "warn" : "good");
        });
        V.text(svg, 240, 312, `x = (${state.x.join(", ")})`, "viz-probe-text");

        const row = html("div", { class: "viz-readout" }, panel);
        row.textContent = state.feasible ? `feasible: every edge has a chosen end; size ${state.x.reduce((a, b) => a + b, 0)}` :
          `infeasible: uncovered ${state.uncovered.map(([a, b]) => `${a}${b}`).join(", ")}`;
        V.table(panel, ["counter", "value"], [
          ["examined", `${state.examined} of 16`],
          ["feasible so far", String(state.count_feasible)],
          ["best so far", state.best === null ? "none yet" : `${state.best} at (${state.best_x.join(", ")})`],
        ], (i, j) => (j === 0 ? "viz-bas" : i === 2 && state.improved ? "viz-goodcell" : ""));
        const strip = html("div", { class: "viz-strip" }, panel);
        run.states.forEach((s, i) => {
          const cell = html("span", { class: "viz-strip-cell" + (i === k ? " now" : "") + (i > k ? " later" : s.feasible ? " ok" : " bad") }, strip);
          cell.title = `(${s.x.join(",")})`;
        });
        html("div", { class: "viz-hint" }, panel, "Strip: one square per candidate, in the order the oracle tries them. Filled: a cover.");
      },
    });
  });

  // ---------------------------------------------------------------- certificate builder
  //   data-graphs='{"name": {"nodes": [[id, x, y], ...], "edges": [[u, v], ...]}, ...}'
  // Click vertices to put them in C, edges to put them in M. The verdict is computed live.
  V.register("certificate", (host) => {
    const graphs = JSON.parse(host.dataset.graphs);
    const names = Object.keys(graphs);
    host.classList.add("viz-side");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const svg = V.newSvg(left, 480, 330, "click vertices for a cover and edges for a matching");
    const controls = html("div", { class: "viz-controls" }, left);
    const pick = html("select", { class: "viz-pick", "aria-label": "choose a graph" }, controls);
    names.forEach((n) => html("option", { value: n }, pick, n));
    const clear = html("button", { type: "button" }, controls, "clear");
    const right = html("div", { class: "viz-right" }, host);
    const out = html("div", {}, right);
    html("div", { class: "viz-hint" }, right, "Click a vertex to add it to the cover C, an edge to add it to the matching M. Click again to remove.");

    let G, C, M;
    const load = (name) => { G = graphs[name]; C = new Set(); M = new Set(); draw(); };
    function draw() {
      svg.replaceChildren();
      const key = ([u, v]) => `${u}-${v}`;
      const g = V.graph(svg, {
        nodes: G.nodes.map(([id, x, y]) => ({ id: String(id), x, y })),
        edges: G.edges.map(([u, v]) => ({ id: key([u, v]), u: String(u), v: String(v) })),
      }, { radius: 20 });
      // wide invisible hit areas make edges easy to click
      for (const [u, v] of G.edges) {
        const h = g.edge(key([u, v]));
        const hit = h.path.cloneNode();
        hit.setAttribute("class", "viz-hit");
        hit.addEventListener("click", () => { M.has(key([u, v])) ? M.delete(key([u, v])) : M.add(key([u, v])); draw(); });
        h.g.appendChild(hit);
      }
      for (const [id] of G.nodes) {
        const h = g.node(String(id));
        h.g.style.cursor = "pointer";
        h.g.addEventListener("click", () => { C.has(id) ? C.delete(id) : C.add(id); draw(); });
      }
      const uncovered = G.edges.filter(([u, v]) => !C.has(u) && !C.has(v));
      const ends = [...M].flatMap((k) => k.split("-").map(Number));
      const clash = ends.filter((v, i) => ends.indexOf(v) !== i);
      for (const [id] of G.nodes) g.nodeClass(String(id), C.has(id) ? "chosen" : clash.includes(id) ? "warn" : "");
      for (const e of G.edges) {
        const k = key(e);
        const bad = M.has(k) && (clash.includes(e[0]) || clash.includes(e[1]));
        g.edgeClass(k, M.has(k) ? (bad ? "warn" : "good") : C.size && uncovered.some((f) => key(f) === k) ? "hot" : "");
      }

      out.replaceChildren();
      const coverOk = uncovered.length === 0, matchOk = clash.length === 0;
      V.table(out, ["check", "result"], [
        ["C covers every edge", !C.size ? "C is empty" : coverOk ? `yes, |C| = ${C.size}` : `no: ${uncovered.map(([u, v]) => `${u}${v}`).join(", ")} uncovered (dashed)`],
        ["M shares no endpoint", !M.size ? "M is empty" : matchOk ? `yes, |M| = ${M.size}` : `no: vertex ${[...new Set(clash)].join(", ")} used twice`],
      ], (i, j, v) => (i < 0 ? "" : j === 0 ? "viz-bas" : String(v).startsWith("yes") ? "viz-goodcell" : String(v).startsWith("no") ? "viz-bad" : "viz-soft"));
      const verdict = html("div", { class: "viz-readout" }, out);
      if (coverOk && matchOk && C.size === M.size && C.size > 0) {
        verdict.className = "viz-readout viz-cert";
        verdict.textContent = `|C| = |M| = ${C.size}: each proves the other optimal. The smallest cover has ${C.size} vertices.`;
      } else if (coverOk && matchOk && M.size > 0) {
        verdict.textContent = `So the smallest cover has between ${M.size} and ${C.size} vertices.`;
      } else if (matchOk && M.size > 0) {
        verdict.textContent = `Any cover needs at least ${M.size} vertices.`;
      } else if (coverOk && C.size > 0 && !(M.size && !matchOk)) {
        verdict.textContent = `The smallest cover has at most ${C.size} vertices.`;
      } else {
        verdict.textContent = "";
      }
    }
    pick.addEventListener("change", () => load(pick.value));
    clear.addEventListener("click", () => load(pick.value));
    load(names[0]);
  });
})();
