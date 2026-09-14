# Interactive figures

Optional support material: each unit can have an `explore.html`, a short companion deck
of interactive figures. The slides never depend on it. A deck links to it only through a
small muted chip (`▸ explore interactively`) in the top-right corner of the slides a
figure supports, opening in a new tab, plus one sentence in the deck's "getting around"
box. Skipping every figure costs a learner nothing.

```fish
uv run co explore 02                 # open unit 02's figures (rebuilds its data first)
uv run co viz [02]                   # rebuild viz-data.js for one unit or all
slides/tools/viz-check.sh 02         # check the figures (see below)
```

## Pieces

| File | Role |
|---|---|
| `slides/viz/viz.js` | Core: DOM and number helpers, 2-D geometry, `plot`, `graph`, `table`, `slider`, `draggable`, and the `stepper` shell for replaying recorded states |
| `slides/viz/viz.css` | Styles for all figures, from deck.css's colour tokens (dark mode follows) |
| `slides/viz/widgets/*.js` | One file per family of figures, each calling `CoViz.register(name, build)` |
| `slides/viz/traces/uNN.py` | `data()` for unit NN, computed with the unit's reference solution or `colib`; `co viz` writes it to `units/NN-*/viz-data.js` |
| `slides/viz/explore-template.html` | Starting point for a unit's `explore.html` |
| `slides/viz/add_links.py` | Adds the chips to a deck: `add_links.py 02 "Slide title=1" …` |
| `slides/tools/viz-check.sh`, `viz-check.mjs` | Headless check of an explore page |
| `deck.css` `.viz-link` | The chip's style, the only figure style the decks themselves load |

## Rules

1. **Numbers come from running code.** Geometry is computed in the page from data written
   in the HTML (rows, points, weights); algorithm runs are recorded by
   `traces/uNN.py` from the unit's reference solution. Nothing on a figure is typed in by
   hand, so a figure cannot disagree with the slides.
2. **Classic scripts only.** Pages open from `file://`, which blocks ES modules and
   `fetch()` of sibling files. Data travels as `viz-data.js` setting `window.VIZ_DATA`,
   like `glossary.js`. No libraries beyond what the decks already load.
3. **Figures own their input.** Wrap every host with `CoViz.isolate`, so drags and arrow
   keys inside it never move the slides. Own drags on the svg with `CoViz.draggable`, never
   on an element that gets redrawn (the pilot's arrow died after one pixel that way).
4. **Fail visibly.** A builder that cannot work calls `CoViz.fail(host, reason)`; the check
   looks for the resulting `.viz-error`.
5. **Small and focused.** One to three figures per unit, each answering one question the
   slides raise. Every figure slide says in one line what to try, and its notes say what the
   figure shows and where its data comes from.
6. **No math in labels or in the chip.** Box labels are upper-cased, which turns `x` into `X`.

## The check

`slides/tools/viz-check.sh NN` rebuilds the unit's glossary and viz data, then, in headless
Brave or Chromium: runs the overflow test on every slide of `explore.html`; confirms each
figure drew something and shows no `.viz-error`; steps every stepper through every run to
the end and back; moves every slider to both ends and toggles every checkbox; presses an
arrow key inside each figure and confirms the slide didn't change; and fails on any
uncaught exception. It writes one screenshot per figure slide to `$OUT`; look at them.
After adding chips to a deck, run the deck's own check as well (`slides/tools/deck-check.sh`).
