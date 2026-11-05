# -*- coding: utf-8 -*-
import io, sys, shutil, os

A = r'D:\codex\codex-data\youxi\编辑器原型\index.html'
B = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
BAK = r'D:\codex\codex-data\youxi\编辑器原型\index.bak-before-merge.html'

if not os.path.exists(BAK):
    shutil.copyfile(A, BAK)
    print('BACKUP -> ' + BAK)
else:
    print('BACKUP already exists: ' + BAK)

# 上一轮写坏的文件一律从备份还原后再合
shutil.copyfile(BAK, A)
print('RESTORED from backup, chars=%d' % len(io.open(A, encoding='utf-8').read()))

a = io.open(A, 'r', encoding='utf-8').read()
b_lines = io.open(B, 'r', encoding='utf-8').read().split('\n')

# ---- 从 B 抽取三个代码块 ----
code_block = '\n'.join(b_lines[1633:1762])    # 色号缓存函数群
tools_block = '\n'.join(b_lines[4447:4581])   # maskToRects .. duplicateLayer
draft_block = '\n'.join(b_lines[4582:4840])   # 草稿库

assert code_block.strip().startswith('/* ---------------- 色号标记离屏缓存'), code_block[:80]
assert 'function paintCodesVisible' in code_block and 'function ensureCodeCache' in code_block
assert tools_block.strip().startswith('function maskToRects'), tools_block[:80]
assert 'function duplicateLayer' in tools_block
assert tools_block.rstrip().endswith('}'), tools_block[-120:]
# 括号平衡自检：插入的块必须自圆其说
for name, blk in (('code', code_block), ('tools', tools_block), ('draft', draft_block)):
    o = blk.count('{') + blk.count('(') + blk.count('[')
    c = blk.count('}') + blk.count(')') + blk.count(']')
    if o != c:
        print('FAIL bracket imbalance in %s: %d vs %d' % (name, o, c))
        sys.exit(1)
    print('bracket ok %s (%d)' % (name, o))
assert draft_block.strip().startswith('/* ---------------- 草稿库'), draft_block[:80]
assert 'function openDraftsModal' in draft_block
print('blocks extracted ok: code=%d lines tools=%d lines draft=%d lines'
      % (len(code_block.split('\n')), len(tools_block.split('\n')), len(draft_block.split('\n'))))

edits = []

# 1. CSS
anchor = '.layer-count{font:8px var(--mono);color:var(--muted);flex:0 0 auto}'
repl = '.layer-count{font:8px var(--mono);color:var(--muted);flex:0 0 auto}\n' + '''.layer-count.empty{color:#A14E50;font-weight:700;letter-spacing:.5px}

/* 草稿库 */
.draft-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:10px}
.draft-item{border:2px solid var(--ink);background:var(--panel2);padding:8px;cursor:pointer;position:relative}
.draft-item:hover{border-color:var(--accent)}
.draft-item.active{border-color:var(--accent);background:#FFF6E0}
.draft-thumb{width:100%;height:auto;image-rendering:pixelated;background:#fff;border:1px solid #E4E3DD;display:block}
.draft-name{font:700 11px var(--font);margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.draft-meta{font:9px var(--mono);color:var(--muted);margin-top:2px}
.draft-del{position:absolute;top:3px;right:3px;width:18px;height:18px;border:1px solid var(--ink);background:#fff;font:11px var(--mono);line-height:1;cursor:pointer;padding:0;z-index:2}
.draft-del:hover{background:#A14E50;color:#fff;border-color:#A14E50}
.draft-note{font:10px/1.75 var(--font);color:var(--muted);margin-top:10px}'''
edits.append((anchor, repl, 'CSS'))

# 2. 色号按钮
anchor = '<button class="btn" id="btnNums" title="行列号（默认关）">行列号</button>'
repl = ('<button class="btn" id="btnNums" title="行列号（默认关）">行列号</button>\n'
        '      <button class="btn" id="btnCodes" title="色号：每格标出这一格最终看到的是哪层、什么色号（缩小到看不清时自动隐藏）">色号</button>')
edits.append((anchor, repl, '色号按钮'))

# 3. 作品按钮
anchor = '<button class="btn" id="btnNew" title="新建空白作品">新建</button>'
repl = ('<button class="btn" id="btnDrafts" title="作品 · 多个角色分开存">作品</button>\n'
        '      <button class="btn" id="btnNew" title="新建空白作品">新建</button>')
edits.append((anchor, repl, '作品按钮'))

# 4. 魔棒工具
anchor = '<button class="tool-btn" data-tool="select"><span class="ticon">▦</span><span class="tname">选区</span><span class="tkey">M</span></button>'
repl = ('<button class="tool-btn" data-tool="select"><span class="ticon">▦</span><span class="tname">选区</span><span class="tkey">M</span></button>\n'
        '    <button class="tool-btn" data-tool="magic"><span class="ticon">✦</span><span class="tname">魔棒</span><span class="tkey">W</span></button>')
edits.append((anchor, repl, '魔棒工具'))

# 5. 复制 / 镜像按钮
anchor = '<button class="btn ghost" id="btnMergeLayer">合并向下</button>'
repl = ('<button class="btn ghost" id="btnMergeLayer">合并向下</button>\n'
        '        <button class="btn ghost" id="btnDupLayer" title="整层复制为一个同类新层">复制</button>\n'
        '        <button class="btn ghost" id="btnMirrorLayer" title="整层左右翻转（原地镜像）">镜像</button>')
edits.append((anchor, repl, '复制镜像按钮'))

# 6. isDarkHex
anchor = 'function hexForCode(code) {'
repl = '''function isDarkHex(hex) {
  if (!hex) return false;
  var h = String(hex).replace('#', '');
  if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
  if (h.length !== 6) return false;
  var r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b2 = parseInt(h.slice(4, 6), 16);
  if (isNaN(r) || isNaN(g) || isNaN(b2)) return false;
  return (0.299 * r + 0.587 * g + 0.114 * b2) < 132;
}

function hexForCode(code) {'''
edits.append((anchor, repl, 'isDarkHex'))

# 7. showCodes
anchor = 'var showNumbers = false;'
repl = 'var showNumbers = false;\nvar showCodes = false;'
edits.append((anchor, repl, 'showCodes'))

# 8. 色号缓存常量
anchor = 'var COMPOSE_MAX_EDGE = 3072; // 合成缓存单边像素上限；超过则退回逐层合成'
repl = ('var COMPOSE_MAX_EDGE = 3072; // 合成缓存单边像素上限；超过则退回逐层合成\n'
        'var CODE_CACHE_MAX_EDGE = 2048; // 色号缓存单边像素上限；超过则退回可见区直绘\n'
        'var codeCache = null;')
edits.append((anchor, repl, '色号缓存常量'))

# 9. invalidate
anchor = 'function invalidateLayerCaches() { layerCache = {}; composeCache = null; }'
repl = 'function invalidateLayerCaches() { layerCache = {}; composeCache = null; codeCache = null; }'
edits.append((anchor, repl, 'invalidate'))

# 10. markLayerDirty
anchor = '  markComposeDirty(x0, y0, x1, y1);\n}'
repl = '  markComposeDirty(x0, y0, x1, y1);\n  markCodeDirty(x0, y0, x1, y1);\n}'
edits.append((anchor, repl, 'markLayerDirty'))

# 11. 色号缓存函数群
anchor = 'function ensureComposeCache(n, cellDev) {'
repl = code_block + '\n\nfunction ensureComposeCache(n, cellDev) {'
edits.append((anchor, repl, '色号缓存函数群'))

# 12. renderBoard 色号块
anchor = '  // 当前层锚点\n  var cur = currentLayer();'
repl = '''  // 色号标记（可开关）：走离屏缓存，平时只 blit 一次
  if (showCodes && cell >= 11) {
    var ccx = ensureCodeCache(n, cellDev);
    if (ccx) {
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(ccx.canvas, 0, 0, W, W);
      ctx.imageSmoothingEnabled = true;
    } else {
      paintCodesVisible(ctx, n, cell, ox, oy, cw, ch);
    }
  }

  // 当前层锚点
  var cur = currentLayer();'''
edits.append((anchor, repl, 'renderBoard 色号块'))

# 13. 魔棒 / 偏移 / 镜像 / 复制 / 草稿函数群
anchor = 'function addFrameFromLayer() {'
repl = tools_block + '\n\n' + draft_block + '\n\nfunction addFrameFromLayer() {'
edits.append((anchor, repl, '工具与草稿函数群'))

# 14. onPointerDown 魔棒分支
anchor = "  if (tool === 'bucket') {\n    var layer = paintTargetLayer();"
repl = '''  if (tool === 'magic') {
    var ml = paintTargetLayer();
    if (!ml || !cell.inside) return;
    magicSelect(cell.x, cell.y, ml, e.altKey);
    lastClickedCell = cell;
    requestRender();
    return;
  }

  if (tool === 'bucket') {
    var layer = paintTargetLayer();'''
edits.append((anchor, repl, '魔棒点击分支'))

# 15. onKeyDown 方向键
anchor = "  if (k === ' ' && !spaceDown) { spaceDown = true; e.preventDefault(); return; }"
repl = '''  if (k === 'ArrowLeft' || k === 'ArrowRight' || k === 'ArrowUp' || k === 'ArrowDown') {
    e.preventDefault();
    nudgeLayer(k === 'ArrowLeft' ? -1 : k === 'ArrowRight' ? 1 : 0,
               k === 'ArrowUp' ? -1 : k === 'ArrowDown' ? 1 : 0,
               e.shiftKey);
    return;
  }
  if (k === ' ' && !spaceDown) { spaceDown = true; e.preventDefault(); return; }'''
edits.append((anchor, repl, '方向键'))

# 16. W 快捷键
anchor = "  else if (key === 'm') setTool('select');"
repl = "  else if (key === 'm') setTool('select');\n  else if (key === 'w') setTool('magic');"
edits.append((anchor, repl, 'W 快捷键'))

# 17. bindEvents：色号 + 作品 + 层按钮 + beforeunload
anchor = "  $('#btnUndo').addEventListener('click', undo);"
repl = '''  $('#btnCodes').addEventListener('click', function () {
    showCodes = !showCodes;
    this.classList.toggle('active', showCodes);
    requestRender();
  });

  $('#btnUndo').addEventListener('click', undo);'''
edits.append((anchor, repl, 'bindEvents 色号'))

anchor = "  $('#btnNew').addEventListener('click', openNewModal);"
repl = '''  $('#btnDrafts').addEventListener('click', openDraftsModal);
  $('#btnNew').addEventListener('click', openNewModal);
  window.addEventListener('beforeunload', function () { flushDraftSave(); });'''
edits.append((anchor, repl, 'bindEvents 作品'))

anchor = "  $('#btnMergeLayer').addEventListener('click', mergeDown);"
repl = '''  $('#btnMergeLayer').addEventListener('click', mergeDown);
  $('#btnDupLayer').addEventListener('click', function () { duplicateLayer(false); });
  $('#btnMirrorLayer').addEventListener('click', function () { mirrorCurrentLayer(); });'''
edits.append((anchor, repl, 'bindEvents 层按钮'))

# 18. 空层标记
anchor = """'<span class="layer-count" title="已上色格子数">' + count + '</span>' +"""
repl = """(count === 0 ? '<span class="layer-count empty" title="这一层还没有像素">空</span>' : '<span class="layer-count" title="已上色格子数">' + count + '</span>') +"""
edits.append((anchor, repl, '空层标记'))

# 19. 计数只刷当前层
anchor = '''function refreshLayerListCountsOnly() {
  // 笔画结束后只刷新计数与状态，避免整表重建影响手感
  if (!artwork) return;
  var rows = $$('#layerList .layer-row');
  rows.forEach(function (row) {
    var l = layerById(row.getAttribute('data-layer-id'));
    if (!l) return;
    var cnt = row.querySelector('.layer-count');
    if (cnt) cnt.textContent = pixelCount(l);
  });
}'''
repl = '''function refreshLayerListCountsOnly() {
  // 一次笔画只会动当前层，所以只算这一层的格子数，不再遍历全部 17 层
  if (!artwork) return;
  var cur = currentLayer();
  if (!cur) return;
  var row = null;
  $$('#layerList .layer-row').forEach(function (r) {
    if (r.getAttribute('data-layer-id') === cur.id) row = r;
  });
  if (!row) return;
  var cnt = row.querySelector('.layer-count');
  if (!cnt) return;
  var pc2 = pixelCount(cur);
  cnt.textContent = pc2 === 0 ? '空' : pc2;
  cnt.classList.toggle('empty', pc2 === 0);
}'''
edits.append((anchor, repl, '计数只刷当前层'))

# 20. saveAutosave
anchor = '''function saveAutosave() {
  if (!artwork) return;
  try {
    localStorage.setItem(AUTOSAVE_KEY, JSON.stringify({
      artwork: JSON.parse(serializeArtwork()),
      current_layer_id: currentLayerId,
      saved_at: Date.now()
    }));'''
repl = '''function saveAutosave() {
  if (!artwork) return;
  try {
    localStorage.setItem(AUTOSAVE_KEY, JSON.stringify({
      artwork: artwork,
      current_layer_id: currentLayerId,
      saved_at: Date.now()
    }));'''
edits.append((anchor, repl, 'saveAutosave 瘦身'))

anchor = '''  } catch (e) {
    setSaveStatus('自动保存失败');
  }
}

function commitChange(msg) {'''
repl = '''  } catch (e) {
    setSaveStatus('自动保存失败');
  }
  scheduleDraftSave();
}

function commitChange(msg) {'''
edits.append((anchor, repl, 'saveAutosave 草稿延迟写'))

# 21. 新建作品接草稿
anchor = "        bootArtwork(createArtwork(size, preset), '已新建 ' + size + '×' + size + ' 作品');"
repl = '''        if (currentDraftId) saveDraftNow(currentDraftId, true);
        currentDraftId = uid('D');
        try { localStorage.setItem(DRAFT_CURRENT_KEY, currentDraftId); } catch (e) {}
        bootArtwork(createArtwork(size, preset), '已新建 ' + size + '×' + size + ' 作品');
        saveDraftNow(currentDraftId, true);'''
edits.append((anchor, repl, '新建作品接草稿'))

# 22. boot 建立草稿
anchor = '''  booted = true;
  scheduleAutosave();'''
repl = '''  booted = true;
  ensureDraftBoot();
  scheduleAutosave();'''
edits.append((anchor, repl, 'boot 建立草稿'))

for anchor, repl, label in edits:
    c = a.count(anchor)
    if c != 1:
        print('FAIL %s: count=%d' % (label, c))
        sys.exit(1)
    print('OK %s' % label)

out = a
for anchor, repl, label in edits:
    out = out.replace(anchor, repl, 1)

io.open(A, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE chars=%d' % len(out))
