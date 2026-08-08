/* Richard OS — splash overlay: black bg + logo, then fade to dashboard */
(function () {
  function show() {
    try { if (localStorage.getItem('rich_splash_seen')) return; localStorage.setItem('rich_splash_seen','1'); } catch(e){}

    var s = document.createElement('div');
    s.id = 'rich-splash';
    s.style.cssText = 'position:fixed;inset:0;z-index:999999;background:#000;display:flex;align-items:center;justify-content:center;flex-direction:column;color:#22D3EE;font:12px "Segoe UI",sans-serif;transition:opacity .5s';
    s.innerHTML = '<img src="/ui/assets/logo.png" style="width:96px;height:96px;border-radius:24px;box-shadow:0 0 40px rgba(34,211,238,.5)">' +
                  '<div style="margin-top:14px;letter-spacing:.2em">RICHARD OS</div>' +
                  '<div style="margin-top:6px;color:#8b9ac0;font-size:10px">initializing…</div>';
    (document.body || document.documentElement).appendChild(s);
    // fade out after ~1.4s
    setTimeout(function () {
      s.style.opacity = '0';
      setTimeout(function () { if (s.parentNode) s.parentNode.removeChild(s); }, 550);
    }, 1400);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show);
  else show();
})();
