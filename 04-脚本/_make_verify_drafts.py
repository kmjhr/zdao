# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_drafts.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  setTimeout(function () {
    var n = artwork.size, tb = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
    if (tb) {
      for (var y = 6; y < 14; y++) for (var x = 8; x < 18; x++) tb.pixels[y * n + x] = (x + y) % 2 ? 'G2' : 'A3';
    }
    var hd = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'head') hd = l; });
    if (hd) { for (var y2 = 2; y2 < 6; y2++) for (var x2 = 9; x2 < 15; x2++) hd.pixels[y2 * n + x2] = 'G6'; }
    invalidateLayerCaches();
    if (currentDraftId) saveDraftNow(currentDraftId, true);
    requestRender();
    rep.push('paint draft=' + currentDraftId);
  }, 300);
  setTimeout(function () {
    newDraftFromCurrent();
    rep.push('new draft=' + currentDraftId);
  }, 900);
  setTimeout(function () {
    openDraftsModal();
    rep.push('modal open');
  }, 1500);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 2200);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('DRAFTS VERIFY WRITTEN')
