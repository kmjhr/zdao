# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_save.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  var calls = { auto: 0, draft: 0 };
  var realAuto = saveAutosave, realDraft = saveDraftNow;
  saveAutosave = function () { calls.auto++; return realAuto.apply(null, arguments); };
  saveDraftNow = function () { calls.draft++; return realDraft.apply(null, arguments); };
  function block(layer, x0, y0, code) {
    var n = artwork.size;
    layer.pixels[y0 * n + x0] = code;
  }
  var tb = null;
  setTimeout(function () {
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
    setCurrentLayer(tb.id);
    rep.push('start draft=' + (currentDraftId ? 'yes' : 'no'));
  }, 200);
  setTimeout(function () {
    // 模拟连续 30 次笔画提交
    for (var i = 0; i < 30; i++) {
      block(tb, 3 + (i % 10), 3 + Math.floor(i / 10), 'G2');
      markLayerDirty(tb, 3 + (i % 10), 3 + Math.floor(i / 10), 3 + (i % 10), 3 + Math.floor(i / 10));
      commitChange();
    }
    rep.push('30次commit后 auto=' + calls.auto + ' draft=' + calls.draft);
  }, 350);
  setTimeout(function () {
    rep.push('约700ms auto=' + calls.auto + ' draft=' + calls.draft + ' timer=' + (draftSaveTimer ? 'pending' : 'none'));
  }, 700);
  setTimeout(function () {
    rep.push('约1300ms auto=' + calls.auto + ' draft=' + calls.draft);
  }, 1300);
  setTimeout(function () {
    rep.push('约3800ms auto=' + calls.auto + ' draft=' + calls.draft + '（草稿应在3s后落一次）');
  }, 3800);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 4300);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('SAVE VERIFY WRITTEN')
