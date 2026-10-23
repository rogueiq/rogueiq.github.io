(function(){
  var FEED="https://feed.rogueiq.com";
  var list=document.getElementById("wire-list");
  function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
  function ago(iso){var m=Math.round((Date.now()-new Date(iso))/60000);if(m<60)return m+"m";var h=Math.round(m/60);return h<48?h+"h":Math.round(h/24)+"d"}
  function fallback(){list.innerHTML="";var li=el("li","muted");li.append("The live preview didn't load. ");var a=el("a",null,"Open the feed →");a.href=FEED+"/";li.append(a);list.append(li)}
  if(list){function get(q){return fetch(FEED+"/v1/items?"+q).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(d){return d.items||[]})}
  Promise.all([get("limit=4&source=fed,bls,bea"),get("limit=8&min_importance=2")]).then(function(r){
    var items=r[0].slice(0,4),seen={};items.forEach(function(i){seen[i.id]=1});
    r[1].forEach(function(i){if(items.length<4&&!seen[i.id]){items.push(i);seen[i.id]=1}});
    var newest=r[0].concat(r[1]).reduce(function(m,i){var v=Date.parse(i.published_at);return v>m?v:m},0);
    if(newest&&Date.now()-newest<864e5){var lg=document.querySelector(".logo");if(lg){lg.classList.add("live");lg.title="New Wire release in the last 24 hours"}}
    if(!items.length)return fallback();list.innerHTML="";
    items.forEach(function(i){var li=el("li","post");var top=el("p","post-top");top.append(el("span","src",i.source_name),el("span","chk","✓ Official source"),el("span","muted post-date"," · "+new Date(i.published_at).toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"})+" ("+ago(i.published_at)+" ago)"));
      var t=el("p","post-title",i.title);var s;if(i.source_name&&i.published_at&&!isNaN(Date.parse(i.published_at))&&i.source_url){s=el("a","stamp");s.href=i.source_url;s.rel="noopener";s.append(el("span","st-ag",i.source_name),el("span","st-dt",new Date(i.published_at).toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"})),el("span","st-ln","Source ↗"));s.setAttribute("aria-label","Original source: "+i.source_name)}else if(i.source_url){s=el("a","post-src","View source document →");s.href=i.source_url;s.rel="noopener"}
      li.append(top,t);if(i.excerpt&&i.excerpt!==i.title&&i.source!=="edgar")li.append(el("p","post-ex muted",i.excerpt));if(s)li.append(s);list.append(li)})
  }).catch(fallback)}
  document.querySelectorAll("button.copy").forEach(function(b){b.addEventListener("click",function(){var c=document.getElementById(b.dataset.copy);navigator.clipboard&&navigator.clipboard.writeText(c.textContent).then(function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy"},1500)})})});
})();
