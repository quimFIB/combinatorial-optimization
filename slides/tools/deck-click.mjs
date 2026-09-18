// Drive a deck in a headless browser over the DevTools protocol (node >= 22 for WebSocket):
// open every marked term's popover, check every ref resolves, follow one slide link, check G and Esc.
// Called by deck-check.sh; prints a JSON report and exits 1 if anything failed.
import { spawn } from "node:child_process";

const [url, outdir, browserBin] = process.argv.slice(2);
const port = 9300 + Math.floor(Math.random() * 500);
const browser = spawn(browserBin, ["--headless=new", "--disable-gpu", `--remote-debugging-port=${port}`,
  `--user-data-dir=${outdir}/cdp-profile`, "--window-size=1400,830", "about:blank"], { stdio: "ignore" });
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
ws.addEventListener("message", (m) => {
  const d = JSON.parse(m.data);
  if (pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
});
const send = (method, params = {}) => new Promise((r) => {
  const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params }));
});
const ev = async (expr) =>
  (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result.result.value;
const key = async (k, code, vk) => {
  for (const type of ["keyDown", "keyUp"])
    await send("Input.dispatchKeyEvent", { type, key: k, code, windowsVirtualKeyCode: vk, text: type === "keyDown" && k.length === 1 ? k : undefined });
};

await send("Page.enable");
await send("Page.navigate", { url });
for (let i = 0; i < 80 && !(await ev("!!(window.Reveal && Reveal.isReady() && window.GLOSSARY)")); i++) await sleep(250);

const report = { glossaryEntries: await ev("(window.GLOSSARY || []).length") };

// Every marked term, on every slide, must open a popover with a real entry.
report.unresolved = await ev(`(async () => {
  const bad = [];
  const slides = Reveal.getSlides();
  for (let i = 0; i < slides.length; i++) {
    Reveal.slide(i);
    for (const t of slides[i].querySelectorAll('.term')) {
      t.click();
      await new Promise((r) => setTimeout(r, 20));
      const pop = document.querySelector('.gl-pop');
      if (!pop || !pop.querySelector('.gl-term')) bad.push([i, t.dataset.term]);
      document.body.click();
    }
  }
  return bad;
})()`);
report.termsChecked = await ev("document.querySelectorAll('.reveal .term').length");

// One slide link, from a term whose entry lives on a different slide.
report.jump = await ev(`(async () => {
  const slides = Reveal.getSlides();
  for (let i = 0; i < slides.length; i++) {
    Reveal.slide(i);
    for (const t of slides[i].querySelectorAll('.term')) {
      t.click();
      await new Promise((r) => setTimeout(r, 20));
      const go = document.querySelector('.gl-pop .gl-go');
      const want = go && go.textContent.replace(/^slide: /, '').replace(/ →$/, '');
      const here = slides[i].querySelector('h2')?.textContent;
      if (go && want !== here) {
        go.click();
        await new Promise((r) => setTimeout(r, 100));
        const got = Reveal.getCurrentSlide().querySelector('h2')?.textContent;
        return { from: here, want, got, ok: got === want };
      }
      document.body.click();
    }
  }
  return { ok: true, note: 'no cross-slide link to test' };
})()`);

// Every <span class="ref"> must name a template in the deck's registry, and clicking one
// must show a card with that template's content.
report.refs = await ev(`(async () => {
  const names = new Set([...document.querySelectorAll('.refs template[data-ref]')].map((t) => t.dataset.ref));
  const refs = [...document.querySelectorAll('.reveal .ref')];
  const missing = [...new Set(refs.map((r) => r.dataset.ref).filter((n) => !names.has(n)))];
  const unused = [...names].filter((n) => !refs.some((r) => r.dataset.ref === n));
  let opens = null;
  if (refs.length) {
    const r = refs[0], i = Reveal.getSlides().indexOf(r.closest('.slides > section'));
    Reveal.slide(i);
    await new Promise((res) => setTimeout(res, 50));
    r.click();
    await new Promise((res) => setTimeout(res, 20));
    const card = document.querySelector('.ref-card');
    opens = !!card && card.dataset.for === r.dataset.ref && !/No reference/.test(card.textContent);
    document.body.click();
  }
  return { count: refs.length, missing, unused, opens };
})()`);

await ev("Reveal.slide(1)");
await sleep(200);
await key("g", "KeyG", 71);
await sleep(400);
report.gIndex = await ev("({open: !!document.querySelector('.gl-index'), emptyFilter: document.querySelector('.gl-index input')?.value === ''})");
await key("Escape", "Escape", 27);
await sleep(200);
report.escape = await ev("({closed: !document.querySelector('.gl-index'), noOverview: !Reveal.isOverview()})");

const ok = report.glossaryEntries > 0 && report.unresolved.length === 0 && report.jump.ok &&
  report.refs.missing.length === 0 && report.refs.opens !== false &&
  report.gIndex.open && report.gIndex.emptyFilter && report.escape.closed && report.escape.noOverview;
done(ok ? 0 : 1, { ok, ...report });
