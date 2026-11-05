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
    return Math.round((performance.now() - t0) / times * 100) / 100;
  }
  // 旧实现：每格都重算 + 两次文本绘制（无缓存、无裁剪）
  function legacyCodes() {
    var g = board.getContext('2d');
    var n = artwork.size;
    var cell = Math.max(1, Math.round(BASE_CELL * view.zoom * dpr)) / dpr;
    var ox = Math.round(view.panX * dpr) / dpr, oy = Math.round(view.panY * dpr) / dpr;
    g.save();
    g.translate(ox, oy);
    var lyC = artwork.layers, curL = null;
    for (var k = 0; k < lyC.length; k++) if (lyC[k].id === currentLayerId) curL = lyC[k];
    g.font = '700 ' + Math.min(14, Math.round(cell * 0.55)) + 'px "Consolas", monospace';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.lineWidth = Math.max(1, Math.round(cell * 0.14));
    for (var y = 0; y < n; y++) {
      for (var x = 0; x < n; x++) {
        var idx = y * n + x, top = null;
        if (curL && curL.visible) {
          var pc = curL.pixels[idx];
          if (pc != null && pc !== 'transparent') top = String(pc);
        }
        if (!top) {
          for (var li = lyC.length - 1; li >= 0; li--) {
            var L = lyC[li];
            if (!L.visible) continue;
            var c2 = L.pixels[idx];
            if (c2 == null || c2 === 'transparent') continue;
            top = String(c2); break;
          }
        }
        if (!top) continue;
        var px = x * cell + cell / 2, py = y * cell + cell / 2;
        var dark = isDarkHex(hexForCode(top));
        g.fillStyle = dark ? 'rgba(255,255,255,.96)' : 'rgba(20,18,13,.92)';
        g.strokeStyle = dark ? 'rgba(0,0,0,.62)' : 'rgba(255,255,255,.88)';
        g.strokeText(top, px, py);
        g.fillText(top, px, py);
      }
    }
    g.restore();
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
    renderBoard();
    rep.push('painted');
  }, 300);
  setTimeout(function () {
    rep.push('n=' + artwork.size + ' cell=' + (Math.round(BASE_CELL * view.zoom * dpr) / dpr) + ' dpr=' + dpr);
    var cold = timeit(function () { codeCache = null; renderBoard(); }, 30);
    var warm = timeit(function () { renderBoard(); }, 150);
    var oldw = timeit(function () { legacyCodes(); }, 60);
    rep.push('冷帧=' + cold + 'ms 热帧=' + warm + 'ms 旧版=' + oldw + 'ms');
    rep.push('cache=' + (codeCache ? codeCache.canvas.width + 'px' : 'none'));
    rep.push('提速=' + (oldw > 0 ? Math.round(oldw / Math.max(0.01, warm)) + 'x' : 'n/a'));
  }, 900);
  setTimeout(function () {
    block(tb, 14, 4, 1, 1, 'B5');
    markLayerDirty(tb, 14, 4, 14, 4);
    renderBoard();
    rep.push('dirty ok');
  }, 1500);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 2000);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('PERF VERIFY2 WRITTEN')
