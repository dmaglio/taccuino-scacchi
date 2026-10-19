"""Genera build/taccuino.epub dal file HTML del PDF.

Le scacchiere diventano PNG (gli e-reader gestiscono male gli SVG), le
impaginazioni a griglia diventano una colonna sola e i capitoli sono i livelli.
Richiede rsvg-convert, ImageMagick e pandoc."""
import pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "build"
W = B / "epub"
shutil.rmtree(W, ignore_errors=True)
(W / "img").mkdir(parents=True)

html = (B / "taccuino.html").read_text(encoding="utf-8")
html = re.sub(r"<style>.*?</style>", "", html, flags=re.S)

# 1. scacchiere: SVG -> PNG
count = 0
def to_png(m):
    global count
    count += 1
    name = f"img/b{count:04d}.png"
    svg = m.group(0)
    if "xmlns=" not in svg[:200]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    subprocess.run(["rsvg-convert", "-w", "480", "-o", str(W / name)], input=svg.encode(), check=True)
    subprocess.run(["magick", str(W / name), "-colors", "12", "PNG8:" + str(W / name)], check=True)
    return f'<img src="{name}" alt="Scacchiera"/>'
html = re.sub(r"<svg\b.*?</svg>", to_png, html, flags=re.S)

# 2. titoli dei capitoli
def head(m):
    n, t = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
    label = f"Livello {n}: {t}" if n.isdigit() and n != "0" else t
    return f"<h1>{label}</h1>"
html = re.sub(r'<div class="lvlhead"><div class="n"[^>]*>(.*?)</div><h2>(.*?)</h2></div>', head, html, flags=re.S)
html = re.sub(r'<div class="run">.*?</div>', "", html, flags=re.S)
html = re.sub(r'<section class="cover".*?</section>', "", html, flags=re.S)

# 3. segni di mossa e casella da spuntare
html = html.replace('<span class="who w"></span>', "○ ").replace('<span class="who b"></span>', "● ")
html = html.replace('<span class="tick"></span>', "☐")

# 4. un esercizio per blocco
html = re.sub(r'<div class="cap">(.*?)</div></div>', lambda m: "<p class=\"cap\">" + re.sub(r"</?span[^>]*>", " ", m.group(1)) + "</p></div>", html, flags=re.S)
(W / "in.html").write_text(html, encoding="utf-8")

(W / "style.css").write_text("""
body { font-family: serif; line-height: 1.4; }
h1 { font-family: sans-serif; margin: 1.2em 0 .6em; }
img { display:block; width: 78%; max-width: 480px; margin: .8em auto .2em; }
figure { margin: 1em 0; text-align: center; }
figcaption, .cap { font-size: .85em; text-align: center; margin: 0 0 1.1em; font-family: sans-serif; }
table { border-collapse: collapse; margin: .6em auto; font-family: sans-serif; font-size:.9em; }
td, th { border: 1px solid #888; padding: .15em .6em; }
.sol p { margin: .15em 0; font-family: monospace; font-size: .85em; }
.score { border: 1px solid #2f5d50; padding: .4em .8em; margin: 1em 0; }
.lines div { border-bottom: 1px solid #aaa; height: 1.8em; }
""", encoding="utf-8")

# copertina
subprocess.run(["magick", "-size", "1200x1600", "xc:#2f5d50", "-gravity", "center", "-fill", "white",
                "-font", "DejaVu-Sans-Bold", "-pointsize", "110", "-annotate", "+0-160", "Passo dopo passo",
                "-pointsize", "50", "-annotate", "+0+0", "Taccuino di scacchi a livelli",
                "-pointsize", "36", "-annotate", "+0+120", "ripasso, 7 livelli, 275 esercizi", str(W / "cover.png")], check=True)

out = B / "taccuino.epub"
subprocess.run(["pandoc", str(W / "in.html"), "-f", "html", "-t", "epub3", "-o", str(out),
                "--split-level=1", "--toc", "--toc-depth=1", "--css", str(W / "style.css"),
                "--epub-cover-image", str(W / "cover.png"), "--resource-path", str(W),
                "--metadata", "title=Passo dopo passo", "--metadata", "subtitle=Taccuino di scacchi a livelli",
                "--metadata", "lang=it", "--metadata", "rights=Esercizi: Lichess (CC0). Testi: originali."], check=True, cwd=W)
print("epub", out, out.stat().st_size // 1024, "KB,", count, "scacchiere")
