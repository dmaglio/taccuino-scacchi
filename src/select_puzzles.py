"""Sceglie gli esercizi dal database aperto di Lichess (CC0) e li verifica."""
import csv, json, random, sys
import chess

random.seed(2026)
SRC = "data/puzzles.csv"

# (id livello, tema richiesto, altri temi vietati, rating min, rating max, quanti)
PLAN = [
    (1, "mateIn1", set(), 500, 1100, 50),
    (2, "mateIn2", set(), 700, 1300, 40),
    (3, "hangingPiece", {"mate", "mateIn1", "mateIn2"}, 600, 1300, 40),
    (4, "fork", {"mate", "mateIn1", "mateIn2"}, 800, 1400, 30),
    (4, "pin", {"mate", "mateIn1", "mateIn2"}, 900, 1500, 25),
    (5, "skewer", {"mate", "mateIn1", "mateIn2"}, 800, 1500, 15),
    (5, "discoveredAttack", {"mate", "mateIn1", "mateIn2"}, 900, 1500, 20),
    (6, "endgame", {"mate", "mateIn1", "mateIn2"}, 700, 1400, 30),
    (7, "opening", set(), 600, 1300, 25),
]

def good(r, need, ban, lo, hi):
    rating = int(r["Rating"])
    if not lo <= rating <= hi or int(r["Popularity"]) < 92 or int(r["RatingDeviation"]) > 90:
        return False
    th = set(r["Themes"].split())
    if need not in th or th & ban:
        return False
    n = len(r["Moves"].split())
    if need == "mateIn1":
        return n == 2
    if need == "mateIn2":
        return n == 4
    if need == "endgame" and "short" not in th:
        return False
    return 3 <= n <= 6

def build(r):
    board = chess.Board(r["FEN"])
    mv = [chess.Move.from_uci(m) for m in r["Moves"].split()]
    board.push(mv[0])
    last = mv[0]
    start = board.copy()
    sol = []
    for m in mv[1:]:
        assert m in board.legal_moves, r["PuzzleId"]
        sol.append(board.san(m)); board.push(m)
    kind = r["Themes"].split()
    if "mateIn1" in kind or "mateIn2" in kind:
        assert board.is_checkmate(), r["PuzzleId"]
    alts = None
    if "mateIn1" in kind:     # tutte le mosse che danno matto
        alts = []
        for m in start.legal_moves:
            start.push(m)
            if start.is_checkmate():
                start.pop(); alts.append(start.san(m)); start.push(m)
            start.pop()
        assert sol[0] in alts
        sol = alts
    return dict(id=r["PuzzleId"], fen=start.fen(), last=last.uci(), sol=sol,
                alts=bool(alts), rating=int(r["Rating"]), turn="w" if start.turn else "b",
                fullmove=start.fullmove_number)

rows = list(csv.DictReader(open(SRC)))
random.shuffle(rows)
out = {}
used = set()
for lvl, need, ban, lo, hi, n in PLAN:
    pool = [r for r in rows if r["PuzzleId"] not in used and good(r, need, ban, lo, hi)]
    pick = pool[:n]
    assert len(pick) == n, (need, len(pool))
    used |= {r["PuzzleId"] for r in pick}
    items = sorted((build(r) for r in pick), key=lambda x: x["rating"])
    for it in items: it["theme"] = need
    out.setdefault(lvl, []).extend(items)
for lvl in out:   # nel livello: prima un tema, poi l'altro, ciascuno dal facile al difficile
    pass
json.dump(out, open("data/selected.json", "w"), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in out.items()}, sum(len(v) for v in out.values()))
