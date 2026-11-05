# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_perf.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  function block(layer, x0, y0, w, h, code) {
    var n = artwork.size;
    for (var y = y0; y < y0 + h; y++) for (var x = x0; x < x0 + w; x++) layer.pixels[y * n + x] = code;
  }
  var tb = null;
  function findTorso() {
    tb = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
  }
  function timeit(fn, times) {
    var t0 = performance.now();
    for (var i = 0; i < times; i++) fn();
    return Math.round((performance.now() - t0) * 100) / 100;
  }
  setTimeout(function () {
    findTorso();
    block(tb, 2, 2, 10, 10, 'G2');
    block(tb, 20, 20, 6, 6, 'A3');
    var hd = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'head') hd = l; });
    if (hd) block(hd, 4, 26, 5, 4, 'F1');
    invalidateLayerCaches();
    setCurrentLayer(tb.id);
    switchTab('layers');
    showCodes = true;
    var b = document.getElementById('btnCodes'); if (b) b.classList.add('active');
    requestRender();
    rep.push('painted');
  }, 300);
  setTimeout(function () {
    var cold = timeit(function () { codeCache = null; requestRender(); }, 8);
    var warm = timeit(function () { requestRender(); }, 30);
    rep.push('codeColdMs=' + cold / 8 + ' warmFrameMs=' + warm / 30);
    rep.push('cacheEdge=' + (codeCache ? codeCache.canvas.width : 'none'));
  }, 900);
  setTimeout(function () {
    block(tb, 14, 4, 1, 1, 'B5');
    markLayerDirty(tb, 14, 4, 14, 4);
    requestRender();
    rep.push('dirty1cell ok');
  }, 1500);
  setTimeout(function () {
    var hd2 = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'head') hd2 = l; });
    setCurrentLayer(hd2.id);
    requestRender();
    rep.push('switchLayer ok');
  }, 2100);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 2900);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('PERF VERIFY WRITTEN')
