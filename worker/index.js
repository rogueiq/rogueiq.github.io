// rogueiq.com: static site + checker from assets; /wire/* goes to the rogueiq-feed Worker.
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.hostname === "www.rogueiq.com") return Response.redirect(`https://rogueiq.com${url.pathname}${url.search}`, 301);
    if (url.pathname === "/wire" || url.pathname.startsWith("/wire/")) return env.FEED.fetch(req);
    return env.ASSETS.fetch(req);
  },
};
