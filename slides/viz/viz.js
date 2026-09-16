// Interactive figures: the shared core. Classic script, no build step, no libraries,
// because decks open from file://, where ES modules and fetch() of sibling files are blocked.
//
// A unit's explore.html loads this file, then its widget files from slides/viz/widgets/,
// then (if it has recorded traces) its own viz-data.js, which sets window.VIZ_DATA.
// A figure is a <div class="viz" data-viz="NAME" data-...>; widgets register a builder:
//
//   CoViz.register("NAME", (host, V) => { ... });      // V is this CoViz object
//
// Rules every widget follows:
//   * geometry and numbers are computed from data in the page, or come from traces recorded
//     from the unit's reference solution (slides/viz/traces/), never typed in by hand;
//   * pointer and key events inside a figure never reach reveal.js (V.isolate);
//   * a failure shows as a visible .viz-error box, which slides/tools/viz-check.mjs looks for.
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const EPS = 1e-9;
  const registry = {};

  // ------------------------------------------------------------ DOM helpers
  const el = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  };
  const html = (tag, attrs = {}, parent, text) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) e.setAttribute(k, v);
    if (text !== undefined && text !== null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  };
  const text = (parent, x, y, s, cls = "viz-label", anchor = "middle") => {
    const t = el("text", { x, y, class: cls, "text-anchor": anchor }, parent);
    t.textContent = s;
    return t;
  };
  // Short, readable numbers: integers as integers, else up to `digits` decimals; strings pass
  // through (recorded exact values like "5/2"), with a real minus sign.
  const num = (v, digits = 2) => {
    if (typeof v === "string") return v.replace(/^-/, "−");
    if (!Number.isFinite(v)) return v > 0 ? "∞" : v < 0 ? "−∞" : "—";
    const f = 10 ** digits, r = Math.round(v * f) / f;
    if (r === 0) return "0";
    const s = Number.isInteger(r) ? String(r) : r.toFixed(digits).replace(/0+$/, "");
    return s.replace(/^-/, "−");
  };
  // Keep reveal.js from turning drags into swipes and keys into slide changes.
  const isolate = (node) => {
    node.setAttribute("data-prevent-swipe", "");
    for (const t of ["pointerdown", "pointermove", "wheel", "touchstart", "touchmove", "keydown"])
      node.addEventListener(t, (e) => e.stopPropagation());
  };
  const svgPoint = (svg, evt) => {
    const pt = svg.createSVGPoint();
    pt.x = evt.clientX; pt.y = evt.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  };
  let ids = 0;
  const newSvg = (parent, w, h, label) => {
    const svg = el("svg", { viewBox: `0 0 ${w} ${h}`, class: "viz-svg", role: "img", "aria-label": label || "interactive figure" }, parent);
    svg.dataset.vizId = String(++ids);
    return svg;
  };
  // Drags owned by the svg (not the handle), so redrawing the handle mid-drag is safe.
  // isHandle(target) decides whether a pointerdown starts a drag; onDrag(svgX, svgY, event) on moves.
  const draggable = (svg, isHandle, onDrag, onEnd) => {
    let dragging = false;
    svg.addEventListener("pointerdown", (e) => {
      if (!isHandle(e.target)) return;
      dragging = true;
      svg.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    svg.addEventListener("pointermove", (e) => { if (dragging) { const q = svgPoint(svg, e); onDrag(q.x, q.y, e); } });
    const stop = () => { if (dragging) { dragging = false; if (onEnd) onEnd(); } };
    svg.addEventListener("pointerup", stop);
    svg.addEventListener("pointercancel", stop);
    return { get dragging() { return dragging; } };
  };
  // A labelled range slider. onInput(value) fires on every change.
  const slider = (parent, { label, min, max, step, value, format }, onInput) => {
    const wrap = html("label", { class: "viz-slider" }, parent);
    html("span", { class: "viz-slider-label" }, wrap, label);
    const input = html("input", { type: "range", min, max, step, value }, wrap);
    const out = html("span", { class: "viz-slider-value" }, wrap);
    const fmt = format || ((v) => num(v));
    const update = () => { out.textContent = fmt(Number(input.value)); onInput(Number(input.value)); };
    input.addEventListener("input", update);
    out.textContent = fmt(Number(value));
    return { input, set: (v) => { input.value = v; update(); } };
  };
  const fail = (host, msg) => {
    host.replaceChildren();
    html("div", { class: "viz-error" }, host, `figure unavailable: ${msg}`);
    return null;
  };

  // ------------------------------------------------------------ 2-D geometry
  // Rows are [a, b, c] meaning a·x + b·y <= c.
  const clip = (poly, [a, b, c]) => {
    const out = [];
    for (let i = 0; i < poly.length; i++) {
      const p = poly[i], q = poly[(i + 1) % poly.length];
      const fp = a * p[0] + b * p[1] - c, fq = a * q[0] + b * q[1] - c;
      if (fp <= EPS) out.push(p);
      if ((fp < -EPS && fq > EPS) || (fp > EPS && fq < -EPS)) {
        const t = fp / (fp - fq);
        out.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]);
      }
    }
    return out;
  };
  const feasible = (rows, p, tol = 1e-7) => rows.every(([a, b, c]) => a * p[0] + b * p[1] <= c + tol);
  const solve2 = ([a1, b1, c1], [a2, b2, c2]) => {
    const d = a1 * b2 - a2 * b1;
    if (Math.abs(d) < EPS) return null;
    return [(c1 * b2 - c2 * b1) / d, (a1 * c2 - a2 * c1) / d];
  };
  const tightRows = (rows, p, tol = 1e-7) =>
    rows.map((r, i) => [i, r]).filter(([, [a, b, c]]) => Math.abs(a * p[0] + b * p[1] - c) <= tol).map(([i]) => i);
  // The region inside a view box, and every corner (feasible intersection of two rows).
  const region = (rows, box) => {
    const [x0, x1, y0, y1] = box;
    let poly = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
    for (const r of rows) poly = clip(poly, r);
    const onBox = (p) => Math.abs(p[0] - x0) < 1e-7 || Math.abs(p[0] - x1) < 1e-7 ||
                         Math.abs(p[1] - y0) < 1e-7 || Math.abs(p[1] - y1) < 1e-7;
    const vertices = [];
    for (let i = 0; i < rows.length; i++)
      for (let j = i + 1; j < rows.length; j++) {
        const p = solve2(rows[i], rows[j]);
        if (p && feasible(rows, p) && !vertices.some((v) => Math.hypot(v[0] - p[0], v[1] - p[1]) < 1e-7)) vertices.push(p);
      }
    return { poly, vertices, onBox };
  };
  // The segment of the line a·x + b·y = c inside a box, or null.
  const lineInBox = ([a, b, c], [x0, x1, y0, y1]) => {
    const seg = clip(clip([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], [a, b, c + 1e-6]), [-a, -b, -c + 1e-6]);
    if (seg.length < 2) return null;
    const pts = seg.slice().sort((p, q) => (p[0] - q[0]) || (p[1] - q[1]));
    return [pts[0], pts[pts.length - 1]];
  };

  function niceStep(span, target = 8) {
    const raw = span / target, mag = 10 ** Math.floor(Math.log10(raw));
    for (const m of [1, 2, 2.5, 5, 10]) if (raw <= m * mag * (1 + 1e-9)) return m * mag;
    return 10 * mag;
  }
  // A plot mapping data box [x0,x1]×[y0,y1] into an svg w×h, with grid and tick labels.
  // opts: pad (34), grid (true), aspect "equal" (default) or "fill", step [sx, sy].
  function plot(svg, box, w, h, opts = {}) {
    const pad = opts.pad ?? 34;
    const [x0, x1, y0, y1] = box;
    let sx = (w - 2 * pad) / (x1 - x0), sy = (h - 2 * pad) / (y1 - y0);
    if ((opts.aspect || "equal") === "equal") sx = sy = Math.min(sx, sy);
    const ox = pad + ((w - 2 * pad) - sx * (x1 - x0)) / 2, oy = pad + ((h - 2 * pad) - sy * (y1 - y0)) / 2;
    const X = (x) => ox + (x - x0) * sx, Y = (y) => h - oy - (y - y0) * sy;
    const inv = (px, py) => [x0 + (px - ox) / sx, y0 + (h - oy - py) / sy];
    const layer = (cls) => el("g", { class: cls }, svg);
    const axes = layer("viz-axes");
    const ticks = el("g", { class: "viz-ticks" });
    const [stx, sty] = opts.step || [niceStep(x1 - x0), niceStep(y1 - y0)];
    const [lx, ly] = opts.labelScale || [1, 1];   // tick labels = drawing units × labelScale
    if (opts.grid !== false) {
      const xAxisY = Y(Math.max(y0, Math.min(0, y1))), yAxisX = X(Math.max(x0, Math.min(0, x1)));
      for (let i = Math.ceil(x0 / stx - 1e-9); i * stx <= x1 + 1e-9; i++) {
        const x = i * stx;
        el("line", { x1: X(x), y1: Y(y0), x2: X(x), y2: Y(y1), class: i === 0 ? "viz-axis" : "viz-grid" }, axes);
        if (i !== 0) text(ticks, X(x), xAxisY + 15, num(x * lx), "viz-tick", "middle");
      }
      for (let i = Math.ceil(y0 / sty - 1e-9); i * sty <= y1 + 1e-9; i++) {
        const y = i * sty;
        el("line", { x1: X(x0), y1: Y(y), x2: X(x1), y2: Y(y), class: i === 0 ? "viz-axis" : "viz-grid" }, axes);
        if (i !== 0) text(ticks, yAxisX - 8, Y(y) + 4, num(y * ly), "viz-tick", "end");
      }
    }
    const toData = (evt) => { const q = svgPoint(svg, evt); return inv(q.x, q.y); };
    const raise = () => svg.appendChild(ticks);   // tick labels above everything drawn so far
    return { X, Y, sx, sy, box, layer, toData, inv, raise };
  }
  const polyPoints = (P, poly) => poly.map((p) => `${P.X(p[0])},${P.Y(p[1])}`).join(" ");

  // ------------------------------------------------------------ graphs
  // nodes: [{id, x, y, label}] in svg units. edges: [{id, u, v, label, directed, bend}].
  // State is shown by one class per node/edge: hot, chosen, muted, warn, good (see viz.css).
  function graph(svg, { nodes, edges }, opts = {}) {
    const r = opts.radius ?? 16;
    const gE = el("g", { class: "viz-g-edges" }, svg), gN = el("g", { class: "viz-g-nodes" }, svg);
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
    const kinds = ["", "hot", "chosen", "warn", "muted", "good"];
    const defs = el("defs", {}, svg);
    for (const k of kinds) {
      const m = el("marker", { id: `viz-arrow-${svg.dataset.vizId}-${k || "plain"}`, viewBox: "0 0 10 10", refX: 9, refY: 5,
                               markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse" }, defs);
      el("path", { d: "M0,0 L10,5 L0,10 z", class: `viz-arrowhead ${k}` }, m);
    }
    const marker = (k) => `url(#viz-arrow-${svg.dataset.vizId}-${k || "plain"})`;
    const edgeH = {}, nodeH = {};
    for (const e of edges) {
      const a = byId[e.u], b = byId[e.v];
      if (!a || !b) throw new Error(`edge ${e.u}-${e.v} names a missing node`);
      const g = el("g", { class: "viz-g-edge" }, gE);
      const dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1, ux = dx / len, uy = dy / len;
      const bend = e.bend || 0, gap = r + (e.directed ? 2 : 0);
      const mx = (a.x + b.x) / 2 - uy * bend, my = (a.y + b.y) / 2 + ux * bend;
      let sx = a.x + ux * r, sy = a.y + uy * r, tx = b.x - ux * gap, ty = b.y - uy * gap;
      if (bend) {  // start and end along the curve's tangents
        const d1 = Math.hypot(mx - a.x, my - a.y), d2 = Math.hypot(b.x - mx, b.y - my);
        sx = a.x + (mx - a.x) / d1 * r; sy = a.y + (my - a.y) / d1 * r;
        tx = b.x - (b.x - mx) / d2 * gap; ty = b.y - (b.y - my) / d2 * gap;
      }
      const path = el("path", { d: bend ? `M${sx},${sy} Q${mx},${my} ${tx},${ty}` : `M${sx},${sy} L${tx},${ty}`, class: "viz-g-line" }, g);
      if (e.directed) path.setAttribute("marker-end", marker(""));
      let lab = null;
      if (e.label !== undefined && e.label !== null) {
        const off = e.labelOffset ?? 13;
        const lx = bend ? (a.x + 2 * mx + b.x) / 4 - uy * Math.sign(bend) * 8 : (a.x + b.x) / 2 - uy * off;
        const ly = bend ? (a.y + 2 * my + b.y) / 4 + ux * Math.sign(bend) * 8 : (a.y + b.y) / 2 + ux * off;
        lab = text(g, lx, ly + 4, String(e.label), "viz-g-elabel", "middle");
      }
      edgeH[e.id ?? `${e.u}-${e.v}`] = { g, path, lab, directed: !!e.directed };
    }
    for (const n of nodes) {
      const g = el("g", { class: "viz-g-node" }, gN);
      const c = el("circle", { cx: n.x, cy: n.y, r, class: "viz-g-circle" }, g);
      const t = text(g, n.x, n.y + 5, String(n.label ?? n.id), "viz-g-nlabel", "middle");
      const note = text(g, n.x + (n.noteDx ?? 0), n.y + (n.noteDy ?? -r - 7), "", "viz-g-note", "middle");
      nodeH[n.id] = { g, c, t, note };
    }
    const setClass = (h, base, cls) => {
      h.g.setAttribute("class", base + (cls ? " " + cls : ""));
      if (h.directed) h.path.setAttribute("marker-end", marker(cls));
    };
    return {
      node: (id) => nodeH[id], edge: (id) => edgeH[id],
      nodeClass: (id, cls) => nodeH[id] && setClass(nodeH[id], "viz-g-node", cls),
      edgeClass: (id, cls) => edgeH[id] && setClass(edgeH[id], "viz-g-edge", cls),
      edgeLabel: (id, s) => { const h = edgeH[id]; if (h && h.lab) h.lab.textContent = s; },
      nodeNote: (id, s) => { const h = nodeH[id]; if (h) h.note.textContent = s; },
      nodeLabel: (id, s) => { const h = nodeH[id]; if (h) h.t.textContent = s; },
    };
  }

  // ------------------------------------------------------------ tables
  // header: array of strings (or null); rows: array of arrays; cls(i, j, value) -> class (row -1 = header).
  function table(parent, header, rows, cls) {
    const t = html("table", { class: "viz-tab" }, parent);
    if (header) {
      const tr = html("tr", {}, t);
      header.forEach((h, j) => html("th", { class: cls ? cls(-1, j, h) : null }, tr, h));
    }
    rows.forEach((r, i) => {
      const tr = html("tr", {}, t);
      r.forEach((v, j) => html("td", { class: cls ? cls(i, j, v) : null }, tr, typeof v === "number" || typeof v === "string" ? num(v) : v));
    });
    return t;
  }

  // ------------------------------------------------------------ the stepper shell
  // A figure that replays recorded states. spec:
  //   runs: [{title, states: [...]}]      states are whatever render() understands
  //   width, height: svg size (520 × 400); layout "side" (svg left, panel right) or "stack"
  //   setup(ctx): optional, once per run;  render(ctx): draw ctx.state
  //   ctx = {svg, panel, run, k, n, state, V}; svg and panel are emptied before each render
  // A state may carry .note (bold line above the panel) and .explain (muted text below it).
  function stepper(host, spec) {
    const runs = (spec.runs || []).filter((r) => r && r.states && r.states.length);
    if (!runs.length) return fail(host, "no recorded runs: run `uv run co viz`");
    host.classList.add("viz-stepper", spec.layout === "stack" ? "viz-stack" : "viz-side");
    isolate(host);
    const W = spec.width || 520, H = spec.height || 400;
    const left = html("div", { class: "viz-left" }, host);
    const svg = newSvg(left, W, H, spec.label || "step-through figure");
    const controls = html("div", { class: "viz-controls" }, left);
    let pick = null;
    if (runs.length > 1) {
      pick = html("select", { class: "viz-pick", "aria-label": "choose a run" }, controls);
      runs.forEach((r, i) => html("option", { value: i }, pick, r.title));
    }
    const first = html("button", { type: "button", title: "back to the start" }, controls, "⏮");
    const prev = html("button", { type: "button", title: "back (←)" }, controls, "◀");
    const next = html("button", { type: "button", title: "step (→)", class: "viz-next" }, controls, `${spec.stepWord || "step"} ▶`);
    const count = html("span", { class: "viz-count" }, controls);
    const right = html("div", { class: "viz-right" }, host);
    if (runs.length === 1 && runs[0].title) html("div", { class: "viz-runtitle" }, right, runs[0].title);
    const note = html("div", { class: "viz-note" }, right);
    const panel = html("div", { class: "viz-panel-body" }, right);
    const explain = html("div", { class: "viz-explain" }, right);

    let run = runs[0], k = 0;
    const ctx = () => ({ svg, panel, run, k, n: run.states.length, state: run.states[k], V: window.CoViz });
    function show() {
      const c = ctx();
      svg.replaceChildren();
      panel.replaceChildren();
      try { spec.render(c); } catch (err) { console.error(err); return fail(host, err.message); }
      note.textContent = c.state.note || "";
      explain.textContent = c.state.explain || "";
      count.textContent = `${k + 1} / ${run.states.length}`;
      first.disabled = prev.disabled = k === 0;
      next.disabled = k === run.states.length - 1;
    }
    function load(i) {
      run = runs[i]; k = 0;
      if (spec.setup) { try { spec.setup(ctx()); } catch (err) { console.error(err); return fail(host, err.message); } }
      show();
    }
    if (pick) pick.addEventListener("change", () => load(Number(pick.value)));
    first.addEventListener("click", () => { k = 0; show(); });
    prev.addEventListener("click", () => { if (k > 0) { k--; show(); } });
    next.addEventListener("click", () => { if (k < run.states.length - 1) { k++; show(); } });
    host.tabIndex = 0;
    host.addEventListener("keydown", (e) => {
      if (e.target.closest("select, input")) return;
      if (e.key === "ArrowRight" && k < run.states.length - 1) { k++; show(); e.preventDefault(); }
      if (e.key === "ArrowLeft" && k > 0) { k--; show(); e.preventDefault(); }
    });
    load(0);
    return { show, get k() { return k; } };
  }

  // Recorded data for this page: window.VIZ_DATA[key], or a visible error.
  const data = (host, key) => {
    const d = (window.VIZ_DATA || {})[key];
    if (!d) fail(host, `no recorded data "${key}": run \`uv run co viz\``);
    return d;
  };

  // ------------------------------------------------------------ registry and start-up
  const register = (name, build) => { registry[name] = build; };
  const init = () => document.querySelectorAll(".viz[data-viz]").forEach((host) => {
    if (host.dataset.vizReady) return;
    host.dataset.vizReady = "1";
    const build = registry[host.dataset.viz];
    if (!build) return fail(host, `no widget "${host.dataset.viz}" (is its script loaded?)`);
    try { build(host, window.CoViz); } catch (err) { console.error(err); fail(host, err.message); }
  });

  window.CoViz = {
    register, init, data, fail,
    el, html, text, num, isolate, svgPoint, newSvg, draggable, slider,
    clip, feasible, solve2, tightRows, region, lineInBox, plot, niceStep, polyPoints,
    graph, table, stepper,
  };
  // Widget scripts load after this one: start when the whole page has loaded.
  if (document.readyState === "complete") setTimeout(init, 0);
  else window.addEventListener("load", init);
})();
