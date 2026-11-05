# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\编辑器原型\index.html'
OUT = r'D:\codex\codex-data\youxi\编辑器原型\_verify_merged.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  function block(layer, x0, y0, w, h, code) {
    var n = artwork.size;
    for (var y = y0; y < y0 + h; y++) for (var x = x0; x < x0 + w; x++) layer.pixels[y * n + x] = code;
  }
  var tb = null, hd = null, emptyL = null;
  setTimeout(function () {
    artwork.layers.forEach(function (l) {
      if (l.part_type === 'torso') tb = l;
      if (l.part_type === 'head') hd = l;
    });
    // 造内容：躯干六色棋盘
    var cols = ['G2', 'G4', 'A3', 'F1', 'B5', 'C2'];
    var n = artwork.size;
    for (var y = 2; y < 12; y++) for (var x = 2; x < 12; x++) {
      tb.pixels[y * n + x] = cols[((x - 2) % 2) + ((y - 2) % 2) * 2 + (((x - 2) >> 1) % 2) * 1];
    }
    // 简化：直接刷 6 条竖带，便于核对
    for (var y2 = 2; y2 < 12; y2++) {
      for (var x2 = 2; x2 < 12; x2++) {
        tb.pixels[y2 * n + x2] = cols[Math.min(5, Math.floor((x2 - 2) / 2))];
      }
    }
    block(hd, 4, 26, 4, 4, 'H1');
    invalidateLayerCaches();
    setCurrentLayer(tb.id);
    switchTab('layers');
    showCodes = true;
    var b = document.getElementById('btnCodes'); if (b) b.classList.add('active');
    renderBoard();
    rep.push('painted');
  }, 260);
  setTimeout(function () {
    // 整层偏移
    nudgeLayer(-2, -1, false);
    rep.push('偏移后 torso=' + pixelCount(tb));
  }, 700);
  setTimeout(function () {
    // 复制 + 镜像
    duplicateLayer(false);
    rep.push('复制后 层数=' + artwork.layers.length);
  }, 1000);
  setTimeout(function () {
    // 魔棒：点躯干上一格
    setTool('magic');
    magicSelect(2, 2, tb, false);
    rep.push('魔棒选中=' + selectionRects.length + '块');
  }, 1300);
  setTimeout(function () {
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 1700);
})();
</script>
</body>'''

assert src.count('</body>') == 1
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(src.replace('</body>', inject, 1))
print('MERGED VERIFY WRITTEN')
