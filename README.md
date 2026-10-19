# rogueiq.com

The RogueIQ website. Plain files hosted free on GitHub Pages. `.nojekyll` must stay.

> **LAUNCH TODO: re-add `CNAME`.** The custom domain was removed on main (commit 499e10c) so the checker works at rogueiq.github.io until launch. At launch, add a `CNAME` file containing `rogueiq.com` and set the custom domain again in Settings → Pages.

You edit files in `content/`, then run one command that rebuilds the site:

```
python3 build.py
```

No installs needed. Never edit `index.html`, `blog/`, `sitemap.xml`, `llms.txt` or `robots.txt` by hand: `build.py` rewrites them.

## Preview on your computer

```
python3 build.py --preview      # includes drafts, marked DRAFT
python3 -m http.server 8000      # then open http://localhost:8000
```

Run `python3 build.py` (no `--preview`) again before committing, so drafts stay out.

## Add a build-log (timeline) entry

Make a new file in `content/timeline/`, named `YYYY-MM-DD-short-name.md`:

```
---
date: 2026-10-25
link: /some-page/
---
Shipped the thing, in one short sentence.
```

`link:` is optional (delete the line if there's no page). Newest shows first.

## Write a blog post

Make a new file in `content/posts/`. The file name becomes the address: `my-post.md` → `rogueiq.com/blog/my-post/`.

```
---
title: My post title
date: 2026-10-25
description: One sentence for Google and link previews.
draft: true
---
Write here. Blank line between paragraphs.

## A subheading

- a bullet
- **bold**, *italic*, [a link](https://example.com)
```

While `draft: true`, the post is left out of the site, sitemap, RSS and llms.txt (only `--preview` shows it). To publish, change it to `draft: false` and run `python3 build.py`.

## Add or change a tool

Edit the `tools` list in `content/site.json`. `status` is `Live` or `Building`; leave `url` empty for tools that aren't out yet. The tagline is in the same file.

## Paste the beehiiv form

1. In beehiiv: **Grow → Subscribe Forms**, pick a form, copy the embed code.
2. Open `build.py`, find `BEEHIIV EMBED GOES HERE`.
3. Delete everything from `BEEHIIV-PLACEHOLDER-START` to `BEEHIIV-PLACEHOLDER-END` and paste the beehiiv code there.
4. Run `python3 build.py`.

Until then the form shows "Coming soon" and sends nothing.

## Charts held back (compliance, Oct 19, 2026)
The SOXL "pros sold / crowd bought 3x" chart and the MSTR/Metaplanet MSCI chart are off /charts/ until each has named sources with links and dates (Warren's review). The images and scripts stay in `rogueiq/chart-archive/` (`pros-vs-crowd-cyan.png`, `msci-btc-cyan.png`). To bring one back, add it to `charts` in `content/site.json` with full sources and an `as_of` line.
