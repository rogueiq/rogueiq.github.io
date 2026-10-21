(function(){
  var FEED="https://rogueiq-feed.rogueiq.workers.dev";
  var list=document.getElementById("wire-list");
  function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
  function ago(iso){var m=Math.round((Date.now()-new Date(iso))/60000);if(m<60)return m+"m";var h=Math.round(m/60);return h<48?h+"h":Math.round(h/24)+"d"}
  function fallback(){list.innerHTML="";var li=el("li","muted");li.append("The live preview didn't load. ");var a=el("a",null,"Open the feed →");a.href=FEED+"/";li.append(a);list.append(li)}
  if(list){fetch(FEED+"/v1/items?limit=4&min_importance=2").then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(d){
    if(!d.items||!d.items.length)return fallback();list.innerHTML="";
    d.items.forEach(function(i){var li=el("li","post");var top=el("p","post-top");top.append(el("span","src",i.source_name),el("span","chk","✓ Official source"),el("span","muted"," · "+ago(i.published_at)));
      var t=el("p","post-title",i.title);var s=el("a","post-src","View source document →");s.href=i.source_url;s.rel="noopener";
      li.append(top,t);if(i.excerpt&&i.excerpt!==i.title)li.append(el("p","post-ex muted",i.excerpt));li.append(s);list.append(li)})
  }).catch(fallback)}
  document.querySelectorAll("button.copy").forEach(function(b){b.addEventListener("click",function(){var c=document.getElementById(b.dataset.copy);navigator.clipboard&&navigator.clipboard.writeText(c.textContent).then(function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy"},1500)})})});
})();
