#!/usr/bin/env python3
"""
build.py: turns the files in content/ into the website. No installs needed (plain Python 3).

  python3 build.py            -> builds the real site (drafts left out)
  python3 build.py --preview  -> also builds drafts, marked DRAFT and hidden from Google, for local review only

It writes: index.html, blog/, blog/<post>/index.html, blog/rss.xml, sitemap.xml, robots.txt, llms.txt
"""
import html, json, re, shutil, sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent
C = ROOT / "content"
SITE = json.loads((C / "site.json").read_text())
BASE = SITE["url"].rstrip("/")
PREVIEW = "--preview" in sys.argv
esc = html.escape

# ---------- tiny front matter + markdown ----------
def parse(path):
    text = path.read_text()
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    return meta, body

def inline(s):
    s = esc(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{esc(m.group(2))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\s)(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s

def markdown(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out, blocks = [], re.split(r"\n\s*\n", md.strip())
    for b in blocks:
        lines = b.strip().splitlines()
        if not lines: continue
        h = re.match(r"^(#{1,4})\s+(.*)", lines[0])
        if h and len(lines) == 1:
            n = len(h.group(1)) + (1 if len(h.group(1)) == 1 else 0)
            out.append(f"<h{n}>{inline(h.group(2))}</h{n}>")
        elif all(re.match(r"^[-*]\s+", l) for l in lines):
            out.append("<ul>" + "".join(f"<li>{inline(l[2:].strip())}</li>" for l in lines) + "</ul>")
        elif all(re.match(r"^\d+\.\s+", l) for l in lines):
            out.append("<ol>" + "".join(f"<li>{inline(re.sub(r'^\d+\.\s+', '', l))}</li>" for l in lines) + "</ol>")
        elif lines[0].startswith("|") and len(lines) > 1 and re.match(r"^\|[\s:|-]+\|$", lines[1]):
            cells = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
            head = "".join(f"<th>{inline(c)}</th>" for c in cells(lines[0]))
            rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(l)) + "</tr>" for l in lines[2:])
            out.append(f'<div class="table"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    return "\n".join(out)

def nice(d):  # 2026-10-19 -> Oct 19, 2026
    return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d, %Y")

# ---------- load content ----------
posts = []
for p in sorted((C / "posts").glob("*.md")):
    meta, body = parse(p)
    draft = meta.get("draft", "false").lower() == "true"
    if draft and not PREVIEW: continue
    posts.append(dict(slug=p.stem, title=meta["title"], date=meta["date"], desc=meta.get("description", ""),
                      draft=draft, html=markdown(body)))
posts.sort(key=lambda x: x["date"], reverse=True)
live_posts = [p for p in posts if not p["draft"]]

timeline = []
for p in sorted((C / "timeline").glob("*.md")):
    meta, body = parse(p)
    timeline.append(dict(date=meta["date"], link=meta.get("link", ""), text=body.strip()))
timeline.sort(key=lambda x: x["date"], reverse=True)

# ---------- page shell ----------
ORG = {"@type": "Organization", "@id": BASE + "/#org", "name": SITE["name"], "url": BASE + "/",
       "sameAs": [SITE["x"], SITE["github"]]}

def page(path, title, desc, body, jsonld, og_type="website", noindex=False):
    url = BASE + path
    ld = json.dumps({"@context": "https://schema.org", "@graph": jsonld}, ensure_ascii=False)
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="RogueIQ">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<meta name="twitter:site" content="@rogueiq">
<meta name="theme-color" content="#000000">
<link rel="alternate" type="application/rss+xml" title="RogueIQ blog" href="/blog/rss.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 16 16%22%3E%3Ccircle cx=%228%22 cy=%228%22 r=%226%22 fill=%22%2300e676%22/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap">
  <a class="logo" href="/">Rogue<span>IQ</span></a>
  <nav aria-label="Main"><a href="/#tools">Tools</a><a href="/#log">Log</a><a href="/blog/">Blog</a><a class="tag" href="{SITE['x']}">@rogueiq</a></nav>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="wrap foot">
  <p>Educational tools only, not financial advice.</p>
  <p><a href="{SITE['x']}">@rogueiq</a> · <a href="/blog/rss.xml">RSS</a> · <a href="/llms.txt">llms.txt</a></p>
</footer>
</body>
</html>
"""

def write(rel, text):
    f = ROOT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)

# ---------- home ----------
def tool_html(t):
    live = t["status"] == "Live"
    badge = f'<span class="badge {"live" if live else "soon"}">{esc(t["status"])}</span>'
    inner = f'<div><h3>{esc(t["name"])}</h3><p>{esc(t["summary"])}</p></div>{badge}'
    return f'<li><a class="row" href="{t["url"]}">{inner}</a></li>' if t["url"] else f'<li><div class="row">{inner}</div></li>'

def log_html(e):
    text = esc(e["text"])
    if e["link"]: text = f'<a href="{esc(e["link"])}">{text}</a>'
    return (f'<li class="entry"><div class="who"><span class="dot" aria-hidden="true"></span><strong>RogueIQ</strong>'
            f'<span class="muted">@rogueiq · <time datetime="{e["date"]}">{nice(e["date"])}</time></span></div><p>{text}</p></li>')

# NEWSLETTER: see README "How to paste the beehiiv form".
NEWSLETTER = """<section class="news" id="newsletter" aria-labelledby="nl-h">
  <h2 id="nl-h">Follow the build</h2>
  <p class="muted">New tools and posts, by email. No spam.</p>
  <!-- ===== BEEHIIV EMBED GOES HERE =====
       1. In beehiiv: Grow > Subscribe Forms > pick a form > Get embed code.
       2. Delete everything between BEEHIIV-PLACEHOLDER-START and BEEHIIV-PLACEHOLDER-END below.
       3. Paste the beehiiv <iframe> snippet in its place, then run: python3 build.py
  -->
  <!-- BEEHIIV-PLACEHOLDER-START: "coming soon" form. It sends nothing anywhere. -->
  <form class="signup" action="#" onsubmit="this.querySelector('.note').hidden=false;return false;">
    <label class="sr" for="nl-email">Email address</label>
    <input id="nl-email" type="email" placeholder="you@email.com" autocomplete="email" disabled>
    <button type="submit">Coming soon</button>
    <p class="note muted" hidden>The newsletter isn't open yet.</p>
  </form>
  <!-- BEEHIIV-PLACEHOLDER-END -->
</section>"""

home_body = f"""<section class="hero">
  <h1>Rogue<span>IQ</span></h1>
  <p class="lead">{esc(SITE['tagline'])}</p>
</section>
<section id="tools" aria-labelledby="tools-h"><h2 id="tools-h">Tools</h2><ul class="list">{''.join(tool_html(t) for t in SITE['tools'])}</ul></section>
<section id="log" aria-labelledby="log-h"><h2 id="log-h">Build log</h2><ol class="timeline">{''.join(log_html(e) for e in timeline)}</ol></section>
{"<section aria-labelledby='bl-h'><h2 id='bl-h'>From the blog</h2><ul class='list posts'>" + ''.join(f'<li><a class="row" href="/blog/{p["slug"]}/"><div><h3>{esc(p["title"])}</h3><p><time datetime="{p["date"]}">{nice(p["date"])}</time></p></div></a></li>' for p in posts[:3]) + "</ul></section>" if posts else ""}
{NEWSLETTER}"""
write("index.html", page("/", "RogueIQ | Simple tools built on public data", SITE["description"], home_body,
      [ORG, {"@type": "WebSite", "@id": BASE + "/#site", "name": "RogueIQ", "url": BASE + "/", "publisher": {"@id": BASE + "/#org"}}]))

# ---------- blog ----------
shutil.rmtree(ROOT / "blog", ignore_errors=True)
def post_item(p):
    d = ' <span class="badge soon">Draft</span>' if p["draft"] else ""
    return f'<li><a class="row" href="/blog/{p["slug"]}/"><div><h3>{esc(p["title"])}{d}</h3><p>{esc(p["desc"])}</p><p class="muted"><time datetime="{p["date"]}">{nice(p["date"])}</time></p></div></a></li>'
blog_body = f'<section class="hero small"><h1>Blog</h1><p class="lead">How our tools work, and what we learn building them.</p></section><ul class="list posts">{"".join(post_item(p) for p in posts) or "<li class=muted>First posts coming soon.</li>"}</ul>'
write("blog/index.html", page("/blog/", "Blog | RogueIQ", "Notes from RogueIQ on how our data tools work and what we're building.", blog_body,
      [ORG, {"@type": "Blog", "name": "RogueIQ Blog", "url": BASE + "/blog/", "publisher": {"@id": BASE + "/#org"}}]))
for p in posts:
    url = f"/blog/{p['slug']}/"
    banner = '<p class="draft">DRAFT: not published. Hidden from search, sitemap and RSS.</p>' if p["draft"] else ""
    body = f'<article class="post">{banner}<p class="muted"><a href="/blog/">← Blog</a></p><h1>{esc(p["title"])}</h1><p class="muted"><time datetime="{p["date"]}">{nice(p["date"])}</time></p>{p["html"]}</article>'
    write(f"blog/{p['slug']}/index.html", page(url, f"{p['title']} | RogueIQ", p["desc"], body,
          [ORG, {"@type": "BlogPosting", "headline": p["title"], "description": p["desc"], "datePublished": p["date"],
                 "url": BASE + url, "mainEntityOfPage": BASE + url, "author": {"@id": BASE + "/#org"}, "publisher": {"@id": BASE + "/#org"}}],
          og_type="article", noindex=p["draft"]))

# ---------- RSS, sitemap, robots, llms ----------
def rfc822(d): return datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 +0000")
items = "".join(f"<item><title>{esc(p['title'])}</title><link>{BASE}/blog/{p['slug']}/</link><guid>{BASE}/blog/{p['slug']}/</guid><pubDate>{rfc822(p['date'])}</pubDate><description>{esc(p['desc'])}</description></item>" for p in live_posts)
write("blog/rss.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>RogueIQ Blog</title><link>{BASE}/blog/</link><atom:link href="{BASE}/blog/rss.xml" rel="self" type="application/rss+xml"/><description>Notes from RogueIQ.</description><language>en-us</language>{items}</channel></rss>\n')

today = date.today().isoformat()
urls = [("/", today), ("/blog/", today)] + [(t["url"], today) for t in SITE["tools"] if t["url"]] + [(f"/blog/{p['slug']}/", p["date"]) for p in live_posts]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")

llms = [f"# RogueIQ\n", f"> RogueIQ ({BASE.replace('https://','')}) builds simple tools from public data. Tools run in the browser; user inputs are not sent or stored. Educational only, not financial advice.\n", "## Tools\n"]
llms += [f"- [{t['name']}]({BASE}{t['url']}): {t['summary']}" if t["url"] else f"- {t['name']} (status: {t['status']}, not yet available): {t['summary']}" for t in SITE["tools"]]
llms += ["\n## Blog\n", f"- [Blog index]({BASE}/blog/)", f"- [RSS feed]({BASE}/blog/rss.xml)"]
llms += [f"- [{p['title']}]({BASE}/blog/{p['slug']}/): {p['desc']}" for p in live_posts]
llms += ["\n## Build log\n"] + [f"- {e['date']}: {e['text']}" for e in timeline]
write("llms.txt", "\n".join(llms) + "\n")

print(f"Built: {len(posts)} post(s) ({len(posts)-len(live_posts)} draft), {len(timeline)} log entries" + (" [PREVIEW: drafts included, do not publish]" if PREVIEW else ""))
