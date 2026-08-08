/* Richard OS — shell: sidebar + topbar + command palette */
(function () {
  const NAV = [
    { group: "OPERATE", items: [
      { label: "Dashboard", href: "/ui/", ic: "\u25C9" },
      { label: "CEO Brief", href: "/ui/ceo.html", ic: "\u2605" },
      { label: "AI Core", href: "/ui/chat.html", ic: "\uD83D\uDCAC" },
      { label: "Doc Chat", href: "/ui/docchat.html", ic: "\uD83D\uDCC4" },
      { label: "Models", href: "/ui/models.html", ic: "\uD83E\uDDE0" },
      { label: "Model Registry", href: "/ui/models-registry.html", ic: "\uD83C\uDFED" },
      { label: "Brain", href: "/ui/brain.html", ic: "\u2B61" },
      { label: "Agents", href: "/ui/agents.html", ic: "\u25CF" },
      { label: "Tasks", href: "/ui/tasks.html", ic: "\u2610" },
      { label: "Skills", href: "/ui/skills.html", ic: "\u2318" },
      { label: "Approvals", href: "/ui/approvals.html", ic: "\u2713" },
      { label: "Workflows", href: "/ui/workflows.html", ic: "\u21BA" },
      { label: "Execution", href: "/ui/execution.html", ic: "\u2699\uFE0F" },
      { label: "Validation", href: "/ui/validation.html", ic: "\uD83E\uDDEA" },
      { label: "Lifecycle", href: "/ui/lifecycle.html", ic: "\uD83D\uDD04" },
      { label: "Memory", href: "/ui/memory.html", ic: "\uD83E\uDDE0" },
      { label: "Knowledge Graph", href: "/ui/kg.html", ic: "\uD83D\uDD78\uFE0F" },
      { label: "Plugins", href: "/ui/plugins.html", ic: "\uD83E\uDDE9" },
      { label: "Hub", href: "/ui/hub.html", ic: "\uD83D\uDED2" },
      { label: "SDK", href: "/ui/sdk.html", ic: "\uD83D\uDEE0\uFE0F" },
      { label: "System", href: "/ui/system.html", ic: "\uD83D\uDDA5\uFE0F" },
      { label: "Settings", href: "/ui/settings.html", ic: "\u2699\uFE0F" },
      { label: "Automations", href: "/ui/automations.html", ic: "\u23F0" },
      { label: "Collaboration", href: "/ui/collab.html", ic: "\uD83E\uDDE0" },
      { label: "Organization", href: "/ui/org.html", ic: "\u26DB" },
      { label: "Departments", href: "/ui/departments.html", ic: "\uD83C\uDFE2" },
      { label: "Personas", href: "/ui/personas.html", ic: "\u263A" },
      { label: "Personal Life", href: "/ui/life.html", ic: "\uD83E\uDDD8" },
    ]},
    { group: "SYSTEM", items: [
      { label: "Communications", href: "/ui/comms.html", ic: "\u2709" },
      { label: "Funnel", href: "/ui/funnel.html", ic: "\u21E2" },
      { label: "Finance", href: "/ui/finances.html", ic: "\u20BF" },
      { label: "Social", href: "/ui/social.html", ic: "\u2630" },
      { label: "Content", href: "/ui/content.html", ic: "\u270D" },
      { label: "Integrations", href: "/ui/integrations.html", ic: "\u21C4" },
      { label: "Analytics", href: "/ui/analytics.html", ic: "\u25A6" },
      { label: "Roadmap", href: "/ui/roadmap.html", ic: "\u21E3" },
      { label: "Reference", href: "/ui/reference.html", ic: "\u2630" },
      { label: "Learning", href: "/ui/learning.html", ic: "\u2730" },
      { label: "Deals", href: "/ui/deals.html", ic: "\u20BF" },
      { label: "Connections", href: "/ui/connections.html", ic: "\u21C4" },
      { label: "Tool Repos", href: "/ui/repos.html", ic: "\u2699" },
      { label: "Registry", href: "/ui/registry.html", ic: "\uD83D\uDCC1" },
      { label: "Repo Intel", href: "/ui/repo-intel.html", ic: "\uD83D\uDDFA" },
       { label: "Structures", href: "/ui/structures.html", ic: "\uD83D\uDCD0" },
    ]},
  ];
  const PAGE = window.PAGE || { title: "Console", crumb: ["Operate", "Console"] };
  const all = NAV.flatMap(g => g.items.map(i => ({ ...i, group: g.group })));

  function init() {
    const css = document.createElement("link");
    css.rel = "stylesheet"; css.href = "/ui/style.css";
    document.head.appendChild(css);

    const body = document.body;
    body.className = "grid-bg";
    // ── I1 auth guard: no token -> login (skip on login page) ──
    if (!location.pathname.endsWith("login.html")) {
      var tok = (document.cookie.match(/(?:^|; )richard_token=([^;]*)/) || [])[1] || "";
      if (!tok) { location.href = "/ui/login.html"; return; }
    }
    body.style.cssText = "margin:0;display:flex;height:100vh;overflow:hidden;";

    const sidebar = document.createElement("aside");
    sidebar.className = "os-sidebar";
    sidebar.innerHTML =
      '<div class="os-brand"><span class="dot"></span><b>Richard OS</b></div>' +
      '<nav class="os-nav">' + NAV.map(g =>
        '<div class="group">' + g.group + '</div>' +
        g.items.map(i => '<a href="' + i.href + '" class="' + (i.href === location.pathname ? "active" : "") + '"><span class="ic">' + i.ic + '</span>' + i.label + '</a>').join("")
      ).join("") + '</nav>' +
      '<div class="foot">DATA_MODE · FAKE<br>v3 · files you own</div>';

    const main = document.createElement("main");
    main.className = "os-main";
    main.innerHTML =
      '<header class="os-topbar">' +
        '<div class="os-crumb">' + PAGE.crumb.map((c, i) => '<span>' + c + '</span>' + (i < PAGE.crumb.length - 1 ? '<span class="sep">/</span>' : "")).join("") + '</div>' +
        '<div class="os-sync"><button class="os-menu-btn" id="os-menu-btn">☰</button><button class="qa-btn">QUICK ADD</button><button class="notify-btn">NOTIFY <span class="dot"></span> <span id="notify-count" style="color:var(--ok)"></span><span id="notify-badge" style="display:none;background:var(--err);color:var(--bg);border-radius:8px;font-size:9px;padding:0 5px;font-weight:700"></span></button><button class="theme-btn">THEME</button><span class="ws-label">SUJITH</span><span class="led"></span><span id="sched-label">SCHEDULER ON</span><span id="live-pill" class="live-pill">&#9899; DEMO</span><kbd>CMD K</kbd></div>' +
      '</header>' +
      '<div class="os-content" id="os-content"></div>';

    while (body.firstChild) main.querySelector("#os-content").appendChild(body.firstChild);
    body.appendChild(sidebar);
    body.appendChild(main);
    // ── Mobile drawer (v3.26): hamburger toggles sidebar on phones ──
    var backdrop = document.createElement("div");
    backdrop.className = "os-drawer-backdrop";
    body.appendChild(backdrop);
    function toggleDrawer(open) {
      document.body.classList.toggle("os-drawer-open", open);
    }
    document.addEventListener("click", function(e) {
      if (e.target.closest && e.target.closest("#os-menu-btn")) { toggleDrawer(!document.body.classList.contains("os-drawer-open")); }
      if (e.target.closest && e.target.closest(".os-drawer-backdrop")) { toggleDrawer(false); }
      if (e.target.closest && e.target.closest(".os-nav a")) { toggleDrawer(false); }
    });
    // ── PWA (v3.26): manifest + service worker ──
    var l = document.createElement("link");
    l.rel = "manifest"; l.href = "/ui/manifest.json";
    document.head.appendChild(l);
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/ui/sw.js").catch(function(){});
    }

    // ── Command palette ──
    const pal = document.createElement("div");
    pal.className = "os-palette"; pal.id = "os-palette";
    pal.innerHTML = '<div class="box"><input id="os-pal-input" placeholder="Jump to a view…"><div class="res"></div></div>';
    body.appendChild(pal);
    // -- Live pill (v3.4): polls /api/v1/integrations every 30s
    (async function livePill() {
      var el = document.getElementById("live-pill");
      if (!el) return;
      async function tick() {
        try {
          var d = await (await fetch("/api/v1/integrations")).json();
          var live = Object.values(d.integrations || {}).filter(function(v){ return v.status === "live"; }).length;
          el.textContent = live ? "LIVE " + live : "DEMO";
          el.className = "live-pill" + (live ? " on" : "");
        } catch (e) { el.textContent = "DEMO"; }
      }
      tick(); setInterval(tick, 30000);
    })();

    const input = pal.querySelector("input"), res = pal.querySelector(".res");
    function show(q) {
      const f = all.filter(i => i.label.toLowerCase().includes(q.toLowerCase()));
      res.innerHTML = f.map(i => '<a href="' + i.href + '"><span class="ic">' + i.ic + '</span><span>' + i.label + '</span><span style="margin-left:auto;color:var(--dim)">' + i.group + '</span></a>').join("") || '<a style="color:var(--dim)">no match</a>';
    }
    document.addEventListener("keydown", e => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        pal.classList.toggle("open");
        if (pal.classList.contains("open")) { input.value = ""; show(""); setTimeout(() => input.focus(), 10); }
      }
      if (e.key === "Escape") pal.classList.remove("open");
    });
    input.addEventListener("input", e => show(e.target.value));
    pal.addEventListener("click", e => { if (e.target === pal) pal.classList.remove("open"); });

    // ── Theme switcher (8 themes) ──
    const THEMES = ["dark", "midnight", "graphite", "oled", "nord", "dracula", "tokyo", "catppuccin"];
    function applyTheme(t) { document.documentElement.setAttribute("data-theme", t); localStorage.setItem("richard-theme", t); }
    applyTheme(localStorage.getItem("richard-theme") || "dark");
    document.querySelector(".theme-btn").addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme") || "dark";
      applyTheme(THEMES[(THEMES.indexOf(cur) + 1) % THEMES.length]);
    });

    // ── Scheduler LED ──
    function pollScheduler() {
      fetch("/scheduler-status").then(r => r.json()).then(d => {
        const led = document.querySelector(".os-sync .led");
        const label = document.getElementById("sched-label");
        if (led) led.style.background = d.running ? "var(--ok)" : "var(--warn)";
        if (label) label.textContent = d.running ? "SCHEDULER ON" : "SCHEDULER OFF";
      }).catch(() => {});
    }
    setInterval(pollScheduler, 5000);
    pollScheduler();
  }

  // ── Delegated: ⌘K chip, QUICK ADD, NOTIFY (timing-proof) ──
  document.addEventListener("click", e => {
    const chip = e.target.closest ? e.target.closest(".os-sync kbd") : null;
    const qa = e.target.closest ? e.target.closest(".qa-btn") : null;
    const nb = e.target.closest ? e.target.closest(".notify-btn") : null;
    if (!chip && !qa && !nb) return;
    e.stopPropagation();
    let el = document.getElementById("os-drop");
    if (!el) { el = document.createElement("div"); el.id = "os-drop"; el.style.cssText = "position:fixed;background:var(--surface);border:1px solid var(--hairline2);padding:6px;z-index:70;min-width:200px;font-size:11px;box-shadow:0 10px 30px rgba(0,0,0,.5);"; document.body.appendChild(el); }
    if (chip) {
      const pal = document.getElementById("os-palette");
      if (pal) { pal.classList.toggle("open"); const inp = document.getElementById("os-pal-input"); if (inp && pal.classList.contains("open")) { inp.value = ""; inp.focus(); } }
      return;
    }
    const items = qa ? [{ a: "task", l: "+ New task" }, { a: "agent", l: "+ Run agent" }, { a: "note", l: "+ New note" }] : [{ a: "none", l: "(no notifications — demo)" }, { a: "approvals", l: "check approval queue" }];
    el.innerHTML = items.map(i => '<div data-a="' + i.a + '">' + i.l + '</div>').join("");
    el.querySelectorAll("div").forEach(d => d.addEventListener("click", () => {
      el.style.display = "none";
      if (d.dataset.a === "task") { const t = prompt("New task title:"); if (t) fetch("/quick-add-task?title=" + encodeURIComponent(t), { method: "POST" }).then(() => location.href = "/ui/tasks.html"); }
      else if (d.dataset.a === "agent") location.href = "/ui/agents.html";
      else if (d.dataset.a === "note") location.href = "/ui/";
      else if (d.dataset.a === "approvals") location.href = "/ui/approvals.html";
    }));
    if (nb) fetch("/approval-count").then(r => r.json()).then(x => { const b = document.getElementById("notify-badge"); if (b && x.pending) { b.textContent = x.pending; b.style.display = "inline-block"; } }).catch(() => {});
    const b = qa || nb, r = b.getBoundingClientRect();
    el.style.top = (r.bottom + 4) + "px"; el.style.right = (window.innerWidth - r.right) + "px"; el.style.display = "block";
    setTimeout(() => document.addEventListener("click", function h() { el.style.display = "none"; document.removeEventListener("click", h); }), 10);
  });

  // ── NOTIFY badge live count ──
  (function badgeUpdater() {
    function upd() {
      const badge = document.getElementById("notify-badge");
      const count = document.getElementById("notify-count");
      if (!badge && !count) return;
      fetch("/approval-count").then(r => r.json()).then(d => {
        const n = d.pending || 0;
        if (count) count.textContent = n ? "(" + n + ")" : "";
        if (badge) { if (n) { badge.textContent = n; badge.style.display = "inline-block"; } else { badge.style.display = "none"; } }
      }).catch(() => {});
    }
    upd();
    setTimeout(upd, 300);
    setInterval(upd, 8000);
  })();

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
