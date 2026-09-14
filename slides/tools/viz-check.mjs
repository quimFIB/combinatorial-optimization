// Check a unit's explore.html in a headless browser over the DevTools protocol (node >= 22):
//   * the deck's overflow test (as ?check=1 does), on every slide;
//   * every .viz figure rendered without a .viz-error box;
//   * every stepper can be stepped to its last state and back, in every run it offers;
//   * every slider can be moved to both ends, every checkbox toggled twice;
//   * no uncaught exception on the page at any point;
//   * keys pressed inside a figure never change the slide.
// Prints a JSON report and exits 1 if anything failed. Called by viz-check.sh.
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";

const [url, outdir, browserBin] = process.argv.slice(2);
const port = 9500 + Math.floor(Math.random() * 400);
const browser = spawn(browserBin, ["--headless=new", "--disable-gpu", `--remote-debugging-port=${port}`,
  `--user-data-dir=${outdir}/viz-profile`, "--window-size=1400,830", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const done = (code, report) => { console.log(JSON.stringify(report, null, 1)); browser.kill(); process.exit(code); };

let targets;
for (let i = 0; i < 60 && !targets; i++) {
  try { targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch { await sleep(250); }
}
const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const pending = new Map();
const exceptions = [];
ws.addEventListener("message", (m) => {
  const d = JSON.parse(m.data);
  if (d.method === "Runtime.exceptionThrown") exceptions.push(d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text);
  if (pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
});
const send = (method, params = {}) => new Promise((r) => {
  const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params }));
});
const ev = async (expr) => {
  const res = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
  if (res.result.exceptionDetails) throw new Error(res.result.exceptionDetails.exception?.description || "evaluate failed");
  return res.result.result.value;
};

await send("Runtime.enable");
await send("Page.enable");
await send("Page.navigate", { url });
for (let i = 0; i < 80 && !(await ev("!!(window.Reveal && Reveal.isReady() && window.CoViz && document.querySelector('.viz[data-viz-ready]'))")); i++) await sleep(250);
await sleep(800);

const report = await ev(`(async () => {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const out = { slides: Reveal.getSlides().length, figures: [], overflow: [] };
  const slides = Reveal.getSlides();
  for (let i = 0; i < slides.length; i++) {
    const section = slides[i];
    Reveal.slide(i); await wait(150);
    section.querySelectorAll(".katex-display").forEach((el) => { if (el.scrollWidth > el.clientWidth + 1) out.overflow.push("slide " + i + ": equation"); });
    if (!section.classList.contains("divider") && section.scrollHeight > Reveal.getConfig().height + 1)
      out.overflow.push("slide " + i + ": content " + section.scrollHeight + "px tall");
    for (const host of section.querySelectorAll(".viz[data-viz]")) {
      const f = { slide: i, widget: host.dataset.viz, ok: true, checks: [] };
      const err = host.querySelector(".viz-error");
      if (err) { f.ok = false; f.checks.push("error box: " + err.textContent); out.figures.push(f); continue; }
      if (!host.querySelector("svg, canvas, table")) { f.ok = false; f.checks.push("nothing drawn"); }
      // steppers: every run, to the end and back
      const next = host.querySelector(".viz-next");
      if (next) {
        const pick = host.querySelector(".viz-pick");
        const runs = pick ? pick.options.length : 1;
        for (let r = 0; r < runs; r++) {
          if (pick) { pick.value = String(r); pick.dispatchEvent(new Event("change")); await wait(30); }
          let steps = 0;
          while (!next.disabled && steps < 5000) { next.click(); steps++; if (steps % 25 === 0) await wait(0); }
          const prev = host.querySelector(".viz-controls button[title^='back (']");
          let back = 0;
          while (prev && !prev.disabled && back < 5000) { prev.click(); back++; }
          if (host.querySelector(".viz-error")) { f.ok = false; f.checks.push("run " + r + ": error after stepping"); break; }
          f.checks.push("run " + r + ": " + (steps + 1) + " states");
        }
      }
      for (const s of host.querySelectorAll("input[type=range]")) {
        for (const v of [s.min, s.max, s.defaultValue]) { s.value = v; s.dispatchEvent(new Event("input", { bubbles: true })); await wait(10); }
        f.checks.push("slider moved");
      }
      for (const c of host.querySelectorAll("input[type=checkbox]")) { c.click(); await wait(5); c.click(); await wait(5); }
      const h = Reveal.getIndices().h;
      host.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
      await wait(30);
      if (Reveal.getIndices().h !== h) { f.ok = false; f.checks.push("a key inside the figure changed the slide"); }
      if (host.querySelector(".viz-error")) { f.ok = false; f.checks.push("error box after interaction"); }
      out.figures.push(f);
    }
  }
  Reveal.slide(0);
  return out;
})()`);

// screenshots of every figure slide, for a human to look at
const figureSlides = [...new Set(report.figures.map((f) => f.slide))];
for (const s of figureSlides) {
  await ev(`Reveal.slide(${s})`);
  await sleep(300);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(`${outdir}/explore-slide-${s}.png`, Buffer.from(shot.result.data, "base64"));
}

report.exceptions = exceptions;
report.ok = report.figures.length > 0 && report.figures.every((f) => f.ok) && !report.overflow.length && !exceptions.length;
report.screenshots = figureSlides.map((s) => `${outdir}/explore-slide-${s}.png`);
done(report.ok ? 0 : 1, report);
