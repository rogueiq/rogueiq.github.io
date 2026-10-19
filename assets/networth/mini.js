/* Compact Net Worth by Age check for the home page.
   Uses the checker's own data.js (copied from rogueiq/networth-by-age) and the same
   age-only rules as its app.js: same age groups, same percentile count, same wording.
   Runs in the browser; nothing typed is sent anywhere. */
"use strict";
(function () {
  const form = document.getElementById("mini-check");
  if (!form || typeof SCF_DATA === "undefined") return;
  const out = document.getElementById("mini-result");
  const err = document.getElementById("mini-error");
  const money = (v) => (v < 0 ? "-" : "") + "$" + Math.abs(Math.round(v)).toLocaleString("en-US");
  function parseMoney(text) {
    let s = String(text).trim().toLowerCase().replace(/[$,\s]/g, "");
    if (s === "") return null;
    let m = 1;
    if (s.endsWith("k")) { m = 1e3; s = s.slice(0, -1); } else if (s.endsWith("m")) { m = 1e6; s = s.slice(0, -1); }
    if (!/^-?\d+(\.\d+)?$/.test(s)) return null;
    return Number(s) * m;
  }
  function ordinal(n) { const h = n % 100; if (h >= 11 && h <= 13) return n + "th"; return n + ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th"); }
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    err.hidden = true;
    const ageRaw = form.age.value, age = Number(ageRaw);
    const fail = (m) => { err.textContent = m; err.hidden = false; out.hidden = true; };
    if (!ageRaw || !Number.isFinite(age)) return fail("Enter your age.");
    if (age < 18) return fail("The survey covers families whose reference person is 18 or older.");
    if (age > 110) return fail("Please check the age you entered.");
    const nw = parseMoney(form.nw.value);
    if (nw === null) return fail("Enter your net worth as a number, like 150000 or 150k.");
    const b = SCF_DATA.brackets.find((x) => age >= x.minAge && (x.maxAge === null || Math.floor(age) <= x.maxAge));
    let rank = 0; for (const c of b.percentiles) if (nw >= c) rank++;
    const group = b.id === "under35" ? "under 35" : b.id === "75plus" ? "75 or older" : "aged " + b.label;
    let head, detail;
    if (rank === 0) { head = "Below the 1st percentile"; detail = `Your net worth is lower than the 1st-percentile cut-off for US families ${group}.`; }
    else if (rank === 99) { head = "Top 1%"; detail = `Your net worth is at or above the 99th-percentile cut-off for US families ${group}.`; }
    else { head = `Higher than about ${rank}% of families`; detail = `That puts you around the ${ordinal(rank)} percentile for US families ${group}.`; }
    out.querySelector(".mr-head").textContent = head;
    out.querySelector(".mr-detail").textContent = detail;
    out.querySelector(".mr-median").textContent = `Median for this age group: ${money(b.median)} (2025 dollars).`;
    out.hidden = false;
  });
})();
