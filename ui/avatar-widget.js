/* Richard AI Avatar — floating widget (v6.3)
   Mini glowing orb, draggable, click opens /ui/avatar.html, live mood. */
(function () {
  if (window.__richWidget) return;
  window.__richWidget = true;
  function init() {
    var d = document.createElement('div');
    d.id = 'rich-avatar-widget';
    d.innerHTML = '<span class="raw-orb">\u269B</span>';
    var st = d.style;
    st.position = 'fixed'; st.right = '22px'; st.bottom = '22px';
    st.width = '58px'; st.height = '58px'; st.borderRadius = '50%';
    st.background = 'radial-gradient(circle at 30% 30%, #7C3AED, #0E7490)';
    st.boxShadow = '0 0 20px rgba(167,139,250,.55), inset 0 0 8px rgba(34,211,238,.35)';
    st.display = 'flex'; st.alignItems = 'center'; st.justifyContent = 'center';
    st.fontSize = '24px'; st.cursor = 'grab'; st.userSelect = 'none';
    st.zIndex = 999998; st.border = '2px solid rgba(34,211,238,.6)';
    st.transition = 'box-shadow .3s';
    (document.body || document.documentElement).appendChild(d);

    var moodEl = document.createElement('div'); // tooltip: mood label
    moodEl.id = 'raw-avatar-mood';
    moodEl.style.cssText = 'position:fixed;z-index:999999;pointer-events:none;background:rgba(10,16,31,.9);border:1px solid #22D3EE;color:#D7E0F5;font:11px Segoe UI,sans-serif;padding:3px 8px;border-radius:8px;opacity:0;transition:opacity .2s;white-space:nowrap;';
    document.body.appendChild(moodEl);

    var moods = { idle:['#A78BFA','idle'], thinking:['#FBBF24','thinking'], executing:['#10B981','executing'], error:['#F87171','error'] };
    var state = 'idle';
    function setState(s) {
      if (!moods[s]) s = 'idle';
      if (state === s) return;
      state = s;
      var c = moods[s][0];
      d.style.background = 'radial-gradient(circle at 30% 30%, ' + c + ', #0E7490)';
      d.style.boxShadow = '0 0 20px ' + c + '66, inset 0 0 8px rgba(34,211,238,.35)';
      d.style.borderColor = c;
    }
    function showMood() {
      var r = d.getBoundingClientRect();
      pulseElEl; // placeholder -> replaced below
    }
    function fetchJSON(u, cb) {
      try { fetch(u).then(function (r) { return r.ok ? r.json() : null; }).then(cb).catch(function () { cb(null); }); }
      catch (e) { cb(null); }
    }
    function poll() {
      fetchJSON('/agent-status', function (a) {
        fetchJSON('/scheduler-status', function (s) {
          var ab = a && (a.running || a.active || a.busy);
          var sb = s && (s.running > 0 || s.active > 0);
          if (a === null && s === null) setState('error');
          else if (ab || sb) setState('executing');
          else setState('idle');
        });
      });
    }
    // drag + click
    var dragging = false, moved = false, sx = 0, sy = 0, ox = 0, oy = 0;
    d.addEventListener('pointerdown', function (e) {
      dragging = true; moved = false; sx = e.clientX; sy = e.clientY;
      var r = d.getBoundingClientRect(); ox = e.clientX - r.left; oy = e.clientY - r.top;
      d.setPointerCapture(e.pointerId); d.style.cursor = 'grabbing';
    });
    d.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      if (Math.abs(e.clientX - sx) > 4 || Math.abs(e.clientY - sy) > 4) moved = true;
      d.style.left = (e.clientX - ox) + 'px'; d.style.top = (e.clientY - oy) + 'px';
      d.style.right = 'auto'; d.style.bottom = 'auto';
    });
    function end(e) {
      dragging = false; d.style.cursor = 'grab';
      if (!moved) { window.open('/ui/avatar.html', '_blank'); }
    }
    d.addEventListener('pointerup', end);
    d.addEventListener('pointercancel', function () { dragging = false; d.style.cursor = 'grab'; });
    // hover mood label
    d.addEventListener('mouseenter', function () {
      var r = d.getBoundingClientRect();
      moodEl.textContent = 'Richard · ' + state;
      moodEl.style.left = (r.right + 8) + 'px';
      moodEl.style.top = (r.top + r.height / 2 - 9) + 'px';
      moodEl.style.opacity = '1';
    });
    d.addEventListener('mouseleave', function () { moodEl.style.opacity = '0'; });

    setState('idle');
    poll();
    setInterval(poll, 3000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
