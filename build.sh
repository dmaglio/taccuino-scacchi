#!/bin/sh
# Genera build/taccuino.pdf (A4), build/taccuino-a5.pdf (A5) e, per spillarlo, due fascicoli A5
# (taccuino-a5-p1.pdf e -p2.pdf) con i relativi libretti (taccuino-a5-p1-book.pdf e -p2-book.pdf,
# 2 pagine A5 per facciata A4), piu' build/taccuino.epub, dagli esercizi in data/selected.json.
# Richiede: python3, google-chrome (PDF), pdfbook2 (libretti), rsvg-convert + ImageMagick + pandoc (EPUB).
set -e
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip -q install -r requirements.txt; }
.venv/bin/python src/build.py
google-chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=build/taccuino.pdf build/taccuino.html
.venv/bin/python src/build.py --a5
google-chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=build/taccuino-a5.pdf build/taccuino-a5.html
for part in 1 2; do
  .venv/bin/python src/build.py --a5 --part=$part
  google-chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=build/taccuino-a5-p$part.pdf build/taccuino-a5-p$part.html
  pdfbook2 --no-crop --paper=a4paper build/taccuino-a5-p$part.pdf
done
.venv/bin/python src/epub.py
