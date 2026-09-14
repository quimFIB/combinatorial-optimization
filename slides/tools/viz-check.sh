#!/usr/bin/env bash
# Authoring check for a unit's optional interactive figures (explore.html), in headless Brave
# or Chromium. Rebuilds the unit's glossary.js and viz-data.js, then runs viz-check.mjs:
# overflow, every figure renders, every stepper steps through, no exceptions, and one
# screenshot per figure slide in $OUT (default $TMPDIR/viz-check-<unit>; keep it short).
#
#   slides/tools/viz-check.sh 02
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
unit=$(ls -d "$ROOT"/units/"$(printf %s "$1" | sed 's/^\([0-9]\)$/0\1/')"* | head -1)
BROWSER=$(command -v brave || command -v chromium || command -v google-chrome-stable)
OUT=${OUT:-${TMPDIR:-/tmp}/viz-check-$(basename "$unit" | cut -d- -f1)}
rm -rf "$OUT"; mkdir -p "$OUT"
key=$(basename "$unit" | cut -d- -f1)
(cd "$ROOT" && ./co glossary "$key" >/dev/null && ./co viz "$key" >/dev/null)
[ -f "$unit/explore.html" ] || { echo "no explore.html in $(basename "$unit")"; exit 1; }
timeout 300 node "$ROOT/slides/tools/viz-check.mjs" "file://$unit/explore.html" "$OUT" "$BROWSER"
