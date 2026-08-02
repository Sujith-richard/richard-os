/* Richard OS — shell: sidebar + topbar + command palette */
(function () {
  const NAV = [
    { group: "OPERATE", items: [
      { label: "Console", href: "/ui/", ic: "\u25C9" },
      { label: "Brain", href: "/ui/brain.html", ic: "\u2B61" },
      { label: "Agents", href: "/ui/agents.html", ic: "\u25CF" },
      { label: "Tasks", href: "/ui/tasks.html", ic: "\u2610" },
      { label: "Skills", href: "/ui/skills.html", ic: "\u2318" },
      { label: "Org", href: "/ui/org.html", ic: "\u26DB" },
    ]},
    { group: "SYSTEM", items: [
      { label: "Comms", href: "/ui/comms.html", ic: "\u2709" },
      { label: "Funnel", href: "/ui/funnel.html", ic: "\u21E2" },
      { label: "Finances", href: "/ui/finances.html", ic: "\u20BF" },
      { label: "Social", href: "/ui/social.html", ic: "\u2630" },
      { label: "Integrations", href: "/ui/integrations.html", ic: "\u21C4" },
      { label: "Analytics", href: "/ui/analytics.html", ic: "\u25A6" },
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
    body.style.cssText = "margin:0;display:flex;height:100vh;overflow:hidden;";

    const sidebar = document.createElement("aside");
    sidebar.className = "os-sidebar";
    sidebar.innerHTML =
      '<div class="os-brand"><span class="dot"></span><b>Richard OS</b></div>' +
      '<nav class="os-nav">' + NAV.map(g =>
        '<div class="group">' + g.group + '</div>' +
        g.items.map(i => '<a href="' + i.href + '" class="' + (i.href === location.pathname ? "active" : "") + '"><span class="ic">' + i.ic + '</span>' + i.label + '</a>').join("")
      ).join("") + '</nav>' +
      '<div class="foot">DATA_MODE · FAKE<br>v2.0 · files you own</div>';

    const main = document.createElement("main");
    main.className = "os-main";
    main.innerHTML =
      '<header class="os-topbar">' +
        '<div class="os-crumb">' + PAGE.crumb.map((c, i) => '<span>' + c + '</span>' + (i < PAGE.crumb.length - 1 ? '<span class="sep">/</span>' : "")).join("") + '</div>' +
        '<div class="os-sync"><span>WORKSPACE: SUJITH</span><span class="led"></span><span>SYNCED</span><kbd>CMD K</kbd></div>' +
      '</header>' +
      '<div class="os-content" id="os-content"></div>';

    while (body.firstChild) main.querySelector("#os-content").appendChild(body.firstChild);
    body.appendChild(sidebar);
    body.appendChild(main);

    const pal = document.createElement("div");
    pal.className = "os-palette"; pal.id = "os-palette";
    pal.innerHTML = '<div class="box"><input id="os-pal-input" placeholder="Jump to a view\u2026"><div class="res"></div></div>';
    body.appendChild(pal);
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
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
