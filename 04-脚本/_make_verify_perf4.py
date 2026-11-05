# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_perf2.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  function block(layer, x0, y0, w, h, code) {
    var n = artwork.size;
    for (var y = y0; y < y0 + h; y++) for (var x = x0; x < x0 + w; x++) layer.pixels[y * n + x] = code;
  }
  function stats(g) {
    if (g.__stats) return g.__stats;
    var st = { stroke: 0, fill: 0, draw: 0 };
    var os = g.strokeText, of = g.fillText, od = g.drawImage;
    g.strokeText = function () { st.stroke++; return os.apply(g, arguments); };
    g.fillText = function () { st.fill++; return of.apply(g, arguments); };
    g.drawImage = function () { st.draw++; return od.apply(g, arguments); };
    g.__stats = st;
    return st;
  }
  var tb = null;
  setTimeout(function () {
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
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
    var gc = stats(codeCache.ctx);
    gc.stroke = 0;
    block(tb, 14, 4, 1, 1, 'B5');
    markLayerDirty(tb, 14, 4, 14, 4);
    renderBoard();
    rep.push('改1格→离屏描字=' + gc.stroke + '（应=1，说明只重画那一格）');
  }, 900);
  setTimeout(function () {
    var gc = stats(codeCache.ctx);
    gc.stroke = 0;
    view.zoom = view.zoom * 1.5;
    renderBoard();
    rep.push('改缩放→离屏描字=' + gc.stroke + '（应=全量重画一次）');
    rep.push('新缓存=' + (codeCache ? codeCache.canvas.width + 'x' : 'none'));
  }, 1400);
  setTimeout(function () {
    var gc = stats(codeCache.ctx);
    gc.stroke = 0;
    renderBoard();
    renderBoard();
    renderBoard();
    rep.push('缩放后热3帧→离屏描字=' + gc.stroke + '（应=0）');
  }, 1900);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 2400);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('PERF VERIFY4 WRITTEN')
