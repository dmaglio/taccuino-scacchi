"""Controlla con Stockfish la prima mossa di ogni esercizio non-matto."""
import json, chess, chess.engine
D = json.load(open("data/selected.json"))
eng = chess.engine.SimpleEngine.popen_uci("stockfish")
eng.configure({"Threads": 4, "Hash": 256})
lim = chess.engine.Limit(depth=16)
bad = []
n = 0
for lvl, items in D.items():
    for i, it in enumerate(items, 1):
        if it["theme"] in ("mateIn1", "mateIn2"): continue
        b = chess.Board(it["fen"])
        first = b.parse_san(it["sol"][0])
        best = eng.analyse(b, lim, multipv=2)
        top = best[0]["pv"][0]
        sc = lambda info: info["score"].pov(b.turn).score(mate_score=10000)
        s_best = sc(best[0])
        b.push(first)
        after = eng.analyse(b, lim)["score"].pov(not b.turn).score(mate_score=10000)
        n += 1
        if top != first and s_best - after > 80:
            bad.append((f"{lvl}.{i}", it["id"], it["sol"][0], b.copy().pop() and "", s_best, after))
print("controllati", n, "sospetti", len(bad))
for x in bad: print(x)
eng.quit()
