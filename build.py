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
ORG = {"@type": "Organization", "@id": BASE + "/#org", "name": SITE["name"], "url": BASE + "/", "slogan": SITE["tagline"], "description": SITE["description"],
       "sameAs": [SITE["x"], SITE["github"]]}

def page(path, title, desc, body, jsonld, og_type="website", noindex=False, og_image=None):
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
<meta name="twitter:card" content="{'summary_large_image' if og_image else 'summary'}">
{f'<meta property="og:image" content="{BASE}{og_image}">' if og_image else ''}
<meta name="twitter:site" content="@rogueiq">
<meta name="theme-color" content="#07090A">
<link rel="alternate" type="text/plain" title="llms.txt" href="/llms.txt">
<link rel="alternate" type="application/rss+xml" title="RogueIQ blog" href="/blog/rss.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 16 16%22%3E%3Ccircle cx=%228%22 cy=%228%22 r=%226%22 fill=%22%2322E6D0%22/%3E%3C/svg%3E">
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
  <nav aria-label="Main"><a href="/#wire">The Wire</a><a href="/#agents">Agents</a></nav>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="wrap foot">
  <ul class="trust"><li><a href="https://rogueiq-feed.rogueiq.workers.dev/v1/sources">Sources</a></li><li><a href="/llms.txt">Methodology</a></li><li>No picks or buy/sell calls</li></ul>
  <!-- EMAIL: placeholder form. Replace action with the beehiiv embed/endpoint when set up. -->
  <form class="email" action="#" onsubmit="event.preventDefault();this.querySelector('p').hidden=false"><label for="em" class="muted small">Get updates by email</label>
    <div><input id="em" type="email" placeholder="you@example.com" required><button type="submit">Subscribe</button></div><p class="muted small" hidden>Thanks. Email signup opens soon.</p></form>
  <p class="disc">{esc(SITE['disclaimer'])}</p>
  <p><a href="{SITE['x']}">@rogueiq</a> · <a href="/blog/">Guides</a> · <a href="/blog/rss.xml">RSS</a> · <a href="{SITE['agents']['docs']}">For AI agents</a> · <a href="/llms.txt">llms.txt</a></p>
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

# NEWSLETTER: see README "How to paste the beehiiv form". This is the main call to action.
NL = SITE["newsletter"]
NEWSLETTER = f"""<div class="news" id="newsletter">
  <h2 id="nl-h">{esc(NL['title'])}</h2>
  <p class="muted">Free. Unsubscribe any time.</p>
  <!-- ===== BEEHIIV EMBED GOES HERE =====
       1. In beehiiv: Grow > Subscribe Forms > pick a form > Get embed code.
       2. Delete everything between BEEHIIV-PLACEHOLDER-START and BEEHIIV-PLACEHOLDER-END below.
       3. Paste the beehiiv <iframe> snippet in its place, then run: python3 build.py
  -->
  <!-- BEEHIIV-PLACEHOLDER-START: placeholder form. It sends nothing anywhere. -->
  <form class="signup" action="#" onsubmit="this.querySelector('.note').hidden=false;return false;">
    <label class="sr" for="nl-email">Email address</label>
    <input id="nl-email" type="email" placeholder="you@email.com" autocomplete="email">
    <button type="submit">{esc(NL['button'])}</button>
    <p class="note muted" hidden>Signup opens soon. This form isn't connected yet, so nothing was sent or saved.</p>
  </form>
  <!-- BEEHIIV-PLACEHOLDER-END -->
</div>"""

def log_html(e):
    text = esc(e["text"])
    if e["link"]: text = f'<a href="{esc(e["link"])}">{text}</a>'
    return (f'<li class="entry"><div class="who"><span class="dot" aria-hidden="true">R</span><strong>RogueIQ</strong>'
            f'<span class="muted">@rogueiq · <time datetime="{e["date"]}">{nice(e["date"])}</time></span></div><p>{text}</p></li>')

def chart_html(c):
    srcs = " · ".join(f'<a href="{esc(x["url"])}">{esc(x["label"])}</a>' if x.get("url") else esc(x["label"]) for x in c["sources"])
    note = f'<p class="cnote">{esc(c["note"])}</p>' if c.get("note") else ""
    return (f'<li class="chart" id="{esc(c["id"])}"><figure><img src="{esc(c["img"])}" alt="{esc(c["alt"])}" loading="lazy" decoding="async">'
            f'<figcaption><h3>{esc(c["title"])}</h3><p class="take">{esc(c["takeaway"])}</p>{note}<p class="src"><span>Sources</span> {srcs}</p>'
            f'<p class="asof">{esc(c.get("as_of") or "As of " + nice(c["date"]))}</p></figcaption></figure></li>')

def chart_ld(c):
    return {"@type": "ImageObject", "name": c["title"], "caption": c["takeaway"], "contentUrl": BASE + c["img"], "description": c["alt"], "datePublished": c["date"],
            "creator": {"@id": BASE + "/#org"}, "isBasedOn": [x["url"] for x in c["sources"] if x.get("url")] or None, "citation": [x["label"] for x in c["sources"]]}

hook = SITE["hook"]; wl = SITE["waitlist"]; AG = SITE["agents"]; st = SITE["start"]; LD = SITE["live_data"]
checker = SITE["tools"][0]
MINI = f"""<div class="mini" id="try">
  <h2 class="mini-h">{esc(hook['label'])}</h2>
  <form id="mini-check" class="mini-form" novalidate>
    <div class="mf"><label><span>Your age</span><input name="age" type="number" inputmode="numeric" min="18" max="110" placeholder="34" autocomplete="off"></label>
      <div class="slider-row"><input class="slider" name="age_s" type="range" min="18" max="95" step="1" value="35" aria-label="Age slider"><output class="slider-out" data-for="age"></output></div></div>
    <div class="mf"><label><span>Net worth (US $)</span><input name="nw" type="text" inputmode="decimal" placeholder="150,000" autocomplete="off"></label>
      <div class="slider-row"><input class="slider" name="nw_s" type="range" aria-label="Net worth slider, -$1M to $50M+ in uneven steps"><output class="slider-out" data-for="nw"></output></div></div>
    <button type="submit">Check</button>
  </form>
  <p id="mini-error" class="mini-err" role="alert" hidden></p>
  <div id="mini-result" class="mini-result" aria-live="polite" hidden>
    <p class="mr-head"></p><p class="mr-detail"></p><p class="mr-median muted"></p>
    <p><a href="{esc(checker['url'])}">Full breakdown, chart and filters →</a></p>
  </div>
  <p class="muted mini-note">Slide for a quick answer or type an exact amount. {esc(hook['note'])}</p>
</div>"""
cards = "".join(f'<li><a class="card" href="{esc(c["url"])}"><h3>{esc(c["q"])}</h3><p>{esc(c["a"])}</p><span class="go">Find out →</span></a></li>' for c in st["cards"])
toolcards = "".join(f'<li><a class="card" href="{esc(t["url"])}"><span class="badge live">{esc(t["status"])}</span><h3>{esc(t["question"])}</h3><p class="preview">{esc(t["preview"])}</p><p class="muted small">{esc(t["name"])} · Web, API and MCP</p></a></li>' for t in SITE["tools"])
home_charts = [c for c in SITE["charts"] if c.get("home")]
FEED = "https://rogueiq-feed.rogueiq.workers.dev"
MCP = "https://rogueiq-tools.rogueiq.workers.dev/mcp"
SNIP = '{\n  "mcpServers": {\n    "rogueiq": { "url": "' + MCP + '" }\n  }\n}'
home_body = f"""<section class="hero">
  <h1 class="shimmer">Get Smarter About Money.</h1>
  <p class="lead">Market tools and sourced news that show where you stand today. Built for you and your AI agent.</p>
  <p class="cta"><a class="btn ember" href="https://x.com/rogueiq">Follow along on X</a><a class="btn ghost" href="#agents">Connect your agent</a></p>
</section>
<section id="wire" aria-labelledby="wire-h"><h2 id="wire-h">The RogueIQ Wire</h2>
  <p class="big">Market-moving releases, from the source.</p>
  <p class="intro">For people who hold or trade stocks, follow macro or watch crypto. Releases from the Fed, BLS, BEA, SEC and other agencies, each with its source and date, so you can check the facts behind the headline.</p>
  <ol class="wire" id="wire-list" aria-live="polite"><li class="muted">Loading the latest official posts…</li></ol>
  <p class="cta"><a class="btn" href="{FEED}/">Open the full feed</a></p>
</section>
<section id="agents" class="agents" aria-labelledby="ag-h"><h2 id="ag-h">For agents</h2>
  <p class="big">Give your AI agent the same sourced data.</p>
  <ul class="aglist">
    <li><strong>MCP server</strong> <code>{MCP}</code></li>
    <li><strong>API docs</strong> <a href="{esc(AG['docs'])}">OpenAPI and examples →</a> · <a href="/llms.txt">llms.txt</a> · <a href="https://rogueiq-tools.rogueiq.workers.dev/SKILL.md">SKILL.md</a></li>
  </ul>
  <div class="snip"><pre class="code"><code id="snip">{esc(SNIP)}</code></pre><button type="button" class="copy" data-copy="snip">Copy</button></div>
</section>
<section id="tool" aria-labelledby="tool-h"><h2 id="tool-h">Market tool</h2>
  <div class="card solo"><span class="badge">Coming soon</span><h3>A market tool that shows where things stand</h3>
  <p>Our first indicator, built on public market data. It will show signals and leave the decisions to you.</p></div>
</section>
<script src="/assets/home.js" defer></script>"""
write("index.html", page("/", f"RogueIQ | {SITE['tagline']}", SITE["description"], home_body,
      [ORG, {"@type": "WebSite", "@id": BASE + "/#site", "name": "RogueIQ", "url": BASE + "/", "description": SITE["description"], "publisher": {"@id": BASE + "/#org"}},
       {"@type": "WebAPI", "name": "RogueIQ Tools API and MCP server", "url": AG["docs"], "documentation": AG["docs"], "termsOfService": BASE + "/",
        "description": "Free, read-only RogueIQ money tools for AI agents: JSON API, OpenAPI spec and a remote MCP server.", "provider": {"@id": BASE + "/#org"}},
       ]))

charts_body = f"""<section class="hero small"><p class="kicker">{esc(LD['kicker'])}</p><h1>Charts</h1><p class="lead">{esc(LD['text'])}</p></section>
<ul class="charts">{"".join(chart_html(c) for c in SITE["charts"])}</ul>"""
write("charts/index.html", page("/charts/", "Charts | RogueIQ", "RogueIQ charts from primary sources, each with a plain-English line on what it means and links to its sources.", charts_body,
      [ORG, {"@type": "CollectionPage", "name": "RogueIQ charts", "url": BASE + "/charts/", "publisher": {"@id": BASE + "/#org"}, "hasPart": [chart_ld(c) for c in SITE["charts"]]}],
      og_image=SITE["charts"][0]["img"]))

# ---------- blog ----------
shutil.rmtree(ROOT / "blog", ignore_errors=True)
def post_item(p):
    d = ' <span class="badge soon">Draft</span>' if p["draft"] else ""
    return f'<li><a class="row" href="/blog/{p["slug"]}/"><div><h3>{esc(p["title"])}{d}</h3><p>{esc(p["desc"])}</p><p class="muted"><time datetime="{p["date"]}">{nice(p["date"])}</time></p></div></a></li>'
blog_body = f'<section class="hero small"><h1>Guides</h1><p class="lead">Plain-language explainers built on primary-source public data, with every source linked.</p></section><ul class="list posts">{"".join(post_item(p) for p in posts) or "<li class=muted>First posts coming soon.</li>"}</ul>'
write("blog/index.html", page("/blog/", "Guides | RogueIQ", "Plain-language RogueIQ guides to the numbers behind money headlines, built on primary-source public data.", blog_body,
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
write("blog/rss.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>RogueIQ Blog</title><link>{BASE}/blog/</link><atom:link href="{BASE}/blog/rss.xml" rel="self" type="application/rss+xml"/><description>Plain-language RogueIQ guides built on primary-source public data.</description><language>en-us</language>{items}</channel></rss>\n')

today = date.today().isoformat()
urls = [("/", today), ("/charts/", today), ("/blog/", today)] + [(t["url"], today) for t in SITE["tools"] if t["url"].startswith("/")] + [(f"/blog/{p['slug']}/", p["date"]) for p in live_posts]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")

link = lambda u: u if u.startswith("http") else BASE + u
AG = SITE["agents"]
llms = [f"# RogueIQ\n", f"> {SITE['tagline']} {SITE['subline']}\n",
        f"Every tool is built once and works three ways: a web page for people, a JSON API, and an MCP server for agents. Web tools run in the browser; inputs stay on the device. {SITE['disclaimer']}\n",
        "## Tools\n"]
llms += [f"- [{t['name']}]({link(t['url'])}): {t['summary']} API: {t['api']}" for t in SITE["tools"]]
llms += ["\n## For AI agents\n", f"- [API and MCP docs]({AG['docs']})", f"- [MCP server (streamable HTTP, no auth)]({AG['mcp']})",
         f"- [OpenAPI spec]({AG['openapi']})", f"- [Tools llms.txt]({AG['llms']})", f"- [SKILL.md]({AG['skill']})"]
llms += ["\n## Charts (each chart lists its sources)\n", f"- [All charts]({BASE}/charts/)"]
llms += [f"- [{c['title']}]({BASE}/charts/#{c['id']}) ({c['date']}): {c['takeaway']} Sources: " + "; ".join(x['label'] + (f" <{x['url']}>" if x.get('url') else "") for x in c['sources']) for c in SITE["charts"]]
llms += ["\n## Guides\n", f"- [Guides index]({BASE}/blog/)", f"- [RSS feed]({BASE}/blog/rss.xml)"]
llms += [f"- [{p['title']}]({BASE}/blog/{p['slug']}/): {p['desc']}" for p in live_posts]
llms += ["\n## Build log\n"] + [f"- {e['date']}: {e['text']}" for e in timeline]
write("llms.txt", "\n".join(llms) + "\n")

print(f"Built: {len(posts)} post(s) ({len(posts)-len(live_posts)} draft), {len(timeline)} log entries" + (" [PREVIEW: drafts included, do not publish]" if PREVIEW else ""))
