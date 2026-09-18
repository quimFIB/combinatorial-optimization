// Two-variable LP figures: the polygon explorer (units 01, 03, 05) and the simplex
// stepper (unit 02). Needs slides/viz/viz.js.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  const rowText = ([a, b, c]) => {
    const term = (k, name, first) => {
      if (k === 0) return "";
      const sign = k < 0 ? "−" : first ? "" : "+";
      const mag = Math.abs(k) === 1 ? "" : num(Math.abs(k));
      return `${first ? sign : " " + sign + " "}${mag}${name}`;
    };
    const lhs = (term(a, "x", true) + term(b, "y", a === 0)).trim() || "0";
    return `${lhs} ≤ ${num(c)}`;
  };
  const objText = ([a, b]) => rowText([a, b, 0]).replace(" ≤ 0", "");

  // ---------------------------------------------------------------- polygon explorer
  //   data-rows='[[a,b,c],...]'  data-labels='["row 1",...]'  data-off="5,6"  (1-based rows off at start)
  //   data-objective="2,1"  data-box="x0,x1,y0,y1"  data-dual="off" to hide the certificate line
  //   data-shadow="y"  also show the projection onto the y-axis and Fourier–Motzkin's rows for it
  V.register("polytope", (host) => {
    const allRows = JSON.parse(host.dataset.rows);
    const labels = host.dataset.labels ? JSON.parse(host.dataset.labels) : allRows.map((_, i) => `constraint ${i + 1}`);
    const off = (host.dataset.off || "").split(",").filter(Boolean).map(Number);
    const active = allRows.map((_, i) => !off.includes(i + 1));
    const box = (host.dataset.box || "-1,6,-1,5").split(",").map(Number);
    const showDual = host.dataset.dual !== "off";
    const shadow = host.dataset.shadow === "y";
    let c = (host.dataset.objective || "2,1").split(",").map(Number);
    let probe = null, pinned = false;

    host.classList.add("viz-polytope");
    V.isolate(host);
    const W = 560, H = 470;
    const svg = V.newSvg(host, W, H, "interactive polygon: toggle constraints, drag the objective arrow, hover for slacks");
    const P = V.plot(svg, box, W, H);
    const gRegion = P.layer("viz-region"), gLines = P.layer("viz-lines"), gLevel = P.layer("viz-level"),
          gVerts = P.layer("viz-verts"), gProbe = P.layer("viz-probe"), gObj = P.layer("viz-obj");

    const panel = html("div", { class: "viz-panel" }, host);
    html("div", { class: "viz-head" }, panel, "constraints");
    const list = html("div", { class: "viz-rows" }, panel);
    const checks = allRows.map((r, i) => {
      const lab = html("label", { class: "viz-row" }, list);
      const cb = html("input", { type: "checkbox" }, lab);
      cb.checked = active[i];
      cb.addEventListener("change", () => { active[i] = cb.checked; draw(); });
      html("span", { class: "viz-row-name" }, lab, labels[i]);
      html("span", { class: "viz-row-text" }, lab, rowText(r));
      const slack = html("span", { class: "viz-slack" }, lab, "");
      return { lab, slack };
    });
    html("div", { class: "viz-head" }, panel, "objective");
    const objLine = html("div", { class: "viz-readout" }, panel);
    const optLine = html("div", { class: "viz-readout" }, panel);
    const certLine = html("div", { class: "viz-readout viz-cert" }, panel);
    let fmBox = null;
    if (shadow) { html("div", { class: "viz-head" }, panel, "eliminate x (Fourier–Motzkin)"); fmBox = html("div", { class: "viz-fm" }, panel); }
    html("div", { class: "viz-hint" }, panel, "Drag the arrow tip to turn the objective. Hover the plane for slacks; click to pin a point.");

    const dial = [W - 64, H - 64], R = 42;
    const drag = V.draggable(svg, (t) => t.classList.contains("viz-handle"), (x, y) => {
      // direction from the pointer; length grows with distance from the dial's centre, in steps of 0.5
      const ux = x - dial[0], uy = -(y - dial[1]), d = Math.hypot(ux, uy) || 1;
      const size = Math.max(1, Math.min(3, d / R * 2.5));
      let dx = Math.round(ux / d * size * 2) / 2, dy = Math.round(uy / d * size * 2) / 2;
      if (dx === 0 && dy === 0) return;
      c = [dx, dy];
      draw();
    });

    function draw() {
      const rows = allRows.filter((_, i) => active[i]);
      const { poly, vertices, onBox } = V.region(rows, box);
      for (const g of [gRegion, gLines, gLevel, gVerts, gProbe, gObj]) g.replaceChildren();

      allRows.forEach((r, i) => {
        if (!active[i]) return;
        const seg = V.lineInBox(r, box);
        if (seg) el("line", { x1: P.X(seg[0][0]), y1: P.Y(seg[0][1]), x2: P.X(seg[1][0]), y2: P.Y(seg[1][1]), class: "viz-rowline" }, gLines);
      });
      if (poly.length >= 3) {
        el("polygon", { points: V.polyPoints(P, poly), class: "viz-poly" }, gRegion);
        for (let i = 0; i < poly.length; i++) {
          const p = poly[i], q = poly[(i + 1) % poly.length], mid = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
          const open = onBox(p) && onBox(q) && V.tightRows(rows, mid).length === 0;
          el("line", { x1: P.X(p[0]), y1: P.Y(p[1]), x2: P.X(q[0]), y2: P.Y(q[1]), class: open ? "viz-edge-open" : "viz-edge" }, gRegion);
        }
      }

      objLine.textContent = `maximize ${objText(c)}`;
      certLine.textContent = "";
      if (poly.length < 3) {
        optLine.textContent = rows.length ? "infeasible: the constraints leave nothing" : "";
      } else {
        const val = (p) => c[0] * p[0] + c[1] * p[1];
        const best = Math.max(...poly.map(val));
        const winners = poly.filter((p) => val(p) >= best - 1e-7);
        const isVertex = (p) => vertices.some((v) => Math.hypot(v[0] - p[0], v[1] - p[1]) < 1e-7);
        const unbounded = winners.some((p) => onBox(p) && !isVertex(p));
        const lvl = V.lineInBox([c[0], c[1], best], box);
        if (lvl) el("line", { x1: P.X(lvl[0][0]), y1: P.Y(lvl[0][1]), x2: P.X(lvl[1][0]), y2: P.Y(lvl[1][1]), class: "viz-levelline" }, gLevel);
        if (unbounded) {
          optLine.textContent = "unbounded: the objective keeps growing past the edge of the view";
        } else {
          const opt = vertices.filter((v) => val(v) >= best - 1e-7);
          if (opt.length > 1) {
            const [p, q] = opt;
            el("line", { x1: P.X(p[0]), y1: P.Y(p[1]), x2: P.X(q[0]), y2: P.Y(q[1]), class: "viz-optedge" }, gLevel);
            optLine.textContent = `optimum ${num(best)} along a whole edge, (${num(p[0])}, ${num(p[1])}) to (${num(q[0])}, ${num(q[1])})`;
          } else if (opt.length === 1) {
            const v = opt[0];
            optLine.textContent = `optimum ${num(best)} at the corner (${num(v[0])}, ${num(v[1])})`;
            if (showDual) {
              const tight = V.tightRows(rows, v);
              outer: for (let i = 0; i < tight.length; i++)
                for (let j = i + 1; j < tight.length; j++) {
                  const ri = rows[tight[i]], rj = rows[tight[j]];
                  const y = V.solve2([ri[0], rj[0], c[0]], [ri[1], rj[1], c[1]]);
                  if (y && y[0] >= -1e-9 && y[1] >= -1e-9) {
                    const name = (r) => labels[allRows.indexOf(r)];
                    certLine.textContent = `certificate: c = ${num(y[0])}·(${name(ri)}) + ${num(y[1])}·(${name(rj)}), both weights ≥ 0, so nothing beats ${num(best)}`;
                    break outer;
                  }
                }
            }
          }
        }
        for (const v of vertices) {
          const isOpt = !unbounded && Math.abs(val(v) - best) < 1e-7;
          el("circle", { cx: P.X(v[0]), cy: P.Y(v[1]), r: isOpt ? 7 : 5, class: isOpt ? "viz-vertex-opt" : "viz-vertex" }, gVerts);
        }
      }

      el("circle", { cx: dial[0], cy: dial[1], r: R, class: "viz-dial" }, gObj);
      const len = Math.hypot(c[0], c[1]) || 1;
      const tip = [dial[0] + c[0] / len * R, dial[1] - c[1] / len * R];   // the arrow shows direction; c's size is in the label
      el("line", { x1: dial[0], y1: dial[1], x2: tip[0], y2: tip[1], class: "viz-arrow" }, gObj);
      el("circle", { cx: tip[0], cy: tip[1], r: 10, class: "viz-handle" }, gObj);
      V.text(gObj, dial[0], dial[1] + R + 16, `c = (${num(c[0])}, ${num(c[1])})`, "viz-tick");

      checks.forEach(({ lab, slack }, i) => {
        lab.classList.remove("viz-tight", "viz-violated");
        if (!probe || !active[i]) { slack.textContent = ""; return; }
        const [a, b, cc] = allRows[i], s = cc - (a * probe[0] + b * probe[1]);
        slack.textContent = `slack ${num(s)}`;
        if (Math.abs(s) < 0.05) lab.classList.add("viz-tight");
        else if (s < 0) lab.classList.add("viz-violated");
      });
      if (probe) {
        const inside = V.feasible(rows, probe, 0.05);
        el("circle", { cx: P.X(probe[0]), cy: P.Y(probe[1]), r: 6, class: inside ? "viz-probe-in" : "viz-probe-out" }, gProbe);
        V.text(gProbe, P.X(probe[0]) + 10, P.Y(probe[1]) - 10, `(${num(probe[0])}, ${num(probe[1])}) ${inside ? "inside" : "outside"}`, "viz-probe-text", "start");
      }
      if (shadow) drawShadow(rows, poly);
      P.raise(); svg.appendChild(gProbe); svg.appendChild(gObj);
    }

    // The shadow on the y-axis, and the rows Fourier–Motzkin derives for it: each pair of an
    // upper bound on x (a > 0) and a lower bound (a < 0), added with positive multipliers.
    function drawShadow(rows, poly) {
      fmBox.replaceChildren();
      const Z = rows.filter((r) => r[0] === 0), U = rows.filter((r) => r[0] > 0), L = rows.filter((r) => r[0] < 0);
      const derived = [...Z.map((r) => ({ row: [0, r[1], r[2]], from: `${labelOf(r)} (no x)` }))];
      for (const p of U) for (const q of L) {
        const mp = -q[0], mq = p[0];
        derived.push({ row: [0, mp * p[1] + mq * q[1], mp * p[2] + mq * q[2]], from: `${num(mp)}·(${labelOf(p)}) + ${num(mq)}·(${labelOf(q)})` });
      }
      let lo = -Infinity, hi = Infinity, empty = false;
      for (const d of derived) {
        const [, b, c] = d.row;
        if (b > 1e-12) hi = Math.min(hi, c / b);
        else if (b < -1e-12) lo = Math.max(lo, c / b);
        else if (c < -1e-9) empty = true;
        const line = html("div", { class: "viz-fm-row" }, fmBox);
        html("span", { class: "viz-row-text" }, line, b === 0 ? `0 ≤ ${num(c)}` : rowText([0, b, c]).replace(/^0 ?\+? ?/, ""));
        html("span", { class: "viz-slack" }, line, ` from ${d.from}`);
      }
      const summary = html("div", { class: "viz-readout" }, fmBox);
      if (empty || lo > hi + 1e-9) summary.textContent = "some derived constraint reads 0 ≤ negative: no point at all (Farkas)";
      else summary.textContent = `so y ranges over [${num(lo)}, ${num(hi)}]`;
      if (poly.length >= 3 && !empty && lo <= hi + 1e-9) {
        const x = P.X(box[0]) + 10;
        const y0 = Math.max(lo, box[2]), y1 = Math.min(hi, box[3]);
        el("line", { x1: x, y1: P.Y(y0), x2: x, y2: P.Y(y1), class: "viz-shadowbar" }, gLevel);
      }
    }
    function labelOf(r) { return labels[allRows.indexOf(r)]; }

    const snap = (q) => [Math.round(q[0] * 4) / 4, Math.round(q[1] * 4) / 4];
    svg.addEventListener("pointermove", (e) => { if (!drag.dragging && !pinned && !e.buttons) { probe = snap(P.toData(e)); draw(); } });
    svg.addEventListener("pointerleave", () => { if (!pinned && !drag.dragging) { probe = null; draw(); } });
    svg.addEventListener("click", (e) => {
      if (e.target.classList.contains("viz-handle") || e.target.classList.contains("viz-dial")) return;
      pinned = !pinned; probe = snap(P.toData(e)); draw();
    });
    draw();
  });

  // ---------------------------------------------------------------- simplex stepper
  //   data-runs="key1,key2"   keys into window.VIZ_DATA, recorded by slides/viz/traces/u02.py
  V.register("simplex", (host) => {
    const keys = (host.dataset.runs || "").split(",").filter(Boolean);
    const runs = keys.map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    let frame = null;
    V.stepper(host, {
      runs, width: 520, height: 400, stepWord: "pivot", label: "simplex path on the feasible region",
      setup(ctx) {
        const run = ctx.run;
        const rows = run.A.map((r, i) => [r[0], r[1], run.b[i]]).concat([[-1, 0, 0], [0, -1, 0]]);
        const reg = V.region(rows, [-1e6, 1e6, -1e6, 1e6]);
        const pts = run.states.map((s) => s.point);
        const mx = Math.max(...reg.vertices.map((v) => v[0]), ...pts.map((p) => p[0]));
        const my = Math.max(...reg.vertices.map((v) => v[1]), ...pts.map((p) => p[1]));
        // keep the drawing readable on lopsided instances: rescale each axis by a round factor
        const nice = (v) => [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000].find((f) => v / f <= 8) || Math.ceil(v / 8);
        const scale = [nice(mx), nice(my)];
        frame = {
          scale, rows: rows.map(([a, b, c]) => [a * scale[0], b * scale[1], c]),
          box: [-0.5, mx / scale[0] + 1, -0.5, my / scale[1] + 1],
        };
      },
      render(ctx) {
        const { svg, panel, run, k } = ctx;
        const st = run.states[k], [s0, s1] = frame.scale;
        const P = V.plot(svg, frame.box, 520, 400, { labelScale: frame.scale });
        const reg = V.region(frame.rows, frame.box);
        el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-poly" }, svg);
        for (const v of reg.vertices) el("circle", { cx: P.X(v[0]), cy: P.Y(v[1]), r: 4, class: "viz-vertex" }, svg);
        for (let i = 1; i <= k; i++) {
          const a = run.states[i - 1].point, b = run.states[i].point;
          el("line", { x1: P.X(a[0] / s0), y1: P.Y(a[1] / s1), x2: P.X(b[0] / s0), y2: P.Y(b[1] / s1), class: "viz-pathline" }, svg);
        }
        run.states.slice(0, k + 1).forEach((s, i) =>
          el("circle", { cx: P.X(s.point[0] / s0), cy: P.Y(s.point[1] / s1), r: i === k ? 8 : 5, class: i === k ? "viz-vertex-opt" : "viz-vertex-seen" }, svg));
        V.text(svg, P.X(st.point[0] / s0) + 12, P.Y(st.point[1] / s1) - 10, `(${st.point_exact.join(", ")})  z = ${st.z}`, "viz-probe-text", "start");
        if (s0 !== s1) V.text(svg, 512, 16, "x and y drawn at different scales", "viz-tick", "end");
        P.raise();

        const header = ["basis", ...run.columns, "rhs", "ratio"];
        const rows = st.tableau.map((r, i) => {
          const isObj = i === st.tableau.length - 1;
          return [isObj ? "z" : st.basis[i], ...r, isObj || !st.ratios ? "" : (st.ratios[i] ?? "—")];
        });
        const last = rows.length - 1, ncol = header.length;
        V.table(panel, header, rows, (i, j, v) => {
          const cls = [];
          if (j === 0) cls.push("viz-bas");
          if (st.enter !== null && j === st.enter + 1) cls.push("viz-col-enter");
          if (i === st.leave && st.enter !== null) cls.push("viz-row-leave");
          if (i === st.leave && j === st.enter + 1) cls.push("viz-pivot");
          if (i === last) cls.push("viz-objrow");
          if (i === last && j > 0 && j < ncol - 2 && String(v).startsWith("-")) cls.push("viz-neg");
          if (j === ncol - 1) cls.push("viz-ratio");
          return cls.join(" ");
        });
        const rule = run.rule === "bland" ? "Bland's rule takes the lowest-index negative entry" : "Dantzig's rule takes the most negative entry";
        if (st.enter === null || st.enter === undefined) {
          st.explain = st.explain || "No negative entry is left in the objective row: every reduced cost is ≤ 0, so this corner is optimal. The slack columns of that row are the duals.";
        } else if (st.leave === null || st.leave === undefined) {
          st.explain = `No positive entry in column ${run.columns[st.enter]}: nothing stops it growing, so the LP is unbounded.`;
        } else {
          st.explain = `${rule} of the objective row: ${run.columns[st.enter]}. The ratio test divides rhs by the positive entries of that column; ` +
            `the smallest ratio, ${st.ratios[st.leave]}, belongs to ${st.basis[st.leave]}, which leaves. The boxed entry is the pivot.`;
        }
      },
    });
  });
})();
