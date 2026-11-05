# -*- coding: utf-8 -*-
import io, sys

P = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
src = io.open(P, 'r', encoding='utf-8').read()
edits = []

# ---------- 1. 新增 codeCache 常量 ----------
a = 'var COMPOSE_MAX_EDGE = 3072; // 合成缓存单边像素上限；超过则退回逐层合成'
r = '''var COMPOSE_MAX_EDGE = 3072; // 合成缓存单边像素上限；超过则退回逐层合成
var CODE_CACHE_MAX_EDGE = 2048; // 色号缓存单边像素上限；超过则退回可见区直绘
var codeCache = null;'''
edits.append((a, r, 'codeCache 常量'))

# ---------- 2. invalidate 时一并清空色号缓存 ----------
a = 'function invalidateLayerCaches() { layerCache = {}; composeCache = null; }'
r = 'function invalidateLayerCaches() { layerCache = {}; composeCache = null; codeCache = null; }'
edits.append((a, r, 'invalidate 清色号缓存'))

# ---------- 3. markLayerDirty 追加色号脏区 ----------
a = '''  markComposeDirty(x0, y0, x1, y1);
}'''
r = '''  markComposeDirty(x0, y0, x1, y1);
  markCodeDirty(x0, y0, x1, y1);
}'''
edits.append((a, r, 'markLayerDirty 追加色号脏区'))

# ---------- 4. 色号缓存函数群（插在 ensureComposeCache 前） ----------
a = 'function ensureComposeCache(n, cellDev) {'
r = '''/* ---------------- 色号标记离屏缓存（只在数据/层/缩放变化时重绘，其余帧只 blit） ---------------- */
function markCodeDirty(x0, y0, x1, y1) {
  var c = codeCache;
  if (!c) return;
  x0 = Math.max(0, Math.min(x0, x1));
  y0 = Math.max(0, Math.min(y0, y1));
  x1 = Math.min(c.n - 1, Math.max(x0, x1));
  y1 = Math.min(c.n - 1, Math.max(y0, y1));
  if (!c.dirty) { c.dirty = { x0: x0, y0: y0, x1: x1, y1: y1 }; return; }
  c.dirty.x0 = Math.min(c.dirty.x0, x0);
  c.dirty.y0 = Math.min(c.dirty.y0, y0);
  c.dirty.x1 = Math.max(c.dirty.x1, x1);
  c.dirty.y1 = Math.max(c.dirty.y1, y1);
}

function codeCacheSig(n, cellDev) {
  var base = (composeCache && composeCache.n === n && composeCache.cell === cellDev)
    ? composeCache.sig
    : composeSig(n, cellDev);
  return base + '|' + currentLayerId;
}

function paintCodeRect(c, x0, y0, x1, y1) {
  var n = c.n, cs = c.cell, g = c.ctx;
  x0 = Math.max(0, x0); y0 = Math.max(0, y0);
  x1 = Math.min(n - 1, x1); y1 = Math.min(n - 1, y1);
  if (x1 < x0 || y1 < y0) return;
  g.clearRect(x0 * cs, y0 * cs, (x1 - x0 + 1) * cs, (y1 - y0 + 1) * cs);
  var ly = artwork.layers;
  var curL = null;
      for (var k0 = 0; k0 < ly.length; k0++) { if (ly[k0].id === currentLayerId) { curL = ly[k0]; break; } }
  g.font = '700 ' + Math.min(14, Math.round(cs * 0.55)) + 'px "Consolas", monospace';
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.lineWidth = Math.max(1, Math.round(cs * 0.14));
  for (var y = y0; y <= y1; y++) {
    for (var x = x0; x <= x1; x++) {
      var idx = y * n + x;
      var topCode = null;
      if (curL && curL.visible) {
        var pc = curL.pixels[idx];
        if (pc !== null && pc !== undefined && pc !== 'transparent') topCode = String(pc);
      }
      if (!topCode) {
        for (var li = ly.length - 1; li >= 0; li--) {
          var LC = ly[li];
          if (!LC.visible) continue;
          var cc = LC.pixels[idx];
          if (cc === null || cc === undefined || cc === 'transparent') continue;
          topCode = String(cc);
          break;
        }
      }
      if (!topCode) continue;
      var tpx = x * cs + cs / 2, tpy = y * cs + cs / 2;
      var darkBg = isDarkHex(hexForCode(topCode));
      g.fillStyle = darkBg ? 'rgba(255,255,255,.96)' : 'rgba(20,18,13,.92)';
      g.strokeStyle = darkBg ? 'rgba(0,0,0,.62)' : 'rgba(255,255,255,.88)';
      g.strokeText(topCode, tpx, tpy);
      g.fillText(topCode, tpx, tpy);
    }
  }
}

function ensureCodeCache(n, cellDev) {
  if (n * cellDev > CODE_CACHE_MAX_EDGE) { codeCache = null; return null; }
  var sig = codeCacheSig(n, cellDev);
  var c = codeCache;
  if (!c || c.n !== n || c.cell !== cellDev) {
    var size = n * cellDev;
    var canvas = document.createElement('canvas');
    canvas.width = size; canvas.height = size;
    c = { n: n, cell: cellDev, canvas: canvas, ctx: canvas.getContext('2d'), sig: sig, dirty: { x0: 0, y0: 0, x1: n - 1, y1: n - 1 } };
    codeCache = c;
  } else if (c.sig !== sig) {
    c.sig = sig;
    c.dirty = { x0: 0, y0: 0, x1: n - 1, y1: n - 1 };
  }
  if (c.dirty) {
    var r = c.dirty;
    c.dirty = null;
    paintCodeRect(c, r.x0, r.y0, r.x1, r.y1);
  }
  return c;
}

/* 超大缩放下不建缓存，直接只画屏幕可见的格子 */
function paintCodesVisible(ctx, n, cell, ox, oy, cw, ch) {
  var vx0 = Math.max(0, Math.floor(-ox / cell));
  var vy0 = Math.max(0, Math.floor(-oy / cell));
  var vx1 = Math.min(n - 1, Math.ceil((cw - ox) / cell) - 1);
  var vy1 = Math.min(n - 1, Math.ceil((ch - oy) / cell) - 1);
  if (vx1 < vx0 || vy1 < vy0) return;
  var ly = artwork.layers;
  var curL = null;
  for (var k0 = 0; k0 < ly.length; k0++) { if (ly[k0].id === currentLayerId) { curL = ly[k0]; break; } }
  ctx.font = '700 ' + Math.min(14, Math.round(cell * 0.55)) + 'px "Consolas", monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.lineWidth = Math.max(1, Math.round(cell * 0.14));
  for (var y = vy0; y <= vy1; y++) {
    for (var x = vx0; x <= vx1; x++) {
      var idx = y * n + x;
      var topCode = null;
      if (curL && curL.visible) {
        var pc = curL.pixels[idx];
        if (pc !== null && pc !== undefined && pc !== 'transparent') topCode = String(pc);
      }
      if (!topCode) {
        for (var li = ly.length - 1; li >= 0; li--) {
          var LC = ly[li];
          if (!LC.visible) continue;
          var cc = LC.pixels[idx];
          if (cc === null || cc === undefined || cc === 'transparent') continue;
          topCode = String(cc);
          break;
        }
      }
      if (!topCode) continue;
      var tpx = x * cell + cell / 2, tpy = y * cell + cell / 2;
      var darkBg = isDarkHex(hexForCode(topCode));
      ctx.fillStyle = darkBg ? 'rgba(255,255,255,.96)' : 'rgba(20,18,13,.92)';
      ctx.strokeStyle = darkBg ? 'rgba(0,0,0,.62)' : 'rgba(255,255,255,.88)';
      ctx.strokeText(topCode, tpx, tpy);
      ctx.fillText(topCode, tpx, tpy);
    }
  }
  ctx.lineWidth = 1;
}

function ensureComposeCache(n, cellDev) {'''
edits.append((a, r, '色号缓存函数群'))

# ---------- 5. renderBoard 色号块改为 blit ----------
a = '''  // 色号标记（可开关）：先看当前层，当前层这格为空则取最上可见层
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
  }'''
r = '''  // 色号标记（可开关）：走离屏缓存，平时只 blit 一次
  if (showCodes && cell >= 11) {
    var ccx = ensureCodeCache(n, cellDev);
    if (ccx) {
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(ccx.canvas, 0, 0, W, W);
      ctx.imageSmoothingEnabled = true;
    } else {
      paintCodesVisible(ctx, n, cell, ox, oy, cw, ch);
    }
  }'''
edits.append((a, r, 'renderBoard 色号改 blit'))

# ---------- 6. saveAutosave 改造（去掉多余解析 + 草稿改延迟写） ----------
a = '''function saveAutosave() {
  if (!artwork) return;
  try {
    localStorage.setItem(AUTOSAVE_KEY, JSON.stringify({
      artwork: JSON.parse(serializeArtwork()),
      current_layer_id: currentLayerId,
      saved_at: Date.now()
    }));
    var d = new Date();
    setSaveStatus('已保存 ' + pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds()));
  } catch (e) {
    setSaveStatus('自动保存失败');
  }
  if (currentDraftId) saveDraftNow(currentDraftId, false);
}'''
r = '''function saveAutosave() {
  if (!artwork) return;
  try {
    localStorage.setItem(AUTOSAVE_KEY, JSON.stringify({
      artwork: artwork,
      current_layer_id: currentLayerId,
      saved_at: Date.now()
    }));
    var d = new Date();
    setSaveStatus('已保存 ' + pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds()));
  } catch (e) {
    setSaveStatus('自动保存失败');
  }
  scheduleDraftSave();
}'''
edits.append((a, r, 'saveAutosave 瘦身'))

# ---------- 7. saveDraftNow 去掉重复序列化 ----------
a = '''function saveDraftNow(id, withThumb) {
  if (!artwork || !id) return false;
  var payload = {
    artwork: JSON.parse(serializeArtwork()),
    current_layer_id: currentLayerId,
    saved_at: Date.now()
  };
  try {
    localStorage.setItem(DRAFT_ITEM_PREFIX + id, JSON.stringify(payload));
  } catch (e) {'''
r = '''function saveDraftNow(id, withThumb) {
  if (!artwork || !id) return false;
  var savedAt = Date.now();
  var payloadText = JSON.stringify({
    artwork: artwork,
    current_layer_id: currentLayerId,
    saved_at: savedAt
  });
  draftSaveTimer = null;
  try {
    localStorage.setItem(DRAFT_ITEM_PREFIX + id, payloadText);
  } catch (e) {'''
edits.append((a, r, 'saveDraftNow 去重复序列化'))

a = '''  hit.updated = payload.saved_at;
  if (withThumb || !hit.progress) {'''
r = '''  hit.updated = savedAt;
  if (withThumb || !hit.progress) {'''
edits.append((a, r, 'saveDraftNow 时间字段'))

# ---------- 8. 增加草稿延迟写与 flush ----------
a = '''var currentDraftId = null;
var draftFullWarned = false;'''
r = '''var currentDraftId = null;
var draftFullWarned = false;
var draftSaveTimer = null;

/* 草稿写盘比自动保存慢一档：笔画停下 3 秒才落一次，避免每 450ms 同步写两遍 230KB */
function scheduleDraftSave() {
  if (!currentDraftId) return;
  if (draftSaveTimer) clearTimeout(draftSaveTimer);
  draftSaveTimer = setTimeout(function () {
    draftSaveTimer = null;
    saveDraftNow(currentDraftId, false);
  }, 3000);
}

function flushDraftSave() {
  if (draftSaveTimer) { clearTimeout(draftSaveTimer); draftSaveTimer = null; }
  if (currentDraftId) saveDraftNow(currentDraftId, false);
}'''
edits.append((a, r, '草稿延迟写函数'))

# ---------- 9. 切草稿前先 flush ----------
a = '''  if (currentDraftId) saveDraftNow(currentDraftId, true);
  currentDraftId = id;
  try { localStorage.setItem(DRAFT_CURRENT_KEY, id); } catch (e) { /* 忽略 */ }
  closeModal();
  bootArtwork(next, '已切到另一个草稿');'''
r = '''  if (currentDraftId) { if (draftSaveTimer) { clearTimeout(draftSaveTimer); draftSaveTimer = null; } saveDraftNow(currentDraftId, true); }
  currentDraftId = id;
  try { localStorage.setItem(DRAFT_CURRENT_KEY, id); } catch (e) { /* 忽略 */ }
  closeModal();
  bootArtwork(next, '已切到另一个草稿');'''
edits.append((a, r, '切草稿先 flush'))

# ---------- 10. beforeunload 落一次 ----------
a = "  $('#btnDrafts').addEventListener('click', openDraftsModal);"
r = """  $('#btnDrafts').addEventListener('click', openDraftsModal);
  window.addEventListener('beforeunload', function () { flushDraftSave(); });"""
edits.append((a, r, 'beforeunload 落盘'))

# ---------- 11. 笔画结束只刷当前层计数 ----------
a = '''function refreshLayerListCountsOnly() {
  // 笔画结束后只刷新计数与状态，避免整表重建影响手感
  if (!artwork) return;
  var rows = $$('#layerList .layer-row');
  rows.forEach(function (row) {
    var l = layerById(row.getAttribute('data-layer-id'));
    if (!l) return;
    var cnt = row.querySelector('.layer-count');
    if (cnt) {
      var pc2 = pixelCount(l);
      cnt.textContent = pc2 === 0 ? '空' : pc2;
      cnt.classList.toggle('empty', pc2 === 0);
    }
  });
}'''
r = '''function refreshLayerListCountsOnly() {
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
edits.append((a, r, '计数只刷当前层'))

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
