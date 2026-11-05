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
  function instrument() {
    var g = board.getContext('2d');
    if (g.__patched) return g.__stats;
    var st = { stroke: 0, fill: 0, draw: 0 };
    var os = g.strokeText, of = g.fillText, od = g.drawImage;
    g.strokeText = function () { st.stroke++; return os.apply(g, arguments); };
    g.fillText = function () { st.fill++; return of.apply(g, arguments); };
    g.drawImage = function () { st.draw++; return od.apply(g, arguments); };
    g.__patched = true;
    g.__stats = st;
    return st;
  }
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
    instrument();
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
    var st = board.getContext('2d').__stats;
    st.stroke = 0; st.fill = 0; st.draw = 0;
    codeCache = null;
    renderBoard();
    var cold = { s: st.stroke, f: st.fill };
    st.stroke = 0; st.fill = 0; st.draw = 0;
    for (var i = 0; i < 10; i++) renderBoard();
    var warm = { s: st.stroke, f: st.fill, d: st.draw };
    st.stroke = 0; st.fill = 0; st.draw = 0;
    legacyCodes();
    var old = { s: st.stroke, f: st.fill };
    rep.push('冷=' + cold.s + '次描字/' + cold.f + '次填字');
    rep.push('热10帧=' + warm.s + '次描字/' + warm.d + '次贴图');
    rep.push('旧版=' + old.s + '次描字');
    rep.push('缓存=' + (codeCache ? codeCache.canvas.width + 'x' : 'none'));
  }, 900);
  setTimeout(function () {
    block(tb, 14, 4, 1, 1, 'B5');
    markLayerDirty(tb, 14, 4, 14, 4);
    renderBoard();
    var st = board.getContext('2d').__stats;
    rep.push('改1格后重绘区最小化:' + (codeCache && !codeCache.dirty ? 'partial' : '?'));
    rep.push('该帧描字=' + st.stroke);
  }, 1400);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 1900);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('PERF VERIFY3 WRITTEN')
