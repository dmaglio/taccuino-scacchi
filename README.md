# Passo dopo passo — taccuino di scacchi a livelli

*Italian-language chess workbook for beginners who know the rules but have little practice. Builds a printable A4 PDF and an EPUB.*

Un taccuino da stampare (PDF) o da leggere su e-reader (EPUB) per chi conosce le regole degli scacchi ma ha poca pratica.

## Contenuto

- **Ripasso delle regole**: pezzi, mosse speciali, e **come si scrivono le mosse** (lettere italiane R, D, T, A, C), con esercizi.
- **Sette livelli**, 275 esercizi con soluzione, dal più facile al più difficile:
  1. Matto in una mossa (50) · 2. Matto in due mosse (40) · 3. Pezzi in presa (40) · 4. Forchette e inchiodature (55) · 5. Infilate e attacchi di scoperta (35) · 6. Finali (30) · 7. Le aperture (25 + quiz)
- Ogni livello ha una pagina di lezione, un riquadro per il punteggio e le soluzioni in fondo; in più il «taccuino degli errori».

## Come si costruisce

```sh
./build.sh          # -> build/taccuino.pdf e build/taccuino.epub
```

Servono `python3`, Google Chrome (per il PDF), `rsvg-convert`, ImageMagick e `pandoc` (per l'EPUB).
Gli esercizi scelti sono già in `data/selected.json`.

Per rigenerare la selezione dal database dei puzzle di Lichess:

```sh
curl -r 0-83886079 https://database.lichess.org/lichess_db_puzzle.csv.zst -o data/puzzles_part.zst
zstd -dc data/puzzles_part.zst > data/puzzles.csv     # l'ultimo record può essere troncato
.venv/bin/python src/select_puzzles.py
```

`src/verify_engine.py` controlla con Stockfish la prima mossa di ogni esercizio non-matto
(sull'ultima esecuzione: 185 controllati, nessun sospetto).

## Come sono verificati gli esercizi

- Ogni mossa della soluzione è legale e nei matti la posizione finale è davvero matto (`python-chess`).
- Nei matti in una mossa sono elencate tutte le mosse che danno matto.
- Gli esempi delle lezioni sono controllati dal programma (matti, forchette, inchiodature, stallo).

## Crediti e licenza

Gli esercizi provengono dal [database dei puzzle di Lichess](https://database.lichess.org/#puzzles), in pubblico dominio (CC0).
Il codice è sotto licenza **AGPL-3.0** (vedi `LICENSE`); i testi delle lezioni sono originali.
