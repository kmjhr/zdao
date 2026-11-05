# -*- coding: utf-8 -*-
import io, sys

P = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
src = io.open(P, 'r', encoding='utf-8').read()
edits = []

# ---------- 1. CSS：空层标记 ----------
a = '.layer-count{font:8px var(--mono);color:var(--muted);flex:0 0 auto}'
r = '''.layer-count{font:8px var(--mono);color:var(--muted);flex:0 0 auto}
.layer-count.empty{color:#A14E50;font-weight:700;letter-spacing:.5px}'''
edits.append((a, r, 'CSS 空层'))

# ---------- 2. 工具轨：魔棒 ----------
a = '<button class="tool-btn" data-tool="select"><span class="ticon">▦</span><span class="tname">选区</span><span class="tkey">M</span></button>'
r = '''<button class="tool-btn" data-tool="select"><span class="ticon">▦</span><span class="tname">选区</span><span class="tkey">M</span></button>
    <button class="tool-btn" data-tool="magic"><span class="ticon">✦</span><span class="tname">魔棒</span><span class="tkey">W</span></button>'''
edits.append((a, r, '魔棒按钮'))

# ---------- 3. 层底部按钮 ----------
a = '''      <div class="layer-foot">
        <button class="btn ghost" id="btnMergeLayer">合并向下</button>
        <button class="btn ghost" id="btnDelLayer">删除</button>
      </div>'''
r = '''      <div class="layer-foot">
        <button class="btn ghost" id="btnMergeLayer">合并向下</button>
        <button class="btn ghost" id="btnDupLayer" title="整层复制为一个同类新层">复制</button>
        <button class="btn ghost" id="btnMirrorLayer" title="整层左右翻转（原地镜像）">镜像</button>
        <button class="btn ghost" id="btnDelLayer">删除</button>
      </div>'''
edits.append((a, r, '层底部按钮'))

# ---------- 4. 空层标记（列表行） ----------
a = """        '<span class="layer-count" title="已上色格子数">' + count + '</span>' +"""
r = """        (count === 0 ? '<span class="layer-count empty" title="这一层还没有像素">空</span>' : '<span class="layer-count" title="已上色格子数">' + count + '</span>') +"""
edits.append((a, r, '空层标记行'))

# ---------- 5. 空层标记（增量刷新） ----------
a = '''    var cnt = row.querySelector('.layer-count');
    if (cnt) cnt.textContent = pixelCount(l);'''
r = '''    var cnt = row.querySelector('.layer-count');
    if (cnt) {
      var pc2 = pixelCount(l);
      cnt.textContent = pc2 === 0 ? '空' : pc2;
      cnt.classList.toggle('empty', pc2 === 0);
    }'''
edits.append((a, r, '空层标记刷新'))

# ---------- 6. 快捷键 W + 方向键 ----------
a = "  else if (key === 'm') setTool('select');"
r = "  else if (key === 'm') setTool('select');\n  else if (key === 'w') setTool('magic');"
edits.append((a, r, '快捷键 W'))

a = "  if (k === ' ' && !spaceDown) { spaceDown = true; e.preventDefault(); return; }"
r = """  if (k === 'ArrowLeft' || k === 'ArrowRight' || k === 'ArrowUp' || k === 'ArrowDown') {
    e.preventDefault();
    nudgeLayer(k === 'ArrowLeft' ? -1 : k === 'ArrowRight' ? 1 : 0,
               k === 'ArrowUp' ? -1 : k === 'ArrowDown' ? 1 : 0,
               e.shiftKey);
    return;
  }
  if (k === ' ' && !spaceDown) { spaceDown = true; e.preventDefault(); return; }"""
edits.append((a, r, '方向键偏移'))

# ---------- 7. 指针分支：魔棒 ----------
a = "  if (tool === 'bucket') {\n    var layer = paintTargetLayer();"
r = """  if (tool === 'magic') {
    if (!cell.inside) { clearSelection(); return; }
    var mgl = currentLayer();
    if (!mgl) { toast('当前没有图层', 'warn'); return; }
    if (mgl.locked) { toast('「' + mgl.display_name + '」已锁定，先解锁再选', 'warn'); return; }
    var mcode = mgl.pixels[cell.y * artwork.size + cell.x];
    if (mcode == null || mcode === 'transparent') {
      toast('这一格在当前层是空的，魔棒选不到连通块', 'warn');
      return;
    }
    magicSelect(cell.x, cell.y, mgl, e.altKey);
    return;
  }

  if (tool === 'bucket') {
    var layer = paintTargetLayer();"""
edits.append((a, r, '魔棒指针分支'))

# ---------- 8. 新函数 ----------
a = 'function addFrameFromLayer() {'
r = '''function maskToRects(mask, n) {
  var out = [], open = {};
  for (var y = 0; y < n; y++) {
    var runs = [];
    var x = 0;
    while (x < n) {
      if (!mask[y * n + x]) { x++; continue; }
      var sx = x;
      while (x < n && mask[y * n + x]) x++;
      runs.push([sx, x - 1]);
    }
    var nextOpen = {};
    runs.forEach(function (run) {
      var key = run[0] + ':' + run[1];
      var o = open[key];
      if (o && o.y1 === y - 1) { o.y1 = y; nextOpen[key] = o; }
      else {
        var nr = { x0: run[0], y0: y, x1: run[1], y1: y };
        out.push(nr); nextOpen[key] = nr;
      }
    });
    open = nextOpen;
  }
  return out;
}

function magicSelect(x0, y0, layer, eight) {
  var n = artwork.size;
  var target = layer.pixels[y0 * n + x0];
  var mask = new Uint8Array(n * n);
  var stack = [y0 * n + x0];
  mask[y0 * n + x0] = 1;
  while (stack.length) {
    var idx = stack.pop();
    var cx = idx % n, cy = (idx - cx) / n;
    var nb = eight
      ? [[cx - 1, cy], [cx + 1, cy], [cx, cy - 1], [cx, cy + 1], [cx - 1, cy - 1], [cx + 1, cy - 1], [cx - 1, cy + 1], [cx + 1, cy + 1]]
      : [[cx - 1, cy], [cx + 1, cy], [cx, cy - 1], [cx, cy + 1]];
    for (var i = 0; i < nb.length; i++) {
      var nx = nb[i][0], ny = nb[i][1];
      if (nx < 0 || ny < 0 || nx >= n || ny >= n) continue;
      var ni = ny * n + nx;
      if (mask[ni]) continue;
      var c = layer.pixels[ni];
      var same = (target == null || target === 'transparent')
        ? (c == null || c === 'transparent')
        : (c === target);
      if (!same) continue;
      mask[ni] = 1;
      stack.push(ni);
    }
  }
  var rects = maskToRects(mask, n);
  if (!rects.length) { toast('没有选中任何格子', 'warn'); return; }
  var total = rects.reduce(function (s, r0) { return s + (r0.x1 - r0.x0 + 1) * (r0.y1 - r0.y0 + 1); }, 0);
  applySelectionRects(rects, '魔棒：' + total + ' 格 · ' + rects.length + ' 块矩形（' + target + '）');
}

function nudgeLayer(dx, dy, big) {
  var l = currentLayer();
  if (!l) return;
  var step = big ? 5 : 1;
  var sx = dx * step, sy = dy * step;
  if (!sx && !sy) return;
  if (l.locked) { toast('「' + l.display_name + '」已锁定，先解锁再移', 'warn'); return; }
  var n = artwork.size;
  if (pixelCount(l) === 0) { toast('「' + l.display_name + '」还没有像素，无处可移', 'warn'); return; }
  pushUndo();
  var out = makeEmptyPixels(n);
  for (var y = 0; y < n; y++) {
    for (var x = 0; x < n; x++) {
      var c = l.pixels[y * n + x];
      if (c == null || c === 'transparent') continue;
      var nx2 = x + sx, ny2 = y + sy;
      if (nx2 < 0 || ny2 < 0 || nx2 >= n || ny2 >= n) continue;
      out[ny2 * n + nx2] = c;
    }
  }
  l.pixels = out;
  markLayerDirty(l, 0, 0, n - 1, n - 1);
  invalidateLayerCaches();
  commitChange('「' + l.display_name + '」整层偏移 ' + sx + ' , ' + sy + (big ? '（大步）' : ''));
}

function mirrorCurrentLayer() {
  var l = currentLayer();
  if (!l) return;
  if (l.locked) { toast('「' + l.display_name + '」已锁定，先解锁再镜像', 'warn'); return; }
  var n = artwork.size;
  if (pixelCount(l) === 0) { toast('「' + l.display_name + '」还没有像素', 'warn'); return; }
  pushUndo();
  var out = makeEmptyPixels(n);
  for (var y = 0; y < n; y++) {
    for (var x = 0; x < n; x++) out[y * n + (n - 1 - x)] = l.pixels[y * n + x];
  }
  l.pixels = out;
  l.anchor = { x: clamp(n - l.anchor.x, 0, n), y: l.anchor.y };
  markLayerDirty(l, 0, 0, n - 1, n - 1);
  invalidateLayerCaches();
  commitChange('「' + l.display_name + '」已水平镜像（锚点跟随翻转）');
}

function duplicateLayer(mirror) {
  var src2 = currentLayer();
  if (!src2) { toast('当前没有图层', 'warn'); return; }
  if (!canCreateType(src2.part_type)) {
    toast('「' + typeName(src2.part_type) + '」已达 ' + TYPE_MAP[src2.part_type].max + ' 层上限，不能再复制', 'err');
    return;
  }
  var n = artwork.size;
  if (pixelCount(src2) === 0) { toast('「' + src2.display_name + '」没有像素，复制出来仍是空的', 'warn'); return; }
  pushUndo();
  var idx = nextPartIndex(src2.part_type);
  var nl = makeLayer(n, src2.part_type, idx, {
    display_name: src2.display_name + (mirror ? '·镜像' : '·副本'),
    anchor: { x: src2.anchor.x, y: src2.anchor.y },
    settings: Object.assign({}, src2.settings)
  });
  nl.pixels = src2.pixels.slice();
  if (mirror) {
    var flip = makeEmptyPixels(n);
    for (var y = 0; y < n; y++) {
      for (var x = 0; x < n; x++) flip[y * n + (n - 1 - x)] = nl.pixels[y * n + x];
    }
    nl.pixels = flip;
    nl.anchor = { x: clamp(n - src2.anchor.x, 0, n), y: src2.anchor.y };
  }
  nl.visible = src2.visible;
  artwork.layers.push(nl);
  currentLayerId = nl.id;
  invalidateLayerCaches();
  refreshAllUI();
  commitChange((mirror ? '已镜像复制为「' : '已复制为「') + nl.display_name + '」');
}

function addFrameFromLayer() {'''
edits.append((a, r, '新函数群'))

# ---------- 9. 事件绑定 ----------
a = "  $('#btnMergeLayer').addEventListener('click', mergeDown);"
r = """  $('#btnMergeLayer').addEventListener('click', mergeDown);
  $('#btnDupLayer').addEventListener('click', function () { duplicateLayer(false); });
  $('#btnMirrorLayer').addEventListener('click', function () { mirrorCurrentLayer(); });"""
edits.append((a, r, '复制/镜像事件'))

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
print('WROTE chars=%d' % len(out))
