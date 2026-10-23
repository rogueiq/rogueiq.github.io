// rogueiq.com: static site + checker from assets; /wire/* goes to the rogueiq-feed Worker;
// /networth-by-age/api/* and /networth-by-age/mcp go to the rogueiq-tools Worker (net worth API + MCP).
const NW = "/networth-by-age";
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.protocol === "http:" || url.hostname === "www.rogueiq.com") return Response.redirect(`https://rogueiq.com${url.pathname}${url.search}`, 301);
    if (url.pathname === "/wire" || url.pathname.startsWith("/wire/")) return env.FEED.fetch(req);
    if (url.pathname === `${NW}/mcp`) return tools(req, env, "/mcp");
    if (url.pathname === `${NW}/api` || url.pathname === `${NW}/api/` || url.pathname === `${NW}/api/docs`) return Response.redirect("https://rogueiq.com/agents/#networth", 301);
    if (url.pathname.startsWith(`${NW}/api/`)) return tools(req, env, url.pathname.slice(`${NW}/api`.length));
    return env.ASSETS.fetch(req);
  },
};
function tools(req, env, path) {
  const u = new URL(req.url); u.pathname = path;
  return env.TOOLS.fetch(new Request(u.toString(), req));
}
