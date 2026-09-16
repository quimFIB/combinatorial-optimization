// Integer-programming figures for units 06–09: TU determinants and Ghouila-Houri signings (06),
// the branch-and-bound tree (07), Gomory rounds and cover separation (08), Stoer–Wagner and
// polarity (09). Needs slides/viz/viz.js. Geometry and small enumerations are computed in the
// page from the data in the HTML; algorithm runs come from the unit's viz-data.js.
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;
  const minus = (s) => String(s).replace(/-(?=[\d.∞])/g, "−");
  // a·x₁ + b·x₂ as text, dropping zero terms and unit coefficients: "x₁ − 2x₂"
  const lin = (coefs, names = ["x₁", "x₂"]) => {
    let out = "";
    coefs.forEach((k, i) => {
      if (Math.abs(k) < 1e-12) return;
      const mag = Math.abs(k) === 1 ? "" : num(Math.abs(k));
      out += out ? (k < 0 ? " − " : " + ") + mag + names[i] : (k < 0 ? "−" : "") + mag + names[i];
    });
    return out || "0";
  };

  // ---------------------------------------------------------------- shared: small integer algebra
  const det = (M) => {
    const n = M.length;
    if (n === 1) return M[0][0];
    if (n === 2) return M[0][0] * M[1][1] - M[0][1] * M[1][0];
    let d = 0;
    for (let j = 0; j < n; j++) {
      if (M[0][j] === 0) continue;
      const minor = M.slice(1).map((r) => r.filter((_, k) => k !== j));
      d += (j % 2 ? -1 : 1) * M[0][j] * det(minor);
    }
    return d;
  };
  const subsets = (n, k) => {
    const out = [], cur = [];
    const rec = (start) => {
      if (cur.length === k) { out.push(cur.slice()); return; }
      for (let i = start; i < n; i++) { cur.push(i); rec(i + 1); cur.pop(); }
    };
    rec(0);
    return out;
  };
  const matrixPicker = (host, matrices, onPick) => {
    if (matrices.length < 2) return null;
    const bar = html("div", { class: "viz-controls" }, host);
    const pick = html("select", { class: "viz-pick", "aria-label": "choose a matrix" }, bar);
    matrices.forEach((m, i) => html("option", { value: i }, pick, m.title));
    pick.addEventListener("change", () => onPick(Number(pick.value)));
    return bar;
  };

  // ---------------------------------------------------------------- 06: determinants of submatrices
  //   data-matrices='[{"title":..., "rows":[...], "cols":[...], "M":[[...]]}, ...]'
  V.register("tu-det", (host) => {
    const matrices = JSON.parse(host.dataset.matrices);
    host.classList.add("viz-stack", "viz-ip");
    V.isolate(host);
    let m, selR, selC;
    matrixPicker(host, matrices, (i) => load(i));
    const body = html("div", { class: "viz-ip-cols" }, host);
    const gridBox = html("div", { class: "viz-ip-grid" }, body);
    const side = html("div", { class: "viz-right" }, body);
    const readout = html("div", { class: "viz-note" }, side);
    const detail = html("div", { class: "viz-readout" }, side);
    const bar = html("div", { class: "viz-controls" }, side);
    const all = html("button", { type: "button", class: "viz-btn" }, bar, "check every square submatrix");
    const clear = html("button", { type: "button", class: "viz-btn" }, bar, "clear selection");
    const report = html("div", { class: "viz-panel-body" }, side);
    html("div", { class: "viz-hint" }, side, "Click row and column headers to pick a square submatrix; its determinant appears on the right.");

    function load(i) {
      m = matrices[i]; selR = new Set(); selC = new Set();
      report.replaceChildren();
      draw();
    }
    function draw() {
      gridBox.replaceChildren();
      const t = html("table", { class: "viz-tab viz-matrix" }, gridBox);
      const head = html("tr", {}, t);
      html("th", {}, head, "");
      m.cols.forEach((c, j) => {
        const th = html("th", { class: "viz-pickable" + (selC.has(j) ? " viz-hl" : "") }, head, c);
        th.addEventListener("click", () => { selC.has(j) ? selC.delete(j) : selC.add(j); draw(); });
      });
      m.M.forEach((row, i) => {
        const tr = html("tr", {}, t);
        const th = html("th", { class: "viz-pickable viz-bas" + (selR.has(i) ? " viz-hl" : "") }, tr, m.rows[i]);
        th.addEventListener("click", () => { selR.has(i) ? selR.delete(i) : selR.add(i); draw(); });
        row.forEach((v, j) => html("td", { class: selR.has(i) && selC.has(j) ? "viz-pivotcell" : "" }, tr, minus(v)));
      });
      const R = [...selR].sort((a, b) => a - b), C = [...selC].sort((a, b) => a - b);
      if (!R.length && !C.length) { readout.textContent = "pick rows and columns"; detail.textContent = ""; }
      else if (R.length !== C.length) { readout.textContent = `${R.length} rows × ${C.length} columns: not square`; detail.textContent = "pick as many rows as columns"; }
      else {
        const d = det(R.map((i) => C.map((j) => m.M[i][j])));
        readout.textContent = `${R.length}×${R.length} submatrix: determinant ${minus(d)}`;
        readout.className = "viz-note " + (Math.abs(d) <= 1 ? "viz-okline" : "viz-badline");
        detail.textContent = Math.abs(d) <= 1 ? "in {−1, 0, 1}: fine for TU" : "outside {−1, 0, 1}: this one submatrix already makes the matrix not TU";
      }
    }
    all.addEventListener("click", () => {
      report.replaceChildren();
      const rows = [];
      let bad = null, total = 0, allOk = true;
      for (let k = 1; k <= Math.min(m.M.length, m.M[0].length); k++) {
        const counts = new Map();
        for (const R of subsets(m.M.length, k)) for (const C of subsets(m.M[0].length, k)) {
          const d = det(R.map((i) => C.map((j) => m.M[i][j])));
          counts.set(d, (counts.get(d) || 0) + 1);
          total++;
          if (Math.abs(d) > 1 && !bad) bad = [R, C, d];
          if (Math.abs(d) > 1) allOk = false;
        }
        rows.push([`${k}×${k}`, [...counts.values()].reduce((a, b) => a + b, 0),
          [...counts.entries()].sort((a, b) => a[0] - b[0]).map(([d, c]) => `${c} × ${minus(d)}`).join(", ")]);
      }
      V.table(report, ["size", "count", "determinants"], rows, (i, j) => (j === 2 ? "viz-left" : ""));
      html("div", { class: "viz-readout " + (allOk ? "viz-cert" : "viz-badtext") }, report,
        allOk ? `all ${total} determinants in {−1, 0, 1}: totally unimodular` :
          `not TU: rows ${bad[0].map((i) => m.rows[i]).join(", ")} × columns ${bad[1].map((j) => m.cols[j]).join(", ")} has determinant ${minus(bad[2])} (now selected)`);
      if (bad) { selR = new Set(bad[0]); selC = new Set(bad[1]); draw(); }
    });
    clear.addEventListener("click", () => { selR = new Set(); selC = new Set(); report.replaceChildren(); draw(); });
    load(0);
  });

  // ---------------------------------------------------------------- 06: Ghouila-Houri signings
  //   same data-matrices; click a row's sign to cycle it: off → + → − → off
  V.register("gh-sign", (host) => {
    const matrices = JSON.parse(host.dataset.matrices);
    host.classList.add("viz-stack", "viz-ip");
    V.isolate(host);
    let m, sign;
    matrixPicker(host, matrices, (i) => load(i));
    const body = html("div", { class: "viz-ip-cols" }, host);
    const gridBox = html("div", { class: "viz-ip-grid" }, body);
    const side = html("div", { class: "viz-right" }, body);
    const readout = html("div", { class: "viz-note" }, side);
    const detail = html("div", { class: "viz-readout" }, side);
    const bar = html("div", { class: "viz-controls" }, side);
    const search = html("button", { type: "button", class: "viz-btn" }, bar, "search for a good signing of these rows");
    const every = html("button", { type: "button", class: "viz-btn" }, bar, "test every row subset");
    const report = html("div", { class: "viz-readout" }, side);
    html("div", { class: "viz-hint" }, side, "Click the sign cell of a row to cycle off → + → −. The bottom line is the signed sum of the chosen rows.");

    function load(i) { m = matrices[i]; sign = m.M.map(() => 0); report.textContent = ""; draw(); }
    const sums = (s) => m.cols.map((_, j) => m.M.reduce((acc, row, i) => acc + s[i] * row[j], 0));
    const goodSigning = (rows) => {
      if (!rows.length) return [];
      for (let mask = 0; mask < 1 << (rows.length - 1); mask++) {
        const s = m.M.map(() => 0);
        rows.forEach((r, k) => { s[r] = k === 0 ? 1 : (mask >> (k - 1)) & 1 ? -1 : 1; });
        if (sums(s).every((v) => Math.abs(v) <= 1)) return s;
      }
      return null;
    };
    function draw() {
      gridBox.replaceChildren();
      const t = html("table", { class: "viz-tab viz-matrix" }, gridBox);
      const head = html("tr", {}, t);
      html("th", {}, head, "sign");
      html("th", {}, head, "");
      m.cols.forEach((c) => html("th", {}, head, c));
      m.M.forEach((row, i) => {
        const tr = html("tr", { class: sign[i] ? "" : "viz-offrow" }, t);
        const td = html("td", { class: "viz-pickable viz-sign" }, tr, sign[i] === 1 ? "+" : sign[i] === -1 ? "−" : "·");
        td.addEventListener("click", () => { sign[i] = sign[i] === 0 ? 1 : sign[i] === 1 ? -1 : 0; report.textContent = ""; draw(); });
        html("th", { class: "viz-bas" }, tr, m.rows[i]);
        row.forEach((v) => html("td", {}, tr, minus(v)));
      });
      const s = sums(sign);
      const tr = html("tr", { class: "viz-sumrow" }, t);
      html("td", {}, tr, "");
      html("th", { class: "viz-bas" }, tr, "sum");
      s.forEach((v) => html("td", { class: Math.abs(v) <= 1 ? "" : "viz-bad" }, tr, minus(v)));
      const chosen = sign.filter(Boolean).length;
      if (!chosen) { readout.textContent = "choose some rows by giving them a sign"; readout.className = "viz-note"; detail.textContent = ""; return; }
      const ok = s.every((v) => Math.abs(v) <= 1);
      readout.textContent = ok ? `a good signing of these ${chosen} rows` : "not a good signing: some column sums to ±2 or more";
      readout.className = "viz-note " + (ok ? "viz-okline" : "viz-badline");
      detail.textContent = "Ghouila-Houri: the matrix is TU exactly when every subset of rows has some good signing.";
    }
    search.addEventListener("click", () => {
      const rows = sign.map((v, i) => (v ? i : -1)).filter((i) => i >= 0);
      if (!rows.length) { report.textContent = "give some rows a sign first"; return; }
      const s = goodSigning(rows);
      if (s) { sign = s; draw(); report.textContent = `found one by trying up to ${2 ** (rows.length - 1)} signings`; report.className = "viz-readout viz-cert"; }
      else { report.textContent = `none of the ${2 ** (rows.length - 1)} signings works: this row subset is a witness that the matrix is not TU`; report.className = "viz-readout viz-badtext"; }
    });
    every.addEventListener("click", () => {
      let tested = 0;
      for (let k = 1; k <= m.M.length; k++) for (const rows of subsets(m.M.length, k)) {
        tested++;
        const s = goodSigning(rows);
        if (!s) {
          sign = m.M.map((_, i) => (rows.includes(i) ? 1 : 0)); draw();
          report.textContent = `rows ${rows.map((i) => m.rows[i]).join(", ")} have no good signing (now chosen): not TU`;
          report.className = "viz-readout viz-badtext"; return;
        }
      }
      report.textContent = `all ${tested} row subsets have a good signing: TU`;
      report.className = "viz-readout viz-cert";
    });
    load(0);
  });

  // ---------------------------------------------------------------- 07: branch and bound
  //   data-runs="best,dfs" : keys into VIZ_DATA.runs; VIZ_DATA.rows are [a, b, c] with a·x + b·y <= c
  V.register("bb-tree", (host) => {
    const D = V.data(host, "runs");
    if (!D) return;
    const rows = window.VIZ_DATA.rows.concat([[-1, 0, 0], [0, -1, 0]]);
    const keys = (host.dataset.runs || "best,dfs").split(",");
    const box = [-0.5, 4, -0.5, 3.5];
    V.stepper(host, {
      runs: keys.map((k) => D[k]), width: 440, height: 380, stepWord: "pop", label: "branch-and-bound on the running example",
      render({ svg, panel, state }) {
        const P = V.plot(svg, box, 440, 380);
        const reg = V.region(rows, box);
        el("polygon", { points: V.polyPoints(P, reg.poly), class: "viz-poly" }, svg);
        const cur = state.current !== null ? state.nodes[state.current] : null;
        if (cur) {  // the current node's box of variable bounds
          const [x0, y0] = cur.lb, [x1, y1] = cur.ub;
          const bx = [Math.max(x0, box[0]), Math.min(x1, box[1])], by = [Math.max(y0, box[2]), Math.min(y1, box[3])];
          if (bx[0] <= bx[1] && by[0] <= by[1])
            el("rect", { x: P.X(bx[0]), y: P.Y(by[1]), width: Math.max(2, P.X(bx[1]) - P.X(bx[0])), height: Math.max(2, P.Y(by[0]) - P.Y(by[1])), class: "viz-nodebox" }, svg);
        }
        for (let x = 0; x <= 4; x++) for (let y = 0; y <= 3; y++)
          if (V.feasible(rows, [x, y])) el("circle", { cx: P.X(x), cy: P.Y(y), r: 3.5, class: "viz-vertex" }, svg);
        for (const n of state.nodes) if (n.x) {
          const isCur = cur && n.id === cur.id;
          el("circle", { cx: P.X(n.x[0]), cy: P.Y(n.x[1]), r: isCur ? 7 : 4, class: isCur ? "viz-vertex-opt" : "viz-lpdot" }, svg);
        }
        if (state.incumbent_x) {
          const [x, y] = state.incumbent_x;
          el("rect", { x: P.X(x) - 7, y: P.Y(y) - 7, width: 14, height: 14, class: "viz-incumbent" }, svg);
        }
        P.raise();
        V.text(svg, 432, 18, "box: the current node's bounds", "viz-tick", "end");

        // the tree, as its own svg in the panel
        const byParent = {};
        state.nodes.forEach((n) => { (byParent[n.parent] = byParent[n.parent] || []).push(n); });
        const depth = {}, xpos = {};
        let leaf = 0;
        const place = (n, d) => {
          depth[n.id] = d;
          const kids = byParent[n.id] || [];
          if (!kids.length) { xpos[n.id] = leaf++; return; }
          kids.forEach((k) => place(k, d + 1));
          xpos[n.id] = (xpos[kids[0].id] + xpos[kids[kids.length - 1].id]) / 2;
        };
        place(state.nodes[0], 0);
        const maxD = Math.max(...Object.values(depth)), W = 640, H = Math.max(160, 64 * (maxD + 1) + 16);
        const tsvg = V.newSvg(panel, W, H, "the search tree");
        tsvg.classList.add("viz-treesvg");
        const colW = (W - 20) / Math.max(1, leaf), X = (id) => 10 + colW * (xpos[id] + 0.5), Y = (id) => 30 + depth[id] * 64;
        const bw = Math.min(130, colW - 6);
        for (const n of state.nodes) if (n.parent !== null)
          el("line", { x1: X(n.parent), y1: Y(n.parent) + 20, x2: X(n.id), y2: Y(n.id) - 20, class: "viz-treeedge" }, tsvg);
        for (const n of state.nodes) {
          const g = el("g", { class: `viz-tnode viz-t-${n.status.replace(/ /g, "-")}${state.current === n.id ? " viz-t-current" : ""}` }, tsvg);
          el("rect", { x: X(n.id) - bw / 2, y: Y(n.id) - 20, width: bw, height: 40, rx: 6 }, g);
          V.text(g, X(n.id), Y(n.id) - 4, n.branch, "viz-tlabel");
          V.text(g, X(n.id), Y(n.id) + 13, n.value === null ? "infeasible" : minus(num(n.value)), "viz-tsub");
        }
        const inc = state.incumbent === null ? "none yet" : minus(num(state.incumbent));
        const low = state.lower === null ? "—" : minus(num(state.lower));
        html("div", { class: "viz-readout" }, panel, `incumbent U = ${inc} · global lower bound L = ${low} · open: ${state.frontier.length}`);
        const legend = html("div", { class: "viz-tlegend" }, panel);
        for (const [cls, word] of [["open", "open (dashed)"], ["branched", "branched"], ["incumbent", "integral"], ["pruned-by-bound", "pruned or infeasible"]])
          html("span", { class: `viz-tkey viz-t-${cls}` }, legend, word);
        state.note = minus(state.note);
      },
    });
  });

  // ---------------------------------------------------------------- 08: Gomory rounds
  //   data-runs="deck,diamond,four": keys into VIZ_DATA
  V.register("gomory", (host) => {
    const keys = (host.dataset.runs || "deck").split(",");
    const runs = keys.map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    let box = null;
    V.stepper(host, {
      runs, width: 500, height: 400, stepWord: "round", label: "Gomory cuts on a two-variable integer program",
      setup({ run }) {
        const rows = run.states[0].rows.map((r) => r).concat([[-1, 0, 0], [0, -1, 0]]);
        const reg = V.region(rows, [-1e4, 1e4, -1e4, 1e4]);
        const mx = Math.max(...reg.vertices.map((v) => v[0])), my = Math.max(...reg.vertices.map((v) => v[1]));
        box = [-0.4, Math.max(2, Math.ceil(mx)) + 0.4, -0.4, Math.max(2, Math.ceil(my)) + 0.4];
      },
      render({ svg, panel, run, k, state }) {
        const P = V.plot(svg, box, 500, 400);
        const nonneg = [[-1, 0, 0], [0, -1, 0]];
        const base = state.rows.slice(0, state.base).concat(nonneg);
        const now = state.rows.concat(nonneg);
        el("polygon", { points: V.polyPoints(P, V.region(base, box).poly), class: "viz-shade-warn" }, svg);
        el("polygon", { points: V.polyPoints(P, V.region(now, box).poly), class: "viz-poly" }, svg);
        state.rows.slice(state.base).forEach((r) => {
          const s = V.lineInBox(r, box);
          if (s) el("line", { x1: P.X(s[0][0]), y1: P.Y(s[0][1]), x2: P.X(s[1][0]), y2: P.Y(s[1][1]), class: "viz-oldcut" }, svg);
        });
        for (let x = 0; x <= box[1]; x++) for (let y = 0; y <= box[3]; y++)
          if (V.feasible(base, [x, y], 1e-9)) el("circle", { cx: P.X(x), cy: P.Y(y), r: 3.5, class: "viz-vertex" }, svg);
        if (state.cut) {
          const s = V.lineInBox(state.cut, box);
          if (s) el("line", { x1: P.X(s[0][0]), y1: P.Y(s[0][1]), x2: P.X(s[1][0]), y2: P.Y(s[1][1]), class: "viz-cut" }, svg);
        }
        const [px, py] = state.point;
        el("circle", { cx: P.X(px), cy: P.Y(py), r: 8, class: state.cut ? "viz-ring-warn" : "viz-vertex-opt" }, svg);
        V.text(svg, P.X(px) + 11, P.Y(py) - 9, `(${state.point_exact.join(", ")})`, "viz-probe-text", "start");
        P.raise();
        const rowText = ([a, b, c]) => `${lin([a, b])} ≤ ${minus(num(c))}`;
        const tbl = run.states.slice(0, run.states.length).map((s, i) => [String(i), `(${s.point_exact.join(", ")})`, s.value, s.cut ? rowText(s.cut) : "integral"]);
        V.table(panel, ["round", "LP optimum", "value", "cut added"], tbl, (i) => (i === k ? "viz-hl" : i > k ? "viz-soft viz-future" : ""));
        html("div", { class: "viz-readout" }, panel, run.lp);
        state.explain = state.cut
          ? "The dashed red line is the cut from the most fractional row of the optimal tableau. It cuts off no integer point (it may touch some), and the ring (this round's LP optimum) is on its wrong side. Light red: the region the cuts have removed so far."
          : "The LP optimum is integral, so it is the integer optimum: the cuts carved the region down until a corner of it was an integer point.";
      },
    });
  });

  // ---------------------------------------------------------------- 08: cover separation, live
  //   data-weights="5,5,5,5,8" data-capacity="12" data-x="1,0.7,0.7,0,0"
  V.register("cover", (host) => {
    const w = host.dataset.weights.split(",").map(Number), cap = Number(host.dataset.capacity);
    let x = host.dataset.x.split(",").map(Number);
    const n = w.length;
    host.classList.add("viz-ip-cols", "viz-ip");
    V.isolate(host);
    const left = html("div", { class: "viz-right" }, host);
    html("div", { class: "viz-readout viz-mono" }, left, `row: ${w.map((v, j) => `${v}x${j}`).join(" + ")} ≤ ${cap}`);
    const sliders = x.map((v, j) => V.slider(left, { label: `x${j} (weight ${w[j]})`, min: 0, max: 1, step: 0.05, value: v }, (val) => { x[j] = val; draw(); }));
    const load = html("div", { class: "viz-readout" }, left);
    html("div", { class: "viz-hint" }, left, "Move the LP values. Covers are sets too heavy to fit; a cover's inequality is violated when its cost Σ(1 − x) is below 1.");
    const right = html("div", { class: "viz-right" }, host);
    const best = html("div", { class: "viz-note" }, right);
    const tableBox = html("div", {}, right);
    const lift = html("div", { class: "viz-readout" }, right);

    const all = [];
    for (let mask = 1; mask < 1 << n; mask++) {
      const S = [...Array(n).keys()].filter((j) => mask >> j & 1);
      const weight = S.reduce((a, j) => a + w[j], 0);
      if (weight <= cap) continue;
      if (S.some((j) => weight - w[j] > cap)) continue;   // not minimal
      all.push({ S, weight });
    }
    const liftCover = (C) => {  // sequential up-lifting in index order, brute force over the lifted set
      const alpha = w.map((_, j) => (C.includes(j) ? 1 : 0)), rhs = C.length - 1, lifted = C.slice();
      for (let j = 0; j < n; j++) {
        if (C.includes(j)) continue;
        const room = cap - w[j];
        let bestv = -1;
        if (room >= 0) {
          bestv = 0;
          for (let mask = 1; mask < 1 << lifted.length; mask++) {
            const T = lifted.filter((_, k) => mask >> k & 1);
            if (T.reduce((a, i) => a + w[i], 0) <= room) bestv = Math.max(bestv, T.reduce((a, i) => a + alpha[i], 0));
          }
        }
        alpha[j] = bestv >= 0 ? rhs - bestv : rhs;
        lifted.push(j);
      }
      return { alpha, rhs };
    };
    function draw() {
      const used = w.reduce((a, v, j) => a + v * x[j], 0);
      load.textContent = `load at x*: ${num(used)} of ${cap}` + (used > cap + 1e-9 ? " (infeasible for the LP, but separation still works)" : "");
      load.className = "viz-readout" + (used > cap + 1e-9 ? " viz-badtext" : "");
      const rows = all.map(({ S, weight }) => ({ S, weight, cost: S.reduce((a, j) => a + 1 - x[j], 0) })).sort((a, b) => a.cost - b.cost || a.S.length - b.S.length);
      tableBox.replaceChildren();
      V.table(tableBox, ["minimal cover", "weight", "Σ (1 − x*)", "violated?"],
        rows.map((r) => [`{${r.S.join(", ")}}`, String(r.weight), num(r.cost), r.cost < 1 - 1e-9 ? "yes" : "no"]),
        (i, j) => (i >= 0 && rows[i].cost < 1 - 1e-9 ? (j === 3 ? "viz-bad" : "viz-hl") : ""));
      const top = rows[0];
      if (top && top.cost < 1 - 1e-9) {
        best.textContent = `most violated: {${top.S.join(", ")}}, left side ${num(top.S.reduce((a, j) => a + x[j], 0))} > ${top.S.length - 1}`;
        best.className = "viz-note viz-badline";
        const { alpha, rhs } = liftCover(top.S);
        const lhs = alpha.reduce((a, v, j) => a + v * x[j], 0);
        lift.textContent = `lifted: ${alpha.map((v, j) => (v ? `${v === 1 ? "" : v}x${j}` : "")).filter(Boolean).join(" + ")} ≤ ${rhs}; at x* the left side is ${num(lhs)}`;
      } else {
        best.textContent = "no cover inequality is violated at this point";
        best.className = "viz-note viz-okline";
        lift.textContent = "";
      }
    }
    draw();
  });

  // ---------------------------------------------------------------- 09: Stoer–Wagner
  //   data-runs="four,six": keys into VIZ_DATA
  V.register("stoer-wagner", (host) => {
    const keys = (host.dataset.runs || "four").split(",");
    const runs = keys.map((k) => V.data(host, k));
    if (runs.some((r) => !r)) return;
    const hue = ["#1f4a54", "#8c5e12", "#63397a", "#1f6b3f", "#8a3a3a", "#2a4a80"];
    V.stepper(host, {
      runs, width: 460, height: 400, stepWord: "step", label: "Stoer–Wagner minimum cut",
      render({ svg, panel, run, k, state }) {
        const pos = run.pos;
        const groupOf = {};
        state.groups.forEach((g, gi) => g.forEach((v) => { groupOf[v] = gi; }));
        // blobs behind merged groups
        state.groups.forEach((g, gi) => {
          if (g.length < 2) return;
          const pts = g.map((v) => pos[v]);
          for (let a = 0; a < pts.length; a++) for (let b = a + 1; b < pts.length; b++)
            el("line", { x1: pts[a][0], y1: pts[a][1], x2: pts[b][0], y2: pts[b][1], class: "viz-blob", style: `stroke:${hue[gi % hue.length]}` }, svg);
        });
        const label = (g) => g.join("+");
        const orderSet = new Set(state.order.flat());
        const last = state.order.length ? state.order[state.order.length - 1] : [];
        const G = V.graph(svg, {
          nodes: pos.map((p, v) => ({ id: v, x: p[0], y: p[1], label: v, noteDy: p[1] > 200 ? 34 : -24 })),
          edges: run.edges.map(([u, v, wt]) => ({ id: `${u}-${v}`, u, v, label: num(wt) })),
        }, { radius: 17 });
        run.edges.forEach(([u, v]) => {
          const inside = groupOf[u] === groupOf[v];
          if (inside) G.edgeClass(`${u}-${v}`, "muted");
          else if (state.cut && (state.cut[0].includes(u) !== state.cut[0].includes(v))) G.edgeClass(`${u}-${v}`, "warn");
        });
        pos.forEach((_, v) => {
          if (last.includes(v)) G.nodeClass(v, "chosen");
          else if (orderSet.has(v)) G.nodeClass(v, "hot");
        });
        for (const [key, att] of Object.entries(state.attach || {})) {
          const first = Number(key.split("+")[0]);
          G.nodeNote(first, `attached ${num(att)}`);
        }
        // panel: phase order and best cut
        if (state.order.length) {
          V.table(panel, ["added", "group"], state.order.map((g, i) => [String(i + 1), `{${g.join(", ")}}`]),
            (i) => (i === state.order.length - 1 ? "viz-hl" : ""));
        } else {
          html("div", { class: "viz-readout" }, panel, `groups: ${state.groups.map((g) => `{${g.join(",")}}`).join("  ")}`);
        }
        if (state.cut) html("div", { class: "viz-readout viz-badtext" }, panel, `cut of the phase: {${state.cut[0].join(", ")}} against the rest, weight ${num(state.cut[1])} (red edges)`);
        if (state.best) html("div", { class: "viz-readout viz-cert" }, panel, `best cut so far: {${state.best[1].join(", ")}}, weight ${num(state.best[0])}`);
        state.explain = state.order.length
          ? "Each phase grows an order: next is always the group most strongly attached to those already in (numbers beside the nodes). The last group's attachment is a minimum cut between the last two."
          : "Shaded bands join vertices merged into one group. Merging is safe: a cut that separates the two was just found, so what's left to find keeps them together.";
      },
    });
  });

  // ---------------------------------------------------------------- 09: polarity, with a draggable point
  //   data-shapes='[{"title":..., "rows":[[a1,a2],...]}]'  each row means a·x <= 1
  V.register("polar", (host) => {
    const shapes = JSON.parse(host.dataset.shapes);
    host.classList.add("viz-stack", "viz-ip");
    V.isolate(host);
    let shape = shapes[0], y = (host.dataset.y || "1.5,0.5").split(",").map(Number);
    matrixPicker(host, shapes, (i) => { shape = shapes[i]; draw(); });
    const body = html("div", { class: "viz-ip-cols" }, host);
    const W = 760, H = 380;
    const figBox = html("div", { class: "viz-polar-fig" }, body);
    const svg = V.newSvg(figBox, W, H, "a polygon P with a draggable point y, and its polar");
    const side = html("div", { class: "viz-right" }, body);
    const note = html("div", { class: "viz-note" }, side);
    const tableBox = html("div", {}, side);
    const expl = html("div", { class: "viz-explain" }, side);
    html("div", { class: "viz-hint" }, side, "Drag the point y on the left.");
    const box = [-2.2, 2.2, -2.2, 2.2];
    let PL = null;
    V.draggable(svg, (t) => t.classList.contains("viz-handle"), (sx, sy) => {
      const q = PL.inv(sx, sy);
      y = [Math.max(-2, Math.min(2, Math.round(q[0] * 10) / 10)), Math.max(-2, Math.min(2, Math.round(q[1] * 10) / 10))];
      draw();
    });
    function draw() {
      svg.replaceChildren();
      const gl = el("g", {}, svg), gr = el("g", { transform: `translate(${W / 2}, 0)` }, svg);
      const left = el("svg", { x: 0, y: 0, width: W / 2, height: H, viewBox: `0 0 ${W / 2} ${H}` }, gl);
      const right = el("svg", { x: 0, y: 0, width: W / 2, height: H, viewBox: `0 0 ${W / 2} ${H}` }, gr);
      left.dataset.vizId = svg.dataset.vizId + "l"; right.dataset.vizId = svg.dataset.vizId + "r";
      const A = shape.rows.map(([a, b]) => [a, b, 1]);
      PL = V.plot(left, box, W / 2, H, { step: [1, 1] });
      const PR = V.plot(right, box, W / 2, H, { step: [1, 1] });
      // P
      const regP = V.region(A, box);
      el("polygon", { points: V.polyPoints(PL, regP.poly), class: "viz-poly" }, left);
      el("polygon", { points: V.polyPoints(PL, regP.poly), class: "viz-outline" }, left);
      // P° = conv(rows): hull of the row vectors (and they are its vertices when P is irredundant)
      const hull = V.region(convexRows(shape.rows), box).poly;
      el("polygon", { points: V.polyPoints(PR, hull), class: "viz-poly" }, right);
      el("polygon", { points: V.polyPoints(PR, hull), class: "viz-outline" }, right);
      // separation by optimizing over P°: max a·y over its vertices
      const vals = shape.rows.map(([a, b]) => a * y[0] + b * y[1]);
      const bestI = vals.indexOf(Math.max(...vals)), bestV = vals[bestI], inside = bestV <= 1 + 1e-9;
      shape.rows.forEach(([a, b], i) => {
        const s = V.lineInBox([a, b, 1], box);
        const hot = i === bestI && !inside;
        if (s) el("line", { x1: PL.X(s[0][0]), y1: PL.Y(s[0][1]), x2: PL.X(s[1][0]), y2: PL.Y(s[1][1]), class: hot ? "viz-cut" : "viz-rowline" }, left);
        el("circle", { cx: PR.X(a), cy: PR.Y(b), r: hot ? 8 : 5, class: hot ? "viz-dot-warn" : "viz-vertex" }, right);
      });
      // y's own line in the polar picture: {a : a·y = 1}; the polar contains P° inside a·y <= 1 iff y ∈ P
      const ly = V.lineInBox([y[0], y[1], 1], box);
      if (ly && (y[0] || y[1])) el("line", { x1: PR.X(ly[0][0]), y1: PR.Y(ly[0][1]), x2: PR.X(ly[1][0]), y2: PR.Y(ly[1][1]), class: inside ? "viz-levelline" : "viz-cut" }, right);
      el("circle", { cx: PL.X(y[0]), cy: PL.Y(y[1]), r: 9, class: "viz-handle" + (inside ? "" : " viz-handle-warn") }, left);
      const rightSide = y[0] > 0.6;
      V.text(left, PL.X(y[0]) + (rightSide ? -12 : 12), PL.Y(y[1]) - 12, `y = (${num(y[0], 1)}, ${num(y[1], 1)})`, "viz-probe-text", rightSide ? "end" : "start");
      V.text(left, 12, 18, "P", "viz-label");
      V.text(right, 12, 18, "P° (vertices = the rows of P)", "viz-label", "start");
      PL.raise(); PR.raise();
      note.textContent = inside ? `max a·y over P° is ${num(bestV)} ≤ 1: y is in P` : `max a·y over P° is ${num(bestV)} > 1: y is outside P`;
      note.className = "viz-note " + (inside ? "viz-okline" : "viz-badline");
      tableBox.replaceChildren();
      V.table(tableBox, ["vertex a of P°", "a·y", "row of P"], shape.rows.map(([a, b], i) => [`(${minus(num(a))}, ${minus(num(b))})`, num(vals[i]), `${lin([a, b])} ≤ 1`]),
        (i) => (i === bestI ? (inside ? "viz-hl" : "viz-bad") : ""));
      expl.textContent = inside
        ? "Every vertex of P° scores at most 1 against y, so every row of P holds at y. The dashed line on the right, a·y = 1, has all of P° on one side."
        : "The best vertex of P° is a row of P that y violates (red on both sides). Finding it was an optimization over P°: that is the second direction of Grötschel, Lovász & Schrijver.";
    }
    // The hull of the row vectors, as rows [a, b, c] for V.region.
    function convexRows(pts) {
      const hull = convexHull(pts);
      const out = [];
      for (let i = 0; i < hull.length; i++) {
        const p = hull[i], q = hull[(i + 1) % hull.length];
        const a = q[1] - p[1], b = p[0] - q[0], c = a * p[0] + b * p[1];
        out.push([a, b, c]);   // counter-clockwise hull: (a, b) points outward, the inside has a·x <= c
      }
      return out;
    }
    function convexHull(pts) {
      const P = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
      const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
      const lower = [], upper = [];
      for (const p of P) { while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop(); lower.push(p); }
      for (const p of P.reverse()) { while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop(); upper.push(p); }
      return lower.slice(0, -1).concat(upper.slice(0, -1));
    }
    draw();
  });
})();
