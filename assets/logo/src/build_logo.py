"""Hand-built RogueIQ raven. Coordinates traced from raven.png (512 grid). Run: python3 build_logo.py"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = "/workspace/rogueiq-brand-kit"

def P(pts): return "M" + " L".join(f"{x} {y}" for x, y in pts) + " Z"
# silhouette pieces
BODY = [(63,30),(284,80),(348,128),(361,152),(446,186),(502,237),(302,203),(233,270),(229,398),(211,416),(209,394),
        (104,472),(112,408),(22,482),(50,313),(10,327),(90,207),(57,211),(135,110)]
JAW = [(303,212),(458,237),(334,246),(288,280),(274,350),(234,392),(239,272)]
EYE = [(228,140),(345,165),(266,186)]
# facets (drawn over the base fill, all inside the silhouette)
F = [
 ("#43E8FC", [(63,30),(284,80),(240,122)]),
 ("#12CDF2", [(63,30),(240,122),(205,118),(135,110)]),
 ("#30E2FA", [(284,80),(348,128),(361,152),(345,165),(240,122)]),
 ("#06B4E2", [(205,118),(252,135),(228,140)]),
 ("#2DDCF8", [(57,211),(135,110),(205,118),(150,195),(90,207)]),
 ("#07BDE8", [(90,207),(150,195),(115,270),(10,327)]),
 ("#12D6F8", [(150,195),(205,118),(228,140),(266,186),(205,237)]),
 ("#00ADDC", [(302,203),(205,237),(115,400),(104,472),(209,394),(211,416),(229,398),(233,270)]),
 ("#08CCF2", [(150,195),(205,237),(115,400),(112,408),(50,313),(115,270)]),
 ("#06BCE6", [(10,327),(115,270),(50,313)]),
 ("#02C6EE", [(50,313),(112,408),(22,482)]),
 ("#3EE6FA", [(361,152),(446,186),(502,237),(380,190)]),
 ("#0ACDF2", [(361,152),(380,190),(502,237),(302,203),(345,165)]),
 ("#05B8E4", [(266,186),(345,165),(302,203),(205,237)]),
]
JF = [("#24DAF8", [(303,212),(458,237),(334,246)]),
      ("#00ACDC", [(303,212),(334,246),(288,280),(239,300),(239,272)]),
      ("#10D2F4", [(239,300),(288,280),(274,350),(234,392)])]
EDGE = "#0BA3CC"; DARK = "#07090A"; EMBER = "#FF7A1A"; CYAN = "#22E6D0"
VB = 'viewBox="0 0 512 512"'

def full(defs=True):
    s = f'<g stroke="{EDGE}" stroke-width="3" stroke-linejoin="round"><path fill="#10D0F4" d="{P(BODY)}"/><path fill="#10D0F4" d="{P(JAW)}"/></g>'
    s += "".join(f'<path fill="{c}" d="{P(p)}"/>' for c, p in F + JF)
    s += f'<g stroke="{EDGE}" stroke-width="1.5" stroke-linejoin="round" fill="none"><path d="{P(BODY)}"/><path d="{P(JAW)}"/></g>'
    s += f'<path fill="{DARK}" d="{P(EYE)}"/><circle cx="272" cy="166.5" r="10" fill="{EMBER}"/>'
    return s
def mono(color="#22E6D0"):
    return (f'<path fill="{color}" fill-rule="evenodd" d="{P(BODY)} {P(EYE)}"/><path fill="{color}" d="{P(JAW)}"/>'
            f'<circle cx="272" cy="166.5" r="10" fill="{color}"/>')
# favicon: fewer points, thicker eye, chunkier gaps
FAV_BODY = [(56,34),(290,84),(362,150),(500,236),(300,206),(236,272),(232,420),(110,470),(116,404),(24,480),(60,300),(14,326),(96,206),(60,212),(136,112)]
FAV_JAW = [(306,220),(456,238),(290,286),(244,400),(248,278)]
FAV_EYE = [(222,138),(350,164),(262,194)]
def favicon():
    return (f'<path fill="#12CFF4" d="{P(FAV_BODY)}"/><path fill="#43E8FC" d="{P([(56,34),(290,84),(362,150),(240,124)])}"/>'
            f'<path fill="#00ADDC" d="{P([(300,206),(205,240),(110,470),(232,420),(236,272)])}"/>'
            f'<path fill="#12CFF4" d="{P(FAV_JAW)}"/><path fill="{DARK}" d="{P(FAV_EYE)}"/><circle cx="270" cy="169" r="14" fill="{EMBER}"/>')
def svg(body, vb=VB, w=None, h=None, title="RogueIQ"):
    wh = f' width="{w}" height="{h}"' if w else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" {vb}{wh} role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n'

def text_path(txt, font, size, x, y, fill):
    gs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font["head"].unitsPerEm; sc = size / upm
    out = []; hm = font["hmtx"]
    for ch in txt:
        g = cmap[ord(ch)]; pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x, y)))
        out.append(f'<path fill="{fill}" d="{pen.getCommands()}"/>'); x += hm[g][0] * sc
    return "".join(out), x

def main():
    os.makedirs(OUT, exist_ok=True)
    w = lambda n, s: open(os.path.join(OUT, n), "w").write(s)
    w("raven.svg", svg(full())); w("raven-mono.svg", svg(mono("#22E6D0")))
    w("raven-favicon.svg", svg(favicon()))
    f = TTFont(f"{KIT}/fonts/Archivo[wdth,wght].ttf")
    f = instantiateVariableFont(f, {"wdth": 125, "wght": 800})
    a, x = text_path("Rogue", f, 300, 560, 365, "#F5EFE6")
    b, x = text_path("IQ", f, 300, x, 365, CYAN)
    W = int(x + 30)
    w("wordmark.svg", svg(f'<g>{full()}</g>{a}{b}', vb=f'viewBox="0 0 {W} 512"', title="RogueIQ"))
    w("wordmark-dark-text.svg", svg(f'<g>{full()}</g>{a.replace("#F5EFE6","#07090A")}{b.replace(CYAN,"#0EA5A4")}', vb=f'viewBox="0 0 {W} 512"', title="RogueIQ"))
main()
