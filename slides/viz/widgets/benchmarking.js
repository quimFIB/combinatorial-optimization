// Reading benchmark results (unit 28): a performance profile whose solvers can be switched off,
// and a bootstrap interval that settles as resamples are added. Needs slides/viz/viz.js and
// viz-data.js (slides/viz/traces/u28.py).
(function () {
  "use strict";
  const V = window.CoViz;
  const { el, html, num } = V;

  // ---------------------------------------------------------------- performance profile
  V.register("perfprofile", (host) => {
    const d = V.data(host, "profile");
    if (!d) return;
    host.classList.add("viz-profile");
    V.isolate(host);
    const on = Object.fromEntries(d.solvers.map((s) => [s, true]));
    const left = html("div", { class: "viz-left" }, host);
    const toggles = html("div", { class: "viz-bm-toggles" }, left);
    const boxes = d.solvers.map((s, i) => {
      const lab = html("label", { class: `viz-bm-toggle c${i}` }, toggles);
      const cb = html("input", { type: "checkbox" }, lab);
      cb.checked = true;
      html("span", {}, lab, `solver ${s}`);
      cb.addEventListener("change", () => {
        if (!d.solvers.some((t) => (t === s ? cb.checked : on[t]))) { cb.checked = true; return; }  // keep at least one
        on[s] = cb.checked; draw();
      });
      return cb;
    });
    const W = 520, H = 330;
    const svg = V.newSvg(left, W, H, "performance profile: share of instances within a factor tau of the best");
    const right = html("div", { class: "viz-right" }, host);
    const note = html("div", { class: "viz-note" }, right);
    const tableHost = html("div", {}, right);
    const explain = html("div", { class: "viz-explain" }, right);
    const full = d.subsets[d.solvers.join("")];

    function draw() {
      const sub = d.solvers.filter((s) => on[s]);
      const res = d.subsets[sub.join("")];
      svg.replaceChildren();
      const P = V.plot(svg, [1, 4, 0, 1], W, H, { aspect: "fill", step: [0.5, 0.25], pad: 40 });
      V.text(svg, W / 2, H - 6, "τ: within this factor of the fastest", "viz-label-soft");
      V.text(svg, 12, 20, "share of instances", "viz-label-soft", "start");
      sub.forEach((s) => {
        const idx = d.solvers.indexOf(s), ys = res.profile[s];
        const pts = [];
        d.taus.forEach((t, k) => {
          if (k > 0) pts.push([t, ys[k - 1]]);
          pts.push([t, ys[k]]);
        });
        const off = (idx - 1) * 0.008;   // nudge overlapping curves apart
        el("polyline", { points: pts.map(([t, y]) => `${P.X(t)},${P.Y(y + off)}`).join(" "), class: `viz-bm-curve c${idx}` }, svg);
        V.text(svg, P.X(4) - 4, P.Y(ys[ys.length - 1] + off) - 6, s, `viz-bm-label c${idx}`, "end");
      });
      P.raise();

      const inf = (r) => (r === null ? "fail" : num(r));
      const header = ["", ...d.instances, "share at τ = 1"];
      const rows = sub.map((s) => [`solver ${s}`, ...res.ratios[s].map(inf), num(res.profile[s][0])]);
      rows.push(["fastest", ...d.instances.map((i) => res.best[i].solver ? `${res.best[i].solver} (${num(res.best[i].seconds)} s)` : "none"), ""]);
      tableHost.replaceChildren();
      V.table(tableHost, header, rows, (i, j, v) => {
        if (i === rows.length - 1) return "viz-soft";
        if (i < 0 || j === 0) return "";
        if (v === "fail") return "viz-bad";
        const s = sub[i];
        const was = j <= d.instances.length ? full.ratios[s][j - 1] : full.profile[s][0];
        const now = j <= d.instances.length ? res.ratios[s][j - 1] : res.profile[s][0];
        return sub.length < d.solvers.length && was !== now ? "viz-hl" : "";
      });
      note.textContent = sub.length === d.solvers.length ? "all three solvers: ratios to the fastest on each instance"
        : `without ${d.solvers.filter((s) => !on[s]).join(" and ")}: highlighted cells changed, though those solvers ran nothing new`;
      explain.textContent = sub.length === d.solvers.length
        ? "Each curve steps up at a solver's ratios; failures never count. X and Y both reach 0.5 at τ = 1 because they tie on p3. Switch a solver off and watch the others' curves move."
        : "A profile measures every solver against the fastest one present. Remove a solver and the fastest changes on the instances it won, so everyone else's ratios, and curves, change with it.";
    }
    draw();
  });

  // ---------------------------------------------------------------- bootstrap
  V.register("bootstrap", (host) => {
    const d = V.data(host, "bootstrap");
    if (!d) return;
    host.classList.add("viz-bootstrap");
    V.isolate(host);
    const left = html("div", { class: "viz-left" }, host);
    const W = 520, H = 320;
    const svg = V.newSvg(left, W, H, "histogram of bootstrap means with the percentile interval");
    let n = d.counts[0];
    V.slider(left, { label: "resamples", min: 0, max: d.counts.length - 1, step: 1, value: 0, format: (i) => String(d.counts[i]) },
      (i) => { n = d.counts[i]; draw(); });
    const right = html("div", { class: "viz-right" }, host);
    const big = html("div", { class: "viz-big" }, right);
    const sub = html("div", { class: "viz-readout" }, right);
    html("div", { class: "viz-head" }, right, "the first resamples, drawn with replacement");
    const tableHost = html("div", {}, right);
    const explain = html("div", { class: "viz-explain" }, right);

    function draw() {
      const means = d.means.slice(0, n);
      const [lo, hi] = d.intervals[String(n)];
      svg.replaceChildren();
      const width = 0.02, x0 = 0.6, x1 = 1.1;
      const bins = new Array(Math.round((x1 - x0) / width) + 1).fill(0);
      means.forEach((m) => { bins[Math.min(bins.length - 1, Math.max(0, Math.round((m - x0) / width)))] += 1; });
      const top = Math.max(...bins) / n;
      const P = V.plot(svg, [x0 - width, x1 + width, 0, Math.max(top * 1.15, 0.05)], W, H, { aspect: "fill", step: [0.1, V.niceStep(Math.max(top * 1.15, 0.05), 4)], pad: 40 });
      el("rect", { x: P.X(lo), y: P.Y(Math.max(top * 1.15, 0.05)), width: P.X(hi) - P.X(lo), height: P.Y(0) - P.Y(Math.max(top * 1.15, 0.05)), class: "viz-bm-band" }, svg);
      bins.forEach((c, k) => {
        if (!c) return;
        const cx = x0 + k * width, h = c / n;
        el("rect", { x: P.X(cx - width * 0.45), y: P.Y(h), width: P.X(cx + width * 0.45) - P.X(cx - width * 0.45), height: P.Y(0) - P.Y(h), class: "viz-bm-bar" }, svg);
      });
      el("line", { x1: P.X(d.mean), y1: P.Y(0), x2: P.X(d.mean), y2: 30, class: "viz-levelline" }, svg);
      V.text(svg, P.X(d.mean), 24, `sample mean ${num(d.mean)}`, "viz-label");
      V.text(svg, 14, 20, "share of resamples", "viz-label-soft", "start");
      V.text(svg, W / 2, H - 6, "mean of a resample", "viz-label-soft");
      P.raise();

      big.textContent = `95% interval [${num(lo)}, ${num(hi)}]`;
      sub.textContent = `from ${n} resample means; shaded on the left. With all ${d.counts[d.counts.length - 1]}: [${num(d.intervals[String(d.counts[d.counts.length - 1])][0])}, ${num(d.intervals[String(d.counts[d.counts.length - 1])][1])}]`;
      tableHost.replaceChildren();
      V.table(tableHost, ["resample", "mean"], d.first.slice(0, Math.min(n, 5)).map((r) => [r.map((v) => num(v)).join(", "), num(r.reduce((a, b) => a + b, 0) / r.length)]));
      explain.textContent = n < 100
        ? "With few resamples the interval is just the extreme means drawn so far, and it keeps moving as more arrive."
        : "Past a few hundred resamples the interval barely moves: its width now reflects the five data points, not the number of resamples. More resamples cannot shrink it; more instances can.";
    }
    draw();
  });
})();
