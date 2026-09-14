// Shared boot for every unit's slides.
//
// Keys, in addition to reveal's own (arrows, Esc for overview, F fullscreen):
//   N   show / hide the notes panel beside the slide (remembered)
//   R   reading mode: every slide stacked in one page, notes beside each
//   D   toggle dark / light
//
// (No speaker-window plugin: reveal 5.1.0's notes plugin from cdnjs throws on
// load and aborts initialisation. N and R cover the same need.)
//
// URL switches, handy for bookmarks and screenshots: ?view=read, ?notes=1.
//
// Math is written as $...$ inline and $$...$$ display; KaTeX renders it once,
// before reveal lays the slides out, so slide sizes are measured correctly.

(function () {
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (_) { /* private mode */ } },
  };

  const params = new URLSearchParams(location.search);
  const reading = params.get("view") === "read";

  const theme = store.get("co-theme");
  if (theme) document.documentElement.setAttribute("data-theme", theme);

  function renderMath() {
    if (!window.renderMathInElement) return;
    renderMathInElement(document.querySelector(".reveal"), {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
      ],
      ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
      throwOnError: false,
    });
  }

  function toggleDark() {
    const root = document.documentElement;
    const dark = root.getAttribute("data-theme") === "dark" ||
      (!root.hasAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    const next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    store.set("co-theme", next);
  }

  function toggleReading() {
    const url = new URL(location.href);
    if (reading) url.searchParams.delete("view"); else url.searchParams.set("view", "read");
    url.hash = "";
    location.href = url.toString();
  }

  function help(text) {
    const el = document.createElement("div");
    el.className = "deck-help";
    el.innerHTML = text;
    document.body.appendChild(el);
  }

  renderMath();

  // ---------------------------------------------------------------- reading
  if (reading) {
    document.body.classList.add("reading");
    const slides = document.querySelector(".reveal .slides");
    let n = 0;
    for (const section of Array.from(slides.children)) {
      if (section.tagName !== "SECTION") continue;
      n += 1;
      const wrap = document.createElement("article");
      wrap.className = "read-slide";
      wrap.id = "s" + n;
      const frame = document.createElement("div");
      frame.className = "read-frame";
      const notes = section.querySelector(":scope > aside.notes");
      section.parentNode.insertBefore(wrap, section);
      frame.appendChild(section);
      wrap.appendChild(frame);
      const side = document.createElement("div");
      side.className = "read-notes";
      side.innerHTML = `<a class="read-no" href="#s${n}">${n}</a>`;
      if (notes) side.appendChild(notes);
      wrap.appendChild(side);
    }
    if (window.RevealHighlight) {
      const hl = RevealHighlight();
      if (hl.hljs) document.querySelectorAll("pre code").forEach((el) => hl.hljs.highlightElement(el));
    }
    help("<kbd>R</kbd> back to slides &nbsp; <kbd>D</kbd> dark");
    document.addEventListener("keydown", (e) => {
      if (e.target.closest("input, textarea")) return;
      if (e.key === "r" || e.key === "R") toggleReading();
      if (e.key === "d" || e.key === "D") toggleDark();
    });
    return;
  }

  // ---------------------------------------------------------------- slides
  help("<kbd>N</kbd> notes &nbsp; <kbd>R</kbd> reading mode &nbsp; " +
    "<kbd>D</kbd> dark &nbsp; <kbd>Esc</kbd> overview");

  Reveal.initialize({
    hash: true,
    width: 1280,
    height: 760,
    margin: 0.05,
    center: false,
    slideNumber: "c/t",
    transition: "none",
    backgroundTransition: "none",
    showNotes: params.get("notes") === "1" || store.get("co-notes") === "1",
    pdfSeparateFragments: false,
    plugins: [RevealHighlight],
    keyboard: {
      78: () => {                                   // N
        const on = !Reveal.getConfig().showNotes;
        Reveal.configure({ showNotes: on });
        store.set("co-notes", on ? "1" : "0");
      },
      82: toggleReading,                            // R
      68: toggleDark,                               // D
    },
  });

  // ?check=1 — an authoring aid: visit every slide, then cover the page with a list of
  // equations wider than their column and slides taller than the frame.
  if (params.get("check") === "1") {
    Reveal.on("ready", () => {
      const problems = [];
      Reveal.getSlides().forEach((section, i) => {
        Reveal.slide(i);
        section.querySelectorAll(".katex-display").forEach((el) => {
          if (el.scrollWidth > el.clientWidth + 1)
            problems.push(`slide ${i + 1}: equation ${el.scrollWidth}px in ${el.clientWidth}px`);
        });
        section.querySelectorAll(".cols > *, pre, table").forEach((el) => {
          if (el.scrollWidth > el.clientWidth + 4 && !el.closest(".katex-display"))
            problems.push(`slide ${i + 1}: ${el.tagName.toLowerCase()} ${el.scrollWidth}px in ${el.clientWidth}px`);
        });
        if (!section.classList.contains("divider") && section.scrollHeight > Reveal.getConfig().height + 1)
          problems.push(`slide ${i + 1}: content ${section.scrollHeight}px tall`);
      });
      Reveal.slide(0);
      const report = document.createElement("pre");
      report.className = "deck-check";
      report.textContent = problems.length ? problems.join("\n") : "no overflow";
      report.style.cssText = "position:fixed;inset:0;z-index:99;margin:0;padding:40px;" +
        "background:#fff;color:#000;font:20px/1.5 monospace";
      document.body.appendChild(report);
    });
  }
})();
