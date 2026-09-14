#!/usr/bin/env bash
# Authoring check for one unit's deck, in headless Brave (or Chromium):
#   1. the deck's ?check=1 overflow test (deck-overflow.mjs)
#   2. every marked glossary term opens a definition; G, Esc and a slide link work
#   3. optional screenshots of chosen slides (reveal indices, 0-based)
#
#   slides/tools/deck-check.sh 01
#   slides/tools/deck-check.sh 01 4 7 10     # ... and screenshot slides 4, 7, 10 into $OUT
#
# Needs network (reveal and KaTeX come from cdnjs). Screenshots go to $OUT,
# default $TMPDIR/deck-check-<unit>. Keep that path short: the browser puts a unix
# socket in its profile directory, and a path over ~100 characters makes it exit silently.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
unit=$(ls -d "$ROOT"/units/"$(printf %s "$1" | sed 's/^\([0-9]\)$/0\1/')"* | head -1)
shift
BROWSER=$(command -v brave || command -v chromium || command -v google-chrome-stable)
OUT=${OUT:-${TMPDIR:-/tmp}/deck-check-$(basename "$unit")}
mkdir -p "$OUT"
url="file://$unit/slides.html"

(cd "$ROOT" && ./co glossary "$(basename "$unit" | cut -d- -f1)" >/dev/null)

echo "== overflow"
timeout 150 node "$ROOT/slides/tools/deck-overflow.mjs" "$url" "$OUT" "$BROWSER" || echo "no report: the deck did not finish loading"

echo "== terms and keys"
timeout 150 node "$ROOT/slides/tools/deck-click.mjs" "$url" "$OUT" "$BROWSER"

for i in "$@"; do
  timeout 60 "$BROWSER" --headless=new --disable-gpu --user-data-dir="$OUT/profile" --hide-scrollbars \
    --window-size=1400,830 --virtual-time-budget=20000 --screenshot="$OUT/slide-$i.png" "$url#/$i" >/dev/null 2>&1
  echo "screenshot $OUT/slide-$i.png"
done
