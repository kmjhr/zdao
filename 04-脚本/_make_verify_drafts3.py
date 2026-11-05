# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\编辑器原型\index.html'
OUT = r'D:\codex\codex-data\youxi\编辑器原型\_verify_drafts2.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  var idA = null, idB = null;
  function block(layer, x0, y0, w, h, code) {
    var n = artwork.size;
    for (var y = y0; y < y0 + h; y++) for (var x = x0; x < x0 + w; x++) layer.pixels[y * n + x] = code;
  }
  var tb = null;
  setTimeout(function () {
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
    block(tb, 3, 3, 8, 8, 'A3');
    invalidateLayerCaches();
    setCurrentLayer(tb.id);
    refreshAllUI();
    commitChange('A：torso 画了 A3 方块');
    saveDraftNow(currentDraftId, true);
    idA = currentDraftId;
    rep.push('A 就绪');
  }, 260);
  setTimeout(function () {
    newDraftFromCurrent();
    idB = currentDraftId;
    rep.push('新草稿=' + (idA !== idB ? '已分开' : '没分开'));
  }, 800);
  setTimeout(function () {
    block(tb, 16, 16, 6, 6, 'C5');
    invalidateLayerCaches();
    commitChange('B：torso 画了 C5 方块');
    saveDraftNow(currentDraftId, true);
    rep.push('B 就绪 草稿数=' + readDraftIndex().length);
  }, 1100);
  setTimeout(function () {
    loadDraft(idA);
    rep.push('切回A');
  }, 1400);
  setTimeout(function () {
    var r = [];
    readDraftIndex().forEach(function (d) { r.push(d.name + '(' + (d.progress ? d.progress.painted : '?') + ')'); });
    rep.push('切回后 层数=' + artwork.layers.length + ' 索引=' + r.join(','));
    var cur = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') cur = l; });
    rep.push('当前torso 格子=' + pixelCount(cur));
    openDraftsModal();
  }, 1700);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 2100);
})();
</script>
</body>'''

assert src.count('</body>') == 1
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(src.replace('</body>', inject, 1))
print('DRAFTS VERIFY2 WRITTEN')
