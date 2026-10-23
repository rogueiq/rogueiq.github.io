"""Eye fix for the ORIGINAL raster raven (Oct 23, 2026).
Master: raven-source.jpg (1024). The ember eye is redrawn smaller, with a tighter glow, centred on the socket's
largest inscribed circle so core + glow sit fully inside the dark socket with a dark margin all round.
Everything outside the socket is untouched. Originals are kept in src/orig/.
"""
import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(L, "src", "orig")
CORE = np.array([252, 102, 8]); GLOW = np.array([255, 106, 26])

def bfs(sel, seed):
    r = np.zeros_like(sel); r[seed[1], seed[0]] = True
    while True:
        n = r.copy(); n[1:] |= r[:-1]; n[:-1] |= r[1:]; n[:, 1:] |= r[:, :-1]; n[:, :-1] |= r[:, 1:]; n &= sel
        if (n == r).all(): return r
        r = n

def eye_layer(shape, cx, cy, rc, rg, ss=8):
    """Returns (rgb, alpha) of the eye: solid core radius rc, glow fading to 0 at rg. Supersampled."""
    h, w = shape
    yy, xx = np.mgrid[0:h * ss, 0:w * ss]
    d = np.hypot((xx + .5) / ss - cx, (yy + .5) / ss - cy)
    core = (d <= rc).astype(float)
    t = np.clip(1 - (d - rc) / (rg - rc), 0, 1); glow = .55 * t ** 2 * (d > rc)
    a = np.maximum(core, glow)
    a = a.reshape(h, ss, w, ss).mean((1, 3)); c = core.reshape(h, ss, w, ss).mean((1, 3))
    rgb = (CORE[None, None] * c[..., None] + GLOW[None, None] * (a - c)[..., None] * .9) / np.maximum(a, 1e-6)[..., None]
    return np.clip(rgb, 0, 255), a

# ---------- 1) master: raven-source.jpg ----------
S = np.array(Image.open(f"{O}/raven-source.jpg").convert("RGB")).astype(float)
box = (480, 300, 740, 460); x0, y0, x1, y1 = box
sub = S[y0:y1, x0:x1]
sock = bfs(sub[:, :, 2] < 110, (586 - x0, 384 - y0))
yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
hole = sock & ((np.hypot(xx - (586 - x0), yy - (384 - y0)) < 33) | (sub[:, :, 0] > 6))
base = np.median(sub[sock & ~hole], axis=0)
# inpaint the old eye by diffusion from the surrounding socket pixels (keeps the socket's natural shading)
known = sock & ~hole; sub[hole] = base
for _ in range(1500):
    acc = np.zeros_like(sub); cnt = np.zeros(sub.shape[:2])
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        m = np.roll(sock, (dy, dx), (0, 1)); acc += np.roll(sub, (dy, dx), (0, 1)) * m[..., None]; cnt += m
    upd = acc / np.maximum(cnt, 1)[..., None]
    sub[hole] = upd[hole]
CX, CY, RC, RG = 584.0, 385.0, 11.0, 19.0          # socket inscribed r = 29.7 here -> >=10 px dark margin
rgb, a = eye_layer(sub.shape[:2], CX - x0, CY - y0, RC, RG)
a = a * sock                                          # never paint outside the socket
sub[:] = sub * (1 - a[..., None]) + rgb * a[..., None]
S[y0:y1, x0:x1] = sub
src = Image.fromarray(S.round().astype(np.uint8)); src.save(f"{L}/raven-source.jpg", quality=95)

# ---------- 2) raven.png (512, transparent socket): same eye, mapped from the master ----------
k = 0.7514; mx = lambda x: (x - 230) * k + 9; my = lambda y: (y - 211) * 0.7508 + 30
P = np.array(Image.open(f"{O}/raven.png")).astype(float)
bx0, by0, bx1, by1 = 200, 100, 380, 220
ps = P[by0:by1, bx0:bx1]
psock = bfs((ps[:, :, 3] < 100) | (ps[:, :, 0] > ps[:, :, 2] + 10), (276 - bx0, 160 - by0))
ps[psock & ((ps[:, :, 0] > ps[:, :, 2] + 10) | (ps[:, :, 3] < 100))] = 0     # back to a clear (transparent) socket
rgb, a = eye_layer(ps.shape[:2], mx(CX) - bx0, my(CY) - by0, RC * k, RG * k)
a = a * psock
ps[..., :3] = np.where(a[..., None] > 0, rgb, ps[..., :3]); ps[..., 3] = np.maximum(ps[..., 3], a * 255)
P[by0:by1, bx0:bx1] = ps
png = Image.fromarray(P.round().astype(np.uint8), "RGBA"); png.save(f"{L}/raven.png", optimize=True)

# ---------- 3) derivatives ----------
def rs(im, n): return im.resize((n, n), Image.LANCZOS)
rs(png, 180).save(f"{L}/raven-180.png", optimize=True); r64 = rs(png, 64); r64.save(f"{L}/raven-64.png", optimize=True)
for d in ("/workspace/newsfeed/public/icons/raven-64.png", "/workspace/networth-by-age/raven-64.png"):
    r64.save(d, optimize=True)
def icon(n):
    bg = Image.new("RGBA", (n, n), (7, 9, 10, 255)); s = round(n * 406 / 512); o = (n - s) // 2
    bg.alpha_composite(rs(png, s), (o, o)); return bg.convert("RGB")
for n in (192, 512): icon(n).save(f"/workspace/newsfeed/public/icons/icon-{n}.png", optimize=True)
icon(180).save(f"{L}/apple-touch-icon.png", optimize=True)
png.save("/workspace/newsfeed/public/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
png.save(f"{L}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

# ---------- 4) 1024 / 2048 exports of the raster (from the fixed master) ----------
os.makedirs(f"{L}/png", exist_ok=True)
crop = src.crop((218, 171, 899, 852))                       # same framing as raven.png
c = np.array(crop).astype(float); bgc = np.median(np.array(src)[:40, :40].reshape(-1, 3), axis=0)
al = np.clip(np.abs(c - bgc).max(2) / 60, 0, 1)
un = np.clip((c - bgc * (1 - al[..., None])) / np.maximum(al, 1e-3)[..., None], 0, 255)
tr = Image.fromarray(np.dstack([un, al * 255]).round().astype(np.uint8), "RGBA")
for n in (1024, 2048):
    t = rs(tr, n); t.save(f"{L}/png/raven-original-{n}-transparent.png", optimize=True)
    dk = Image.new("RGBA", (n, n), (7, 9, 10, 255)); dk.alpha_composite(t); dk.convert("RGB").save(f"{L}/png/raven-original-{n}-dark.png", optimize=True)
print("socket base", base.round(), "png eye centre", round(mx(CX), 2), round(my(CY), 2))
