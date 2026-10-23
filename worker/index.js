// rogueiq.com: static site + checker from assets; /wire/* goes to the rogueiq-feed Worker;
// /net-worth-by-age/api/* and /net-worth-by-age/mcp go to the rogueiq-tools Worker (net worth API + MCP).
// Old /networth-by-age/* paths: GETs 301 to the new path; POST/MCP and API calls keep answering directly
// (agents often don't follow redirects on POST), same approach as feed.rogueiq.com.
const NW = "/net-worth-by-age";
const OLD = "/networth-by-age";
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.protocol === "http:" || url.hostname === "www.rogueiq.com") return Response.redirect(`https://rogueiq.com${url.pathname}${url.search}`, 301);
    if (url.pathname === "/wire" || url.pathname.startsWith("/wire/")) return env.FEED.fetch(req);
    let p = url.pathname;
    if (p === OLD || p.startsWith(OLD + "/")) {
      const rest = p.slice(OLD.length);
      const direct = (rest === "/mcp" && req.method !== "GET") || (rest.startsWith("/api/v1/") && req.method !== "GET") || req.method === "OPTIONS";
      if (!direct) return Response.redirect(`https://rogueiq.com${NW}${rest || "/"}${url.search}`, 301);
      p = NW + rest;
    }
    if (p === `${NW}/mcp`) return tools(req, env, "/mcp");
    if (p === `${NW}/api` || p === `${NW}/api/` || p === `${NW}/api/docs`) return Response.redirect("https://rogueiq.com/agents/#networth", 301);
    if (p.startsWith(`${NW}/api/`)) return tools(req, env, p.slice(`${NW}/api`.length));
    return env.ASSETS.fetch(req);
  },
};
function tools(req, env, path) {
  const u = new URL(req.url); u.pathname = path;
  return env.TOOLS.fetch(new Request(u.toString(), req));
}
