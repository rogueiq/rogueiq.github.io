#!/bin/sh
# Build the site + bundle the net-worth checker into dist/, then deploy the rogueiq-site Worker.
set -e
cd "$(dirname "$0")"
python3 build.py
rm -rf dist && mkdir -p dist/networth-by-age
cp -r index.html assets blog charts llms.txt robots.txt sitemap.xml dist/
for f in index.html app.js data.js style.css; do cp ../networth-by-age/$f dist/networth-by-age/; done
sed -i 's#https://rogueiq.github.io/#https://rogueiq.com/#g' dist/networth-by-age/index.html
env -u CLOUDFLARE_API_TOKEN npx -y wrangler@4.86.0 deploy "$@"
