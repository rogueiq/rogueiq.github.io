import sys, os, base64
from playwright.sync_api import sync_playwright
L = "/workspace/rogueiq-site/assets/logo"
def uri(p, mime): return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    def shot(html, w, h, out, transparent):
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.set_content(f'<html><body style="margin:0;background:{"transparent" if transparent else "#07090A"}">{html}</body></html>'); pg.wait_for_timeout(300)
        pg.screenshot(path=out, omit_background=transparent, clip={"x": 0, "y": 0, "width": w, "height": h}); pg.close()
    if "export" in sys.argv:
        for name in ["raven", "raven-mono", "raven-favicon", "wordmark"]:
            s = open(f"{L}/{name}.svg").read(); vb = s.split('viewBox="')[1].split('"')[0].split(); ar = float(vb[2]) / float(vb[3])
            for size in (1024, 2048):
                W, H = (int(size * ar), size) if ar > 1 else (size, size)
                img = f'<img src="{uri(f"{L}/{name}.svg","image/svg+xml")}" style="display:block;width:{W}px;height:{H}px">'
                for t in (True, False):
                    shot(img, W, H, f"{L}/png/{name}-{size}-{'transparent' if t else 'dark'}.png", t)
    if "compare" in sys.argv:
        o = uri(f"{L}/raven.png", "image/png"); n = uri(f"{L}/raven.svg", "image/svg+xml"); fv = uri(f"{L}/raven-favicon.svg", "image/svg+xml")
        cell = lambda src, s, lab: f'<div style="display:inline-block;vertical-align:top;margin:12px;text-align:center;color:#9A948C;font:14px sans-serif"><img src="{src}" style="width:{s}px;height:{s}px;display:block;margin:0 auto 6px">{lab}</div>'
        html = ('<div style="padding:12px">' + cell(o, 512, "original PNG, 512") + cell(n, 512, "new raven.svg, 512") + "</div>"
                '<div style="padding:12px">' + "".join(cell(a, s, f"{l} {s}px") for s in (32, 16) for a, l in ((o, "original"), (n, "raven.svg"), (fv, "favicon.svg"))) + "</div>"
                '<div style="padding:12px;color:#9A948C;font:14px sans-serif">Pixel-zoomed x4 (32px, then 16px): ' + "".join(f'<canvas data-src="{a}" data-s="{s}" width="{s}" height="{s}" style="width:{s*4}px;height:{s*4}px;image-rendering:pixelated;margin:0 10px;vertical-align:middle"></canvas>' for s in (32, 16) for a in (o, n, fv)) + "</div>"
                '<script>document.querySelectorAll("canvas").forEach(c=>{const i=new Image();i.onload=()=>c.getContext("2d").drawImage(i,0,0,+c.dataset.s,+c.dataset.s);i.src=c.dataset.src;});</script>')
        shot(html, 1100, 880, "/workspace/rogueiq-shots/svg-compare.png", False)
