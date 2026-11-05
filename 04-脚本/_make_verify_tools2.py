# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_tools2.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  function block(layer, x0, y0, w, h, code) {
    var n = artwork.size;
    for (var y = y0; y < y0 + h; y++) {
      for (var x = x0; x < x0 + w; x++) layer.pixels[y * n + x] = code;
    }
  }
  var tb = null;
  function find() {
    tb = null;
    artwork.layers.forEach(function (l) { if (l.part_type === 'torso') tb = l; });
  }
  var report = [];
  setTimeout(function () {
    find();
    block(tb, 4, 4, 6, 6, 'G4');
    block(tb, 16, 16, 4, 4, 'B5');
    invalidateLayerCaches();
    setCurrentLayer(tb.id);
    requestRender();
    report.push('paint L=' + artwork.layers.length);
  }, 300);
  setTimeout(function () {
    switchTab('layers'); showCodes = true;
    var b = document.getElementById('btnCodes'); if (b) b.classList.add('active');
    requestRender(); report.push('codes');
  }, 600);
  setTimeout(function () {
    nudgeLayer(1, -2, false);
    report.push('nudge L=' + pixelCount(tb) + ' bounds?');
  }, 1200);
  setTimeout(function () {
    duplicateLayer(false);
    report.push('dup L=' + artwork.layers.length);
  }, 1900);
  setTimeout(function () {
    var newL = currentLayer();
    mirrorCurrentLayer();
    report.push('mirror on=' + (newL ? newL.display_name : '?') + ' L=' + artwork.layers.length);
  }, 2500);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:9999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + report.join(' | ');
    document.body.appendChild(el);
  }, 3100);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('OK2 WRITTEN')
