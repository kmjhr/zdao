# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
OUT = r'D:\codex\codex-data\youxi\02-原型\_verify_codes.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
setTimeout(function () {
  try {
    var n = artwork.size;
    var ly = artwork.layers;
    var tgt = null;
    for (var i = 0; i < ly.length; i++) { if (ly[i].part_type === 'torso') tgt = ly[i]; }
    if (!tgt) tgt = ly[0];
    var codes = ['G2', 'G4', 'A3', 'F1', 'B5', 'C2'];
    for (var y = 4; y < 14; y++) {
      for (var x = 4; x < 14; x++) {
        tgt.pixels[y * n + x] = codes[(x + y) % codes.length];
      }
    }
    var hd = null;
    for (var j = 0; j < ly.length; j++) { if (ly[j].part_type === 'head') hd = ly[j]; }
    if (hd) { hd.pixels[2 * n + 5] = 'H1'; hd.pixels[2 * n + 6] = 'G6'; hd.pixels[3 * n + 5] = 'F5'; }
    if (typeof invalidateLayerCaches === 'function') invalidateLayerCaches();
    showCodes = true;
    var b = document.getElementById('btnCodes');
    if (b) b.classList.add('active');
    if (typeof setCurrentLayer === 'function' && tgt) setCurrentLayer(tgt.id);
    if (typeof requestRender === 'function') requestRender();
    document.title = 'VOK n=' + n + ' layers=' + ly.length;
  } catch (e) {
    document.title = 'VERR ' + e.message;
  }
}, 500);
</script>
</body>'''

assert src.count('</body>') == 1
out = src.replace('</body>', inject, 1)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('VERIFY FILE WRITTEN')
