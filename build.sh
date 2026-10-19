#!/bin/sh
# Genera build/taccuino.pdf e build/taccuino.epub dagli esercizi in data/selected.json.
# Richiede: python3, google-chrome (PDF), rsvg-convert + ImageMagick + pandoc (EPUB).
set -e
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip -q install -r requirements.txt; }
.venv/bin/python src/build.py
google-chrome --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=build/taccuino.pdf build/taccuino.html
.venv/bin/python src/epub.py
