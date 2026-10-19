"""Genera build/taccuino.html (poi PDF con Chrome) dagli esercizi scelti."""
import html, json, pathlib
import chess, chess.svg

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.load(open(ROOT / "data/selected.json"))
COL = {"square light": "#fbfaf6", "square dark": "#bdb7a6",
       "square light lastmove": "#e9e3b0", "square dark lastmove": "#cfc77e",
       "margin": "#ffffff", "coord": "#555555"}
IT = str.maketrans("KQRBN", "RDTAC")      # lettere dei pezzi in italiano

def ita(san): return san.translate(IT)

def board_svg(board, size, flipped=False, last=None, arrows=()):
    return chess.svg.board(board, size=size, flipped=flipped, coordinates=True,
                           lastmove=last, colors=COL, arrows=list(arrows))

# ---------------------------------------------------------------- esempi delle lezioni
def ex(fen, *moves, caption="", must=None, flip=False):
    """Esempio verificato: applica le mosse e controlla la condizione."""
    b = chess.Board(fen); start = b.copy(); last = None
    for m in moves:
        mv = b.parse_san(m); last = mv; b.push(mv)
    if must: assert must(b), (fen, moves)
    return dict(board=start, caption=caption, flip=flip)

def fig(e, size=190):
    svg = board_svg(e["board"], size, e["flip"])
    return f'<figure>{svg}<figcaption>{e["caption"]}</figcaption></figure>'

def scholar():
    b = chess.Board()
    for m in ["e4", "e5", "Qh5", "Nc6", "Bc4", "Nf6"]: b.push_san(m)
    b2 = b.copy(); b2.push_san("Qxf7"); assert b2.is_checkmate()
    return dict(board=b, caption="Tocca al Bianco: <b>Dxf7#</b> (il «matto del barbiere»).", flip=False)

def skewer_ok():
    b = chess.Board("3k3q/8/8/8/8/8/8/R3K3 w - - 0 1"); b.push_san("Ra8+")
    for m in list(b.legal_moves):
        c = b.copy(); c.push(m)
        assert chess.Move.from_uci("a8h8") in c.legal_moves
        assert c.piece_at(chess.H8).piece_type == chess.QUEEN
    return True

def disc_ok(b):
    return b.is_check() and b.piece_at(chess.H8) == chess.Piece(chess.BISHOP, chess.WHITE)

LEVELS = {
 0: dict(title="Prima di cominciare", intro=""),
 1: dict(title="Il matto in una mossa", goal="Riconoscere al volo il re in trappola.",
   text="""<p>Una partita finisce quando un re è sotto <b>scacco</b> (attaccato) e <b>non ha nessun modo di salvarsi</b>: è lo <b>scacco matto</b>. Per salvarsi un re può fare tre cose: spostarsi, catturare il pezzo che attacca, oppure mettere un pezzo in mezzo. Se nessuna delle tre funziona, è matto.</p>
<p>Prima di muovere chiediti sempre: <i>«Quali sono le caselle libere intorno al re avversario? Chi le controlla già?»</i> Spesso i pezzi dell'avversario (o il suo stesso re) gli tolgono le vie di fuga.</p>
<ul><li><b>Matto del corridoio</b>: il re è chiuso dai suoi pedoni sulla prima traversa e una torre o la donna dà scacco in orizzontale.</li>
<li><b>Donna protetta</b>: la donna dà scacco accanto al re avversario e un altro tuo pezzo la difende, quindi il re non può catturarla.</li></ul>
<p>In questo livello ogni esercizio ha <b>una sola mossa</b> da trovare: l'ultima, quella che dà matto. Guarda tutti gli scacchi possibili, anche quelli che sembrano regalare un pezzo.</p>""",
   examples=[
     ex("6k1/5ppp/8/8/8/8/8/R3K3 w - - 0 1", "Ra8", caption="Matto del corridoio: <b>Ta8#</b>.", must=lambda b: b.is_checkmate()),
     ex("7k/8/5K2/8/8/8/8/6Q1 w - - 0 1", "Qg7", caption="Donna protetta dal re: <b>Dg7#</b>.", must=lambda b: b.is_checkmate()),
     scholar()]),
 2: dict(title="Il matto in due mosse", goal="Pensare una mossa avanti: costringere, poi dare matto.",
   text="""<p>Qui il matto arriva alla <b>seconda</b> mossa. La prima è quasi sempre una mossa che <b>costringe</b> l'avversario: uno scacco, oppure una minaccia di matto così forte che ha pochissime risposte.</p>
<p>Un metodo che funziona: 1) elenca le tue mosse di scacco, 2) per ciascuna chiediti <i>«dove può andare il re? posso catturare io il pezzo che mi disturba?»</i>, 3) cerca il matto dopo ogni risposta possibile. Se per <b>tutte</b> le risposte esiste un matto, hai la soluzione.</p>
<p>Nella soluzione, in fondo, vedrai la risposta più resistente dell'avversario. Se l'avversario ne ha altre equivalenti, il matto resta comunque.</p>
<p><b>Esempio, la «scala»:</b> due torri sulle traverse vicine bloccano il re un gradino alla volta. Dopo 1.Ta7 il re nero non può uscire dall'ottava traversa se non per andare incontro a Tb8#.</p>""",
   examples=[ex("6k1/8/8/8/8/8/R7/1R4K1 w - - 0 1", "Ra7", "Kf8", "Rb8", caption="Matto della scala: 1.Ta7 Rf8 2.Tb8#.", must=lambda b: b.is_checkmate())]),
 3: dict(title="Pezzi in presa", goal="Non regalare materiale, approfittare di quello regalato.",
   text="""<p>Un pezzo è <b>«in presa»</b> quando è attaccato e non abbastanza difeso. La maggior parte delle partite tra principianti si decide qui: basta vincere un pezzo gratis per vincere la partita.</p>
<table class="vals"><tr><th>Pedone</th><th>Cavallo</th><th>Alfiere</th><th>Torre</th><th>Donna</th></tr><tr><td>1</td><td>3</td><td>3</td><td>5</td><td>9</td></tr></table>
<p>Prima di <b>ogni</b> mossa, il controllo in quattro passi:</p>
<ol><li>Che cosa ha mosso l'avversario? Cosa minaccia adesso?</li><li>Quali dei miei pezzi sono attaccati? Sono difesi?</li><li>Quali pezzi suoi sono attaccati o indifesi?</li><li>La mossa che sto per fare lascia un pezzo scoperto?</li></ol>
<p>Se attacchi un pezzo di valore <b>maggiore</b> del tuo, o un pezzo indifeso, spesso conviene catturarlo anche se ti difende un pedone: fai il conto dei valori.</p>""",
   examples=[ex("4k3/8/8/3n4/8/8/8/3RK3 w - - 0 1", "Rxd5", caption="Il cavallo in d5 è attaccato e <b>non difeso</b>: <b>Txd5</b> vince un pezzo.", must=lambda b: b.piece_at(chess.D5) == chess.Piece(chess.ROOK, chess.WHITE))]),
 4: dict(title="Forchette e inchiodature", goal="Colpire due bersagli con una sola mossa.",
   text="""<p>Una <b>forchetta</b> è una mossa che attacca <b>due pezzi insieme</b>: l'avversario può salvarne uno solo. Il cavallo è il campione delle forchette perché salta e dà scacco da una casa che spesso nessuno protegge; ma anche pedoni, alfieri e donna possono farle.</p>
<p>Un'<b>inchiodatura</b> immobilizza un pezzo perché dietro di lui c'è un pezzo più importante. Se il pezzo inchiodato è davanti al re, non può muoversi affatto (è una regola). Se è davanti alla donna, muoverlo costa la donna.</p>
<p>Come cercarle: guarda dove stanno <b>re, donna e torri</b> avversari. Se due sono sulla stessa diagonale, riga o colonna, o a «salto di cavallo» da una casa libera, hai quasi sempre un'occasione.</p>""",
   examples=[ex("r3k3/8/8/3N4/8/8/8/4K3 w - - 0 1", "Nc7+", caption="Forchetta: <b>Cc7+</b> attacca re e torre.", must=lambda b: b.is_check() and b.is_attacked_by(chess.WHITE, chess.A8)),
             ex("4k3/8/2n5/8/8/8/8/4KB2 w - - 0 1", "Bb5", caption="Inchiodatura: <b>Ab5</b> e il cavallo non può muoversi.", must=lambda b: b.is_pinned(chess.BLACK, chess.C6))]),
 5: dict(title="Infilate e attacchi di scoperta", goal="Far spostare un pezzo per colpire quello che sta dietro.",
   text="""<p>Una <b>infilata</b> è l'opposto dell'inchiodatura: attacchi un pezzo <b>di valore</b> (di solito il re o la donna), che deve spostarsi, e così catturi il pezzo che gli stava dietro.</p>
<p>Un <b>attacco di scoperta</b> si ha quando muovi un pezzo e <b>scopri</b> l'attacco di un altro pezzo che stava dietro. È potentissimo se il pezzo che muovi dà a sua volta scacco o cattura qualcosa: l'avversario si trova di fronte due minacce insieme.</p>
<p>Cerca le linee: colonne, traverse e diagonali che hanno un tuo pezzo lungo («torre, alfiere, donna») con in mezzo uno dei tuoi pezzi. Spostare quel pezzo con uno scopo può essere la mossa vincente.</p>""",
   examples=[ex("3k3q/8/8/8/8/8/8/R3K3 w - - 0 1", "Ra8+", caption="Infilata: <b>Ta8+</b>, il re si sposta e <b>Txh8</b> prende la donna.", must=lambda b: skewer_ok()),
             ex("4k2q/8/8/4B3/8/8/8/4RK2 w - - 0 1", "Bxh8+", caption="Scoperta: <b>Axh8+</b> cattura la donna e la torre in e1 dà scacco.", must=disc_ok)]),
 7: dict(title="Le aperture", goal="Mettere i pezzi al posto giusto nei primi dieci minuti.", text="", examples=[]),
 6: dict(title="I finali", goal="Convertire un piccolo vantaggio e non sprecare la vittoria.",
   text="""<p>Nei finali ci sono pochi pezzi e il <b>re diventa un pezzo attivo</b>: portalo al centro. Tre idee da conoscere:</p>
<ul><li><b>L'opposizione</b>: i due re si fronteggiano con una casa in mezzo; chi non deve muovere ha un vantaggio. Con il re davanti al pedone, in sesta traversa, il pedone promuove <i>qualunque</i> cosa faccia l'avversario.</li>
<li><b>Matto con re e torre</b>: la torre chiude una traversa, il re avversario è costretto ai bordi e l'ultimo scacco lo dà la torre, con il tuo re vicino.</li>
<li><b>Stallo</b>: se l'avversario non ha mosse legali e non è sotto scacco, la partita è <b>patta</b>. Prima di dare scacco con la donna, controlla che l'avversario abbia ancora una mossa!</li></ul>""",
   examples=[ex("4k3/8/4K3/4P3/8/8/8/8 w - - 0 1", "Kd6", caption="Re davanti al pedone: <b>Rd6</b>, poi e6, e7. Il pedone promuove.", must=lambda b: True),
             ex("7k/8/6K1/8/8/8/8/R7 w - - 0 1", "Ra8", caption="Matto di torre: <b>Ta8#</b>.", must=lambda b: b.is_checkmate()),
             ex("7k/8/6K1/5Q2/8/8/8/8 w - - 0 1", "Qf7", caption="Attenzione: <b>Df7</b> è <b>stallo</b>, patta!", must=lambda b: b.is_stalemate())]),
}

# ---------------------------------------------------------------- ripasso regole e aperture
def svg_sq(board, squares, size=170, flip=False, last=None):
    fill = {s: "#2f5d5099" for s in squares}
    return chess.svg.board(board, size=size, flipped=flip, coordinates=True, fill=fill, lastmove=last, colors=COL)

def mv_fig(fen, piece_sq, caption):
    b = chess.Board(fen)
    targets = {m.to_square for m in b.legal_moves if m.from_square == chess.parse_square(piece_sq)}
    assert targets, (fen, piece_sq)
    return f'<figure>{svg_sq(b, targets)}<figcaption>{caption}</figcaption></figure>'

def rules_html():
    """Ripasso delle regole: tutto verificato con python-chess."""
    # mosse dei pezzi (re e pezzi soli sulla scacchiera, senza scacchi illegali)
    kn = mv_fig("4k3/8/8/8/3N4/8/8/4K3 w - - 0 1", "d4", "<b>Cavallo</b>: salta a «L» e scavalca i pezzi.")
    rk = mv_fig("4k3/8/8/8/3R4/8/8/4K3 w - - 0 1", "d4", "<b>Torre</b>: in orizzontale e verticale.")
    bi = mv_fig("4k3/8/8/8/3B4/8/8/4K3 w - - 0 1", "d4", "<b>Alfiere</b>: in diagonale; resta sempre sullo stesso colore.")
    qu = mv_fig("4k3/8/8/8/3Q4/8/8/4K3 w - - 0 1", "d4", "<b>Donna</b>: come torre e alfiere insieme.")
    ki = mv_fig("8/8/8/4k3/8/8/3K4/8 w - - 0 1", "d2", "<b>Re</b>: una casa in ogni direzione, mai su una casa attaccata.")
    pb = chess.Board("4k3/8/8/8/8/3p1p2/4P3/4K3 w - - 0 1")
    pt = {m.to_square for m in pb.legal_moves if m.from_square == chess.E2}
    assert pt == {chess.E3, chess.E4, chess.D3, chess.F3}
    pw = f'<figure>{svg_sq(pb, pt)}<figcaption><b>Pedone</b>: avanza di 1 (di 2 alla prima mossa) e <i>cattura in diagonale</i>.</figcaption></figure>'
    start = f'<figure>{board_svg(chess.Board(), 250)}<figcaption>La posizione iniziale. Casa in basso a destra: <b>chiara</b>. La donna sta sul proprio colore.</figcaption></figure>'
    # arrocco
    cb = chess.Board("r3k2r/pppq1ppp/2npbn2/2b1p3/2B1P3/2NPBN2/PPPQ1PPP/R3K2R w KQkq - 0 1")
    assert chess.Move.from_uci("e1g1") in cb.legal_moves and chess.Move.from_uci("e1c1") in cb.legal_moves
    castle = f'<figure>{board_svg(cb, 200)}<figcaption><b>Arrocco</b>: re e torre insieme (<b>O-O</b> corto, <b>O-O-O</b> lungo). Non vale se re o torre si sono già mossi, se ci sono pezzi in mezzo, o se il re passa per una casa attaccata.</figcaption></figure>'
    # en passant
    ep = chess.Board("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    assert chess.Move.from_uci("e5d6") in ep.legal_moves and ep.is_en_passant(chess.Move.from_uci("e5d6"))
    enp = f'<figure>{board_svg(ep, 200)}<figcaption><b>En passant</b>: il Nero ha appena giocato d7-d5. Il pedone in e5 può catturare «di passaggio» (<b>exd6</b>), ma solo subito.</figcaption></figure>'
    pr = chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    assert chess.Move.from_uci("a7a8q") in pr.legal_moves
    prom = f'<figure>{board_svg(pr, 200)}<figcaption><b>Promozione</b>: un pedone che arriva all\'ultima traversa diventa donna (quasi sempre), torre, alfiere o cavallo.</figcaption></figure>'
    return f"""
<section><div class="lvlhead"><div class="n">R</div><h2>Ripasso delle regole</h2></div>
<p class="goal">Mezz'ora per rimettere in ordine ciò che sai già.</p>
<div class="figs">{start}<div style="flex:1;padding-left:4mm"><p><b>Come si dispone.</b> Ogni giocatore ha 16 pezzi: un re, una donna, due torri, due alfieri, due cavalli, otto pedoni. Il Bianco muove sempre per primo, poi si alterna.</p>
<p><b>Come finisce.</b> Con lo <b>scacco matto</b> (vittoria), ma anche con una <b>patta</b>: per stallo, per accordo, per materiale insufficiente per dare matto (per esempio re contro re), per triplice ripetizione della stessa posizione, o dopo 50 mosse senza catture né mosse di pedone.</p></div></div>
<div class="figs">{kn}{rk}{bi}</div>
<div class="figs">{qu}{ki}{pw}</div>
<p><b>Lo scacco.</b> Quando il tuo re è attaccato <i>devi</i> subito rimediare: spostarlo, catturare chi attacca, o mettere un pezzo in mezzo (non contro un cavallo). Non puoi mai fare una mossa che lasci il tuo re sotto scacco.</p></section>
<section><div class="lvlhead"><div class="n">R</div><h2>Le mosse speciali</h2></div>
<div class="figs">{castle}{enp}{prom}</div>
<p><b>Tre regole che si dimenticano.</b> 1) Il Bianco muove per primo, anche se si tratta di un esercizio: guarda il bollino. 2) Un pezzo toccato è un pezzo mosso, se si gioca sul serio. 3) Lo <b>stallo</b> (nessuna mossa legale e re non sotto scacco) è una patta: non è una vittoria, e può sfuggire a chi è in vantaggio.</p>
<div class="score"><b>Prova.</b> Prendi una scacchiera e disponi il Bianco e il Nero. Muovi un pezzo alla volta: prima la torre, poi il cavallo, poi un arrocco, poi un en passant. Quando riesci a farlo senza pensare, sei pronto per il livello 1.</div></section>"""

OPENINGS = [
 ("L'Italiana", "1.e4 e5 2.Cf3 Cc6 3.Ac4", "e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d3 d6 O-O O-O",
  "Alfiere e cavallo puntano il punto debole <b>f7</b> e il centro. Il piano: preparare <b>c3</b> e <b>d4</b>, arroccare presto, portare le torri in gioco. È l'apertura più semplice da capire."),
 ("La Spagnola", "1.e4 e5 2.Cf3 Cc6 3.Ab5", "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O",
  "L'alfiere attacca il cavallo che difende e5: non vince subito niente, ma crea una pressione che dura per tutta la partita. Il Bianco ritira l'alfiere in b3, prepara c3 e poi d4."),
 ("Il Sistema di Londra", "1.d4 d5 2.Af4", "d4 d5 Bf4 Nf6 e3 e6 Nf3 Bd6 Bg3 O-O Bd3 b6",
  "Con il Bianco giochi quasi le stesse mosse contro quasi tutto: <b>d4, Af4, e3, Cf3, Ad3, c3, Cbd2</b> e arrocco. Poche varianti da imparare, struttura solida."),
 ("Il Gambetto di Donna", "1.d4 d5 2.c4", "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O Nf3 Nbd7",
  "Il Bianco offre un pedone per ottenere il centro. Se il Nero lo prende (2...dxc4) lo restituisce presto; se si difende con 2...e6 nascono posizioni solide e chiare, adatte a chi vuole giocare con calma."),
]

def opening_fig(moves):
    b = chess.Board()
    for m in moves.split(): b.push_san(m)
    return b

def legal_trap():
    """Il matto di Légal: verificato fino al matto."""
    b = chess.Board()
    seq = "e4 e5 Nf3 d6 Bc4 Bg4 Nc3 g6 Nxe5 Bxd1 Bxf7+ Ke7 Nd5".split()
    for m in seq[:-1]: b.push_san(m)
    start = b.copy()
    b.push_san(seq[-1]); assert b.is_checkmate()
    return start

def openings_html():
    out = ['<section><div class="lvlhead"><div class="n">7</div><h2>Le aperture</h2></div>'
           '<p class="goal">Mettere i pezzi al posto giusto nei primi dieci minuti.</p>'
           '<p>Le prime mosse non servono a vincere subito: servono a <b>arrivare a una posizione comoda</b> senza perdere materiale. Cinque regole bastano a quasi tutto:</p>'
           '<ol><li><b>Occupa il centro</b> (le case e4, d4, e5, d5) con un pedone o con i pezzi.</li>'
           '<li><b>Sviluppa</b> cavalli e alfieri: ogni mossa deve portare un pezzo in gioco.</li>'
           '<li><b>Arrocca presto</b>: il re al sicuro e la torre libera.</li>'
           '<li><b>Non muovere due volte lo stesso pezzo</b> senza motivo.</li>'
           '<li><b>Non uscire troppo presto con la donna</b>: sarà attaccata e perderai tempo.</li></ol>'
           '<p>Qui sotto trovi quattro aperture adatte a chi comincia. Impara <b>idee e piani</b>, non solo le mosse a memoria: se l\'avversario devia, sai ancora cosa vuoi fare.</p></section>']
    for k, (title, head, moves, idea) in enumerate(OPENINGS):
        b = opening_fig(moves)
        fig_ = f'<figure style="flex:0 0 66mm">{board_svg(b, 205)}<figcaption>La posizione dopo: <b>{ita(chess.Board().variation_san(b.move_stack))}</b></figcaption></figure>'
        brk = "page" if k in (1, 3) else "auto"
        out.append(f'<section style="break-before:{brk};margin-top:6mm;break-inside:avoid"><div class="lvlhead"><div class="n" style="font-size:28pt">♘</div><h2>{title}</h2></div>'
                   f'<p class="sub">{head}</p><div class="figs"><div style="flex:1">{"<p>"+idea+"</p>"}'
                   f'<p class="small">Le mosse sono scritte con i nomi italiani dei pezzi (C cavallo, A alfiere, T torre, D donna, R re).</p></div>{fig_}</div></section>')
    # trappola
    t = legal_trap()
    out.append('<section style="break-before:auto;margin-top:8mm"><div class="lvlhead"><div class="n" style="font-size:28pt">⚠</div><h2>Una trappola da conoscere: il matto di Légal</h2></div>'
               '<p>Una trappola classica contro chi prende senza pensare. Dopo <b>1.e4 e5 2.Cf3 d6 3.Ac4 Ag4 4.Cc3 g6 5.Cxe5!?</b> il Nero prende la donna con 5...Axd1. Ma il Bianco gioca <b>6.Axf7+ Re7 7.Cd5#</b>: matto con soli due pezzi leggeri.</p>'
               f'<div class="figs"><figure>{board_svg(t, 260)}<figcaption>Tocca al Bianco: <b>Cd5#</b>.</figcaption></figure></div>'
               '<p>La lezione: <b>quando l\'avversario ti offre un pezzo, chiediti perché.</b> Non sempre è un regalo.</p></section>')
    return "".join(out)

QUIZ = [
 ("Quale mossa controlla meglio il centro nelle prime battute?", ["a3", "e4 o d4", "h4"], "b"),
 ("Quale tra questi è un «pezzo minore»?", ["Torre", "Cavallo", "Donna"], "b"),
 ("Perché conviene arroccare presto?", ["Il re è più al sicuro e la torre entra in gioco", "Per catturare i pedoni", "Perché è obbligatorio"], "a"),
 ("Dopo 1.e4 e5 2.Cf3 Cc6 3.Ac4, come si chiama l'apertura?", ["Spagnola", "Italiana", "Siciliana"], "b"),
 ("Dopo 1.e4 e5 2.Cf3 Cc6 3.Ab5, come si chiama l'apertura?", ["Spagnola", "Italiana", "Londra"], "a"),
 ("Qual è il punto più debole del Nero all'inizio della partita?", ["f7", "a7", "e5"], "a"),
 ("Uscire con la donna dopo poche mosse è…", ["quasi sempre ottimo", "rischioso: la donna sarà attaccata e perdi tempo", "obbligatorio"], "b"),
 ("Muovere due volte lo stesso pezzo in apertura, senza motivo…", ["fa perdere tempo", "è obbligatorio", "vince materiale"], "a"),
 ("Quale di queste mosse, di solito, non porta pezzi in gioco?", ["Cf3", "Ac4", "a3"], "c"),
 ("Nel Sistema di Londra l'alfiere del Bianco va in…", ["f4", "h6", "a6"], "a"),
 ("Con «il centro» si intendono le case…", ["e4, d4, e5, d5", "quelle sul bordo", "l'ultima traversa"], "a"),
 ("Dopo l'arrocco corto il re del Bianco sta in…", ["g1", "c1", "h1"], "a"),
]

def quiz_html():
    out = ['<section><div class="run">Livello 7 · Le aperture · Quiz</div><h2 style="margin-bottom:4mm">Quiz di fine livello</h2>'
           '<p class="small">Una sola risposta giusta. Cerchia la lettera.</p>']
    for i, (q, opts, _) in enumerate(QUIZ, 1):
        out.append(f'<p style="margin:3mm 0 1mm"><b>7.Q{i}</b> {q}</p><p style="margin:0 0 0 6mm; font:10.5pt Arial">'
                   + " &nbsp;&nbsp; ".join(f"<b>{l})</b> {o}" for l, o in zip("abc", opts)) + '</p>')
    out.append('</section>')
    return "".join(out)
# ---------------------------------------------------------------- come si scrivono le mosse
def hi_board(sqs, size=150, arrows=(), board=None):
    b = board or chess.Board(None)
    return chess.svg.board(b, size=size, fill={s: "#2f5d5099" for s in sqs}, arrows=list(arrows),
                           coordinates=True, colors=COL)

def notation_data():
    lines = {
        "italiana": "e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d3 d6 O-O O-O".split(),
        "spagnola": "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6".split(),
        "legal": "e4 e5 Nf3 d6 Bc4 Bg4 Nc3 g6 Nxe5 Bxd1 Bxf7+ Ke7 Nd5".split(),
    }
    picks = [("italiana", 0), ("italiana", 2), ("italiana", 4), ("italiana", 10),
             ("spagnola", 7), ("legal", 8), ("legal", 10), ("legal", 12)]
    out = []
    for name, ply in picks:
        b = chess.Board()
        for m in lines[name][:ply]: b.push_san(m)
        mv = b.parse_san(lines[name][ply])
        san = b.san(mv)
        b.push(mv); mate_ok = (not san.endswith("#")) or b.is_checkmate(); assert mate_ok
        b.pop()
        out.append((b.copy(), mv, ita(san)))
    return out

SQUARES = ["e4", "c6", "g1", "h8", "b3", "d7"]

def notation_html():
    items = notation_data()
    coord = f'<figure style="flex:0 0 80mm">{hi_board([chess.E4, chess.G7], 230)}<figcaption>Ogni casa ha un nome: <b>colonna</b> (lettera, da a a h) + <b>traversa</b> (numero, da 1 a 8). Le due case evidenziate sono <b>e4</b> e <b>g7</b>. Il Bianco sta sempre in basso, anche quando muove il Nero.</figcaption></figure>'
    tbl = ('<table class="piece"><tr><th>Pezzo</th><th>Re</th><th>Donna</th><th>Torre</th><th>Alfiere</th><th>Cavallo</th><th>Pedone</th></tr>'
           '<tr><td>Lettera</td><td>R</td><td>D</td><td>T</td><td>A</td><td>C</td><td><i>nessuna</i></td></tr></table>')
    exs = ('<table class="piece">'
           '<tr><th>Si scrive</th><th>Vuol dire</th></tr>'
           '<tr><td><b>e4</b></td><td>un pedone va in e4 (niente lettera: è un pedone)</td></tr>'
           '<tr><td><b>Cf3</b></td><td>il cavallo va in f3</td></tr>'
           '<tr><td><b>Axc6</b></td><td>l\'alfiere cattura in c6 (la <b>x</b> vuol dire «cattura»)</td></tr>'
           '<tr><td><b>exd5</b></td><td>il pedone della colonna e cattura in d5 (con i pedoni si scrive la colonna di partenza)</td></tr>'
           '<tr><td><b>Dh5+</b></td><td>la donna va in h5 e dà <b>scacco</b></td></tr>'
           '<tr><td><b>Dxf7#</b></td><td>la donna cattura in f7 e dà <b>scacco matto</b></td></tr>'
           '<tr><td><b>O-O</b> · <b>O-O-O</b></td><td>arrocco corto (lato del re) · arrocco lungo (lato della donna)</td></tr>'
           '<tr><td><b>e8=D</b></td><td>il pedone arriva in e8 e diventa donna</td></tr>'
           '<tr><td><b>Tad1</b></td><td>due torri possono andare in d1: si scrive da quale vengono (qui da <b>a</b>)</td></tr></table>')
    html1 = (f'<section class="notat" style="font-size:11pt;line-height:1.4"><div class="lvlhead"><div class="n">R</div><h2>Come si scrivono le mosse</h2></div>'
             '<p>Ogni mossa si scrive con <b>la lettera del pezzo</b> (in italiano) e <b>la casa di arrivo</b>. Per i pedoni non c\'è lettera.</p>'
             f'{tbl}<div class="figs">{coord}<div style="flex:1;padding-left:5mm">'
             '<p><b>I numeri.</b> «<b>12.</b> Cf3 Cc6» è la mossa numero 12: prima il Bianco, poi il Nero. Se si scrive solo la mossa del Nero compaiono tre puntini: «<b>12...</b> Cc6».</p>'
             '<p><b>Un trucco.</b> Per trovare una casa, prima cerca la <b>lettera</b> lungo il bordo, poi sali con il <b>numero</b>. Con un po\' di pratica la leggi senza pensarci.</p></div></div>'
             f'{exs}</section>')
    # pagina di esercizi
    cells = []
    for i, sq in enumerate(SQUARES, 1):
        cells.append(f'<div class="ex">{hi_board([chess.parse_square(sq)], 190)}<div class="cap"><span><b>A.{i}</b></span><span>Nome della casa</span><span class="tick"></span></div></div>')
    for i, (b, mv, san) in enumerate(items, 1):
        arrows = [(mv.from_square, mv.to_square)]
        svg = chess.svg.board(b, size=190, arrows=arrows, coordinates=True, colors=COL)
        who = "Bianco" if b.turn else "Nero"
        cells.append(f'<div class="ex">{svg}<div class="cap"><span><b>B.{i}</b></span><span>Mossa del {who}</span><span class="tick"></span></div></div>')
    html2 = ('<section><div class="run">Ripasso · Come si scrivono le mosse · Esercizi</div>'
             '<p class="small">A) Scrivi il nome della casa evidenziata. B) La freccia mostra la mossa giocata: scrivila in notazione. Le soluzioni sono in fondo.</p>'
             '<div class="grid g4" style="grid-template-columns:repeat(4,1fr)">' + "".join(cells) + '</div></section>')
    answers = ["<p><b>A</b>&nbsp; " + " &nbsp; ".join(f"{i}) {sq}" for i, sq in enumerate(SQUARES, 1)) + "</p>",
               "<p><b>B</b>&nbsp; " + " &nbsp; ".join(f"{i}) {san}" for i, (_, _, san) in enumerate(items, 1)) + "</p>"]
    return html1 + html2, answers

SECTION_LABEL = {"fork": "Forchette", "pin": "Inchiodature", "skewer": "Infilate",
                 "discoveredAttack": "Attacchi di scoperta"}

CSS = """
@page { size: A4; margin: 14mm 14mm 16mm 14mm;
  @bottom-center { content: counter(page); font: 9pt Georgia, serif; color:#777; } }
:root { --acc:#2f5d50; --ink:#1d1d1b; }
* { box-sizing: border-box; }
body { font: 11pt/1.45 Georgia, 'DejaVu Serif', serif; color: var(--ink); margin:0; }
h1,h2,h3 { font-family: 'Helvetica Neue', Arial, sans-serif; margin:0; }
section { break-before: page; }
.cover { height: 265mm; display:flex; flex-direction:column; justify-content:center; text-align:left; border-left: 8mm solid var(--acc); padding-left: 14mm; }
.cover .k { font: 120pt/1 'DejaVu Sans', sans-serif; color: var(--acc); }
.cover h1 { font-size: 40pt; line-height:1.05; margin-top: 6mm; }
.cover p { font-size: 14pt; color:#444; max-width: 120mm; }
.lvlhead { display:flex; align-items:baseline; gap:6mm; border-bottom: 2px solid var(--acc); padding-bottom:3mm; margin-bottom:5mm; }
.lvlhead .n { font: 700 46pt/1 Arial, sans-serif; color: var(--acc); }
.lvlhead h2 { font-size: 22pt; }
.goal { color:#555; font-style: italic; margin: 0 0 4mm; }
.figs { display:flex; gap: 4mm; margin: 5mm 0; justify-content: space-between; }
figure { margin:0; text-align:center; font-size: 9pt; }
figure svg { display:block; margin:0 auto 2mm; max-width:100%; height:auto; }
.score { border:1.5px solid var(--acc); padding: 3mm 5mm; margin-top: 5mm; font: 10pt Arial, sans-serif; }
.vals { border-collapse: collapse; margin: 2mm 0 4mm; font: 10pt Arial, sans-serif; }
.vals th, .vals td { border:1px solid #999; padding: 1.5mm 4mm; text-align:center; }
.run { font: 8.5pt Arial, sans-serif; color:#777; margin-bottom: 3mm; text-transform: uppercase; letter-spacing:.06em; }
.grid { display:grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(3, auto); gap: 3mm 8mm; }
.ex { break-inside: avoid; }
.ex .cap { font: 10pt Arial, sans-serif; display:flex; justify-content:space-between; margin-top:1mm; }
.ex .cap b { color: var(--acc); }
.ex svg { display:block; width: 62mm; height:auto; margin: 1mm auto 0; }
.grid.g4 .ex svg { width: 41mm; }
.notat table.piece td, .notat table.piece th { padding: .5mm 3mm; }
.notat .figs { margin: 2mm 0; }
.grid.g4 .cap { font-size: 8pt; gap: 1.5mm; justify-content: flex-start; flex-wrap: wrap; }
.grid.g4 .cap .tick { margin-left:auto; }
.who { display:inline-block; width: 3.2mm; height: 3.2mm; border:1px solid #000; border-radius:50%; vertical-align:-0.4mm; margin-right:1.5mm; }
.who.w { background:#fff; } .who.b { background:#000; }
.tick { display:inline-block; width:4mm; height:4mm; border:1px solid #444; vertical-align:-0.8mm; }
.sub { font: 700 11pt Arial, sans-serif; color: var(--acc); margin: 0 0 2mm; }
.lines { margin-top: 3mm; }
.lines div { border-bottom: 1px solid #aaa; height: 9mm; }
.sol { columns: 2; column-gap: 10mm; font: 8.8pt/1.35 'DejaVu Sans Mono', monospace; }
.sol p { margin: 0; break-inside: avoid; }
.sol h3 { font-size: 11pt; margin: 4mm 0 1mm; color: var(--acc); column-span: all; }
.small { font-size: 9pt; color:#555; }
table.piece { border-collapse: collapse; font: 10pt Arial, sans-serif; margin: 2mm 0; }
table.piece td, table.piece th { border:1px solid #999; padding: 1.2mm 4mm; }
"""

def ex_cell(num, it, flipped_for_mover=True):
    b = chess.Board(it["fen"])
    flip = (it["turn"] == "b")
    svg = board_svg(b, 330, flip, chess.Move.from_uci(it["last"]))
    who = "Bianco" if it["turn"] == "w" else "Nero"
    return (f'<div class="ex">{svg}<div class="cap"><span><b>{num}</b></span>'
            f'<span><span class="who {it["turn"]}"></span>Muove il {who}</span>'
            f'<span class="tick"></span></div></div>')

def sol_text(it):
    if it["alts"]:
        return " <span class='small'>o</span> ".join(ita(s) for s in it["sol"])
    n = it["fullmove"]; white = it["turn"] == "w"; parts = []
    b = chess.Board(it["fen"])
    first = True
    for san in it["sol"]:
        s = ita(san)
        if white: parts.append(f"{n}. {s}")
        else: parts.append(f"{n}... {s}" if first else s)
        first = False
        if not white: n += 1
        white = not white
    return " ".join(parts)

def main():
    out = [f"<!doctype html><html lang='it'><meta charset='utf-8'><title>Passo dopo passo</title><style>{CSS}</style><body>"]
    out.append("""<section class="cover" style="break-before:auto"><div class="k">♞</div>
<h1>Passo dopo passo</h1><p><b>Taccuino di scacchi a livelli</b><br>Ripasso delle regole, sette livelli e 275 esercizi con soluzione, per chi conosce le regole ma ha poca pratica.</p>
<p class="small">Esercizi dal database aperto di Lichess (CC0). Testi e impaginazione originali.</p></section>""")
    # istruzioni
    out.append("""<section><div class="lvlhead"><div class="n">0</div><h2>Prima di cominciare</h2></div>
<p><b>Come usarlo.</b> Ogni livello inizia con una breve lezione, poi vengono gli esercizi, dal più facile al più difficile. Fai pochi esercizi ma con attenzione: <b>dieci al giorno</b> valgono più di cinquanta in fretta. Scrivi la soluzione sulla pagina, <b>poi</b> controlla in fondo al libro.</p>
<p><b>Come si leggono i diagrammi.</b> La scacchiera è sempre vista dalla parte di chi muove (il pezzo in basso è suo). Un bollino <span class="who w"></span> vuol dire che muove il Bianco, un bollino <span class="who b"></span> il Nero. Il quadrato di casa giallo indica l'<b>ultima mossa dell'avversario</b>: spesso ti dice cosa sta minacciando.</p>
<p><b>Le mosse in notazione.</b> Ogni casa ha un nome: la colonna (da <b>a</b> a <b>h</b>) e la traversa (da <b>1</b> a <b>8</b>). I pezzi si indicano con la lettera italiana:</p>
<table class="piece"><tr><th>Re</th><th>Donna</th><th>Torre</th><th>Alfiere</th><th>Cavallo</th><th>Pedone</th></tr><tr><td>R</td><td>D</td><td>T</td><td>A</td><td>C</td><td><i>(nessuna)</i></td></tr></table>
<p><b>x</b> = cattura, <b>+</b> = scacco, <b>#</b> = scacco matto, <b>O-O</b> = arrocco. Esempio: <b>Cxe5+</b> significa «il cavallo cattura in e5 e dà scacco». Un numero con un punto è la mossa del Bianco (<b>12.</b>), con tre punti quella del Nero (<b>12...</b>).</p>
<p><b>Se non trovi la soluzione.</b> Dopo due minuti, guarda la soluzione e rimetti i pezzi come in diagramma: <i>perché</i> funziona? Una settimana dopo rifai gli esercizi sbagliati. È così che il cervello impara a riconoscere gli schemi.</p>
<p class="small">Le soluzioni in fondo mostrano la linea principale. In alcuni esercizi esistono altre soluzioni valide, soprattutto nei matti in una mossa dove sono elencate tutte.</p></section>""")
    out.append(rules_html())
    nh, nans = notation_html()
    out.append(nh)
    counts = {}
    sols = [(0, 'Come si scrivono le mosse', nans)]
    for lvl in range(1, 8):
        L = LEVELS[lvl]; items = DATA[str(lvl)]
        if lvl == 7:
            out.append(openings_html())
        else:
            out.append(f'<section><div class="lvlhead"><div class="n">{lvl}</div><h2>{L["title"]}</h2></div>'
                       f'<p class="goal">{L["goal"]}</p>{L["text"]}')
            out.append('<div class="figs">' + "".join(fig(e) for e in L["examples"]) + '</div>')
            out.append(f'<div class="score"><b>Il tuo punteggio</b> &nbsp; Esercizi risolti: ______ / {len(items)} &nbsp;&nbsp; Data: ____________</div></section>')
        # esercizi, 6 a pagina
        sol_lines = []
        prev_theme = None
        for i, it in enumerate(items, 1):
            if i == 1 or (i - 1) % 6 == 0 or it["theme"] != prev_theme and prev_theme is not None:
                # nuova pagina se necessario (cambio tema forza nuova pagina)
                if i != 1: out.append("</div></section>")
                label = SECTION_LABEL.get(it["theme"], "")
                out.append(f'<section><div class="run">Livello {lvl} · {L["title"]}{" · " + label if label else ""}</div><div class="grid">')
            prev_theme = it["theme"]
            num = f"{lvl}.{i}"
            out.append(ex_cell(num, it))
            sol_lines.append(f"<p><b>{num}</b>&nbsp; {sol_text(it)}</p>")
        out.append("</div></section>")
        if lvl == 7:
            out.append(quiz_html())
            sol_lines.append("<p><b>Quiz</b>&nbsp; " + " &nbsp; ".join(f"{i}{a}" for i, (_, _, a) in enumerate(QUIZ, 1)) + "</p>")
        sols.append((lvl, L["title"], sol_lines))
    # taccuino errori
    out.append('<section><div class="lvlhead"><div class="n">✎</div><h2>Il taccuino degli errori</h2></div>'
               '<p>Qui scrivi gli esercizi che hai sbagliato e <b>perché</b>. Rifalli dopo una settimana.</p>'
               '<div class="lines">' + "<div></div>" * 22 + '</div></section>')
    # soluzioni
    out.append('<section><div class="lvlhead"><div class="n">✓</div><h2>Soluzioni</h2></div><div class="sol">')
    for lvl, title, lines in sols:
        out.append(f"<h3>{'Ripasso' if lvl == 0 else 'Livello ' + str(lvl)} · {title}</h3>" + "".join(lines))
    out.append('</div></section>')
    out.append("""<section><div class="lvlhead"><div class="n">©</div><h2>Crediti</h2></div>
<p>Gli esercizi provengono dal database dei puzzle di <b>Lichess</b> (lichess.org), rilasciato in pubblico dominio (CC0). Le lezioni, la scelta e l'ordine degli esercizi e l'impaginazione sono originali. Le soluzioni sono state verificate con la libreria <i>python-chess</i> (ogni mossa è legale e i matti sono matti).</p></section>""")
    out.append("</body></html>")
    d = ROOT / "build"; d.mkdir(exist_ok=True)
    (d / "taccuino.html").write_text("\n".join(out), encoding="utf-8")
    print("ok", sum(len(v) for v in DATA.values()))

main()
