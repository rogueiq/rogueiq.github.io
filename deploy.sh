#!/bin/sh
# Build the site + bundle the net-worth checker into dist/, then deploy the rogueiq-site Worker.
set -e
cd "$(dirname "$0")"
python3 build.py
python3 ../networth-by-age/scripts/build_page.py
rm -rf dist && mkdir -p dist/net-worth-by-age
cp -r index.html 404.html assets blog charts agents llms.txt robots.txt sitemap.xml sitemap-pages.xml dist/
for f in index.html app.js data.js style.css raven-64.png networth-by-age-2025.csv under-35 35-44 45-54 55-64 65-74 75-and-older; do cp -r ../networth-by-age/$f dist/net-worth-by-age/; done
sed -i 's#https://rogueiq.github.io/networth-by-age/#https://rogueiq.com/net-worth-by-age/#g; s#https://rogueiq.github.io/#https://rogueiq.com/#g' dist/net-worth-by-age/index.html
env -u CLOUDFLARE_API_TOKEN npx -y wrangler@4.86.0 deploy "$@"
