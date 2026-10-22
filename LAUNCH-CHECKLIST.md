# rogueiq.com launch checklist

Do these steps only after Alan gives the final go. Times are America/New_York.

## State as of Oct 22, 2026
- The homepage is ready on branch `redesign`, committed locally only. `main` is untouched.
- The feed is live at https://feed.rogueiq.com. It is a Cloudflare Workers custom domain, separate from the apex and www.
- `rogueiq.com` and `www` are proxied through Cloudflare. Both currently return **HTTP 525 (SSL handshake failed)**, so the old Webflow site is already down.
- The real records can't be seen from outside, because public DNS only shows Cloudflare proxy IPs (104.21.9.116, 172.67.189.59).

## Records to replace (confirm in Cloudflare > rogueiq.com > DNS > Records)
Expected Webflow records. **Screenshot or export the real ones first (DNS > Records > Export) for rollback.**
| Type | Name | Expected Webflow value |
|---|---|---|
| A | rogueiq.com (@) | 75.2.70.75 (and/or 99.83.190.102), or a CNAME to proxy-ssl.webflow.com |
| CNAME | www | proxy-ssl.webflow.com (or proxy.webflow.com) |
| TXT | _webflow | one-time-verification=... (delete) |
Leave untouched: `feed` (Worker custom domain), and all MX, SPF, DKIM and email TXT records.

## Steps
1. **Back up:** export the DNS zone file from Cloudflare.
2. **Merge and push:**
   ```
   cd /workspace/rogueiq-site
   git checkout main && git pull
   git merge --no-ff redesign -m "Launch redesign"
   echo rogueiq.com > CNAME && git add CNAME && git commit -m "Custom domain"
   git push origin main
   ```
3. **GitHub Pages:** repo Settings > Pages. Source: main / root. Custom domain: `rogueiq.com`. Leave "Enforce HTTPS" for step 6.
4. **Cloudflare DNS:** delete the Webflow records and add:
   | Type | Name | Value | Proxy |
   |---|---|---|---|
   | A | @ | 185.199.108.153 | DNS only (grey) |
   | A | @ | 185.199.109.153 | DNS only |
   | A | @ | 185.199.110.153 | DNS only |
   | A | @ | 185.199.111.153 | DNS only |
   | AAAA | @ | 2606:50c0:8000::153, 8001::153, 8002::153, 8003::153 | DNS only |
   | CNAME | www | rogueiq.github.io | DNS only |
   Keep the records grey (DNS only) until GitHub issues the certificate.
5. **Wait for the DNS check:** wait until GitHub Pages shows "DNS check successful". This usually takes a few minutes and can take up to 1 hour.
6. **SSL:**
   - When the certificate is issued, tick "Enforce HTTPS".
   - Optional: turn the Cloudflare proxy on (orange) with SSL mode set to **Full (strict)**. Never use Flexible.
7. **Verify:**
   - `curl -sI https://rogueiq.com` → 200
   - `curl -sI https://www.rogueiq.com` → 301 to rogueiq.com
   - Check the homepage on mobile.
   - Check that the Wire preview loads.
   - Check https://rogueiq.com/llms.txt and https://feed.rogueiq.com/mcp.

## Rollback
- **Site:** `git revert -m 1 <merge-sha> && git push origin main`. Or point Pages at the previous commit.
- **DNS:** delete the GitHub records and re-import or re-add the exported Webflow records. Note that Webflow was already returning 525, so rolling back restores a broken site. The safer fallback is to keep the GitHub records and revert the content.
- **Feed:** no change is needed. To detach the feed domain, remove `routes` from `newsfeed/wrangler.jsonc` and redeploy, or use Workers > rogueiq-feed > Settings > Domains.
