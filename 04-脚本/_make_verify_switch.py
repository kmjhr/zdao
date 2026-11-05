# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_switch.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  setTimeout(function () {
    var n = artwork.size, tb = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
    if (tb) { for (var y = 6; y < 14; y++) for (var x = 8; x < 18; x++) tb.pixels[y * n + x] = 'A3'; }
    invalidateLayerCaches();
    if (currentDraftId) saveDraftNow(currentDraftId, true);
    requestRender();
    rep.push('A painted');
  }, 300);
  setTimeout(function () {
    newDraftFromCurrent();
    var n = artwork.size, tb = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
    if (tb) {
      for (var i = 0; i < tb.pixels.length; i++) tb.pixels[i] = null;
      for (var y = 16; y < 24; y++) for (var x = 4; x < 12; x++) tb.pixels[y * n + x] = 'C5';
    }
    invalidateLayerCaches();
    saveDraftNow(currentDraftId, true);
    requestRender();
    rep.push('B painted');
  }, 900);
  setTimeout(function () {
    var list = readDraftIndex();
    rep.push('drafts=' + list.length);
    var other = list.filter(function (d) { return d.id !== currentDraftId; })[0];
    if (other) { loadDraft(other.id); rep.push('switched to ' + other.name); }
  }, 1600);
  setTimeout(function () {
    var cnt = 0;
    var tb2 = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb2 = l; });
    for (var i = 0; i < tb2.pixels.length; i++) if (tb2.pixels[i] != null) cnt++;
    showCodes = true;
    var b = document.getElementById('btnCodes'); if (b) b.classList.add('active');
    requestRender();
    rep.push('after switch torso px=' + cnt + ' draft=' + currentDraftId);
  }, 2200);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 2700);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('SWITCH VERIFY WRITTEN')
