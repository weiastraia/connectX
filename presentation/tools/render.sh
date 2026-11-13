#!/bin/sh
# Render the deck to JPG images for visual checks. usage: render.sh <skill pptx dir> <out dir>
set -e
SK="$1"; OUT="$2"
mkdir -p "$OUT" && rm -f "$OUT"/slide-*.jpg "$OUT"/*.pdf
cp presentation/ConnectX_week4.pptx "$OUT/deck.pptx"
(cd "$OUT" && python3 "$SK/scripts/office/soffice.py" --headless --convert-to pdf deck.pptx >/dev/null 2>&1 && pdftoppm -jpeg -r 110 deck.pdf slide)
ls "$OUT"
