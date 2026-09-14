// The deck's ?check=1 overflow test, run over the DevTools protocol (node >= 22). Used by
// deck-check.sh: --dump-dom returned before the report was attached, so it reported nothing.
// Prints "no overflow" or one line per problem (slide indices are 0-based).
import { spawn } from "node:child_process";
const [url, outdir, browserBin] = process.argv.slice(2);
const port = 9800 + Math.floor(Math.random() * 150);
const browser = spawn(browserBin, ["--headless=new", "--disable-gpu", `--remote-debugging-port=${port}`,
  `--user-data-dir=${outdir}/ov-profile`, "--window-size=1600,1000", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets;
for (let i = 0; i < 60 && !targets; i++) { try { targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch { await sleep(250); } }
const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pending = new Map();
ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } });
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr) => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result.result.value;
await send("Page.enable"); await send("Page.navigate", { url });
for (let i = 0; i < 80 && !(await ev("!!(window.Reveal && Reveal.isReady() && window.renderMathInElement && document.querySelector('.katex'))")); i++) await sleep(250);
await sleep(1500);
console.log(await ev(`(async () => { const problems = [];
  const slides = Reveal.getSlides();
  for (let i = 0; i < slides.length; i++) { const section = slides[i]; Reveal.slide(i); await new Promise(r => setTimeout(r, 60));
    section.querySelectorAll(".katex-display").forEach((el) => { if (el.scrollWidth > el.clientWidth + 1) problems.push("slide " + i + ": equation " + el.scrollWidth + " in " + el.clientWidth); });
    section.querySelectorAll(".cols > *, pre, table").forEach((el) => { if (el.scrollWidth > el.clientWidth + 4 && !el.closest(".katex-display")) problems.push("slide " + i + ": " + el.tagName.toLowerCase() + " " + el.scrollWidth + " in " + el.clientWidth); });
    if (!section.classList.contains("divider") && section.scrollHeight > Reveal.getConfig().height + 1) problems.push("slide " + i + ": content " + section.scrollHeight + "px tall (frame " + Reveal.getConfig().height + ")");
  }
  return problems.length ? problems.join("\\n") : "no overflow"; })()`));
browser.kill(); process.exit(0);
