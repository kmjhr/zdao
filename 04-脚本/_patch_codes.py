# -*- coding: utf-8 -*-
import io, sys

P = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
src = io.open(P, 'r', encoding='utf-8').read()
edits = []

# ---------- 1. 变量 ----------
a1 = 'var showNumbers = false;'
r1 = '''var showNumbers = false;
var showCodes = false;'''
edits.append((a1, r1, 'var showCodes'))

# ---------- 2. 顶栏按钮 ----------
a2 = '<button class="btn" id="btnNums" title="行列号（默认关）">行列号</button>'
r2 = '''<button class="btn" id="btnNums" title="行列号（默认关）">行列号</button>
      <button class="btn" id="btnCodes" title="色号：每格标出这一格最终看到的是哪层、什么色号（缩小到看不清时自动隐藏）">色号</button>'''
edits.append((a2, r2, 'btnCodes 按钮'))

# ---------- 3. isDarkHex ----------
a3 = "function isColorHex(v) { return typeof v === 'string' && /^#([0-9a-f]{6}|[0-9a-f]{3})$/i.test(v); }"
r3 = '''function isColorHex(v) { return typeof v === 'string' && /^#([0-9a-f]{6}|[0-9a-f]{3})$/i.test(v); }
function isDarkHex(hex) {
  if (!hex) return false;
  var h = String(hex).replace('#', '');
  if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
  var r = parseInt(h.substr(0, 2), 16), g = parseInt(h.substr(2, 2), 16), b = parseInt(h.substr(4, 2), 16);
  if (!isFinite(r) || !isFinite(g) || !isFinite(b)) return false;
  return (0.299 * r + 0.587 * g + 0.114 * b) < 132;
}'''
edits.append((a3, r3, 'isDarkHex'))

# ---------- 4. 渲染插入 ----------
a4 = '''  // 当前层锚点
  var cur = currentLayer();'''
r4 = '''  // 色号标记（可开关）：先看当前层，当前层这格为空则取最上可见层
  if (showCodes && cell >= 11) {
    var lyC = artwork.layers;
    var curL = null;
    for (var k0 = 0; k0 < lyC.length; k0++) { if (lyC[k0].id === currentLayerId) { curL = lyC[k0]; break; } }
    var codeFont = Math.min(14, Math.round(cell * 0.55));
    ctx.font = '700 ' + codeFont + 'px "Consolas", monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.lineWidth = Math.max(1, Math.round(cell * 0.14));
    for (var cy0 = 0; cy0 < n; cy0++) {
      for (var cx0 = 0; cx0 < n; cx0++) {
        var cellIdx = cy0 * n + cx0;
        var topCode = null;
        if (curL && curL.visible) {
          var pc = curL.pixels[cellIdx];
          if (pc !== null && pc !== undefined && pc !== 'transparent') topCode = String(pc);
        }
        if (!topCode) {
          for (var li0 = lyC.length - 1; li0 >= 0; li0--) {
            var LC0 = lyC[li0];
            if (!LC0.visible) continue;
            var cc0 = LC0.pixels[cellIdx];
            if (cc0 === null || cc0 === undefined || cc0 === 'transparent') continue;
            topCode = String(cc0);
            break;
          }
        }
        if (!topCode) continue;
        var tpx = cx0 * cell + cell / 2, tpy = cy0 * cell + cell / 2;
        var darkBg = isDarkHex(hexForCode(topCode));
        ctx.fillStyle = darkBg ? 'rgba(255,255,255,.96)' : 'rgba(20,18,13,.92)';
        ctx.strokeStyle = darkBg ? 'rgba(0,0,0,.62)' : 'rgba(255,255,255,.88)';
        ctx.strokeText(topCode, tpx, tpy);
        ctx.fillText(topCode, tpx, tpy);
      }
    }
    ctx.lineWidth = 1;
  }

  // 当前层锚点
  var cur = currentLayer();'''
edits.append((a4, r4, '色号渲染'))

# ---------- 5. 事件 ----------
a5 = "  $('#btnUndo').addEventListener('click', undo);"
r5 = '''  $('#btnCodes').addEventListener('click', function () {
    showCodes = !showCodes;
    this.classList.toggle('active', showCodes);
    requestRender();
  });

  $('#btnUndo').addEventListener('click', undo);'''
edits.append((a5, r5, 'btnCodes 事件'))

for a, r, label in edits:
    c = src.count(a)
    if c != 1:
        print('FAIL %s: count=%d' % (label, c))
        sys.exit(1)
    print('OK %s' % label)

out = src
for a, r, label in edits:
    out = out.replace(a, r, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE %d bytes' % len(out))
