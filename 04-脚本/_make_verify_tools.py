# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_tools.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  function block(layer, x0, y0, w, h, code) {
    var n = artwork.size;
    for (var y = y0; y < y0 + h; y++) {
      for (var x = x0; x < x0 + w; x++) layer.pixels[y * n + x] = code;
    }
  }
  var tb = null, hd = null;
  function find() {
    tb = null; hd = null;
    artwork.layers.forEach(function (l) {
      if (l.part_type === 'torso') tb = l;
      if (l.part_type === 'head') hd = l;
    });
  }
  var report = [];
  setTimeout(function () { find(); block(tb, 2, 2, 8, 8, 'G2'); block(tb, 20, 20, 5, 5, 'A3'); if (hd) block(hd, 2, 26, 4, 3, 'F1'); invalidateLayerCaches(); requestRender(); report.push('paint'); }, 300);
  setTimeout(function () { switchTab('layers'); showCodes = true; var b = document.getElementById('btnCodes'); if (b) b.classList.add('active'); requestRender(); report.push('codes'); }, 600);
  setTimeout(function () { setTool('magic'); magicSelect(3, 3, tb, false); report.push('magic sel=' + selectionRects.length); }, 1000);
  setTimeout(function () { nudgeLayer(0, -3, false); report.push('nudge'); }, 1600);
  setTimeout(function () { duplicateLayer(false); report.push('dup layers=' + artwork.layers.length); }, 2300);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:9999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + report.join(' | ');
    document.body.appendChild(el);
  }, 2900);
})();
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('TOOLS VERIFY FILE WRITTEN')
