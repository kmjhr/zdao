# -*- coding: utf-8 -*-
import io, sys

P = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
src = io.open(P, 'r', encoding='utf-8').read()
edits = []

# ---------- 1. CSS ----------
a = '.layer-count.empty{color:#A14E50;font-weight:700;letter-spacing:.5px}'
r = '''.layer-count.empty{color:#A14E50;font-weight:700;letter-spacing:.5px}

/* 草稿库 */
.draft-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:10px}
.draft-item{border:2px solid var(--ink);background:var(--panel2);padding:8px;cursor:pointer;position:relative}
.draft-item:hover{border-color:var(--accent)}
.draft-item.active{border-color:var(--accent);background:#FFF6E0}
.draft-thumb{width:100%;aspect-ratio:1;image-rendering:pixelated;background:#fff;border:1px solid #E4E3DD;display:block}
.draft-name{font:700 11px var(--font);margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.draft-meta{font:9px var(--mono);color:var(--muted);margin-top:2px}
.draft-del{position:absolute;top:3px;right:3px;width:18px;height:18px;border:1px solid var(--ink);background:#fff;font:11px var(--mono);line-height:1;cursor:pointer;padding:0;z-index:2}
.draft-del:hover{background:#A14E50;color:#fff;border-color:#A14E50}
.draft-note{font:10px/1.75 var(--font);color:var(--muted);margin-top:10px}'''
edits.append((a, r, 'CSS 草稿库'))

# ---------- 2. 顶栏按钮 ----------
a = '      <button class="btn" id="btnNew" title="新建空白作品">新建</button>'
r = '''      <button class="btn" id="btnDrafts" title="作品 · 多个角色分开存">作品</button>
      <button class="btn" id="btnNew" title="新建空白作品">新建</button>'''
edits.append((a, r, '顶栏作品按钮'))

# ---------- 3. 新建改造 ----------
a = "        bootArtwork(createArtwork(size, preset), '已新建 ' + size + '×' + size + ' 作品');"
r = '''        if (currentDraftId) saveDraftNow(currentDraftId, true);
        currentDraftId = uid('D');
        try { localStorage.setItem(DRAFT_CURRENT_KEY, currentDraftId); } catch (e) {}
        bootArtwork(createArtwork(size, preset), '已新建 ' + size + '×' + size + ' 作品');
        saveDraftNow(currentDraftId, true);'''
edits.append((a, r, '新建改造'))

# ---------- 4. 自动保存追加草稿 ----------
a = '''    var d = new Date();
    setSaveStatus('已保存 ' + pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds()));
  } catch (e) {
    setSaveStatus('自动保存失败');
  }
}'''
r = '''    var d = new Date();
    setSaveStatus('已保存 ' + pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds()));
  } catch (e) {
    setSaveStatus('自动保存失败');
  }
  if (currentDraftId) saveDraftNow(currentDraftId, false);
}'''
edits.append((a, r, '自动保存写草稿'))

# ---------- 5. boot 里建立草稿 ----------
a = '''  booted = true;
  scheduleAutosave();'''
r = '''  booted = true;
  ensureDraftBoot();
  scheduleAutosave();'''
edits.append((a, r, 'boot 建立草稿'))

# ---------- 6. 事件绑定 ----------
a = "  $('#btnNew').addEventListener('click', openNewModal);"
r = """  $('#btnDrafts').addEventListener('click', openDraftsModal);
  $('#btnNew').addEventListener('click', openNewModal);"""
edits.append((a, r, '作品按钮事件'))

# ---------- 7. 草稿函数群 ----------
a = 'function addFrameFromLayer() {'
r = '''/* ---------------- 草稿库：多个角色分开存 ---------------- */
var DRAFT_INDEX_KEY = 'papersisland.editor.drafts.index.v1';
var DRAFT_ITEM_PREFIX = 'papersisland.editor.draft.';
var DRAFT_CURRENT_KEY = 'papersisland.editor.drafts.current.v1';
var DRAFT_MAX = 8;
var currentDraftId = null;
var draftFullWarned = false;

function readDraftIndex() {
  try {
    var raw = localStorage.getItem(DRAFT_INDEX_KEY);
    if (!raw) return [];
    var v = JSON.parse(raw);
    return Array.isArray(v) ? v : [];
  } catch (e) { return []; }
}

function writeDraftIndex(list) {
  try { localStorage.setItem(DRAFT_INDEX_KEY, JSON.stringify(list)); } catch (e) { /* 空间满由 saveDraftNow 报 */ }
}

function draftProgressOf(art) {
  var hasHead = false, hasTorso = false, painted = 0;
  var arr = (art && art.layers) || [];
  arr.forEach(function (l) {
    var c = 0;
    for (var i = 0; i < l.pixels.length; i++) {
      var v = l.pixels[i];
      if (v != null && v !== 'transparent') c++;
    }
    if (c > 0) painted++;
    if (l.part_type === 'head' && c > 0) hasHead = true;
    if (l.part_type === 'torso' && c > 0) hasTorso = true;
  });
  return { must: (hasHead ? 1 : 0) + (hasTorso ? 1 : 0), painted: painted, total: arr.length };
}

function draftThumbOf(art) {
  try {
    var n = art.size;
    var cv = document.createElement('canvas');
    cv.width = n; cv.height = n;
    var g = cv.getContext('2d');
    var arr = art.layers || [];
    for (var li = 0; li < arr.length; li++) {
      var L = arr[li];
      if (!L.visible) continue;
      for (var y = 0; y < n; y++) {
        for (var x = 0; x < n; x++) {
          var c = L.pixels[y * n + x];
          if (c == null || c === 'transparent') continue;
          var hex = hexForCode(c);
          if (hex) { g.fillStyle = hex; g.fillRect(x, y, 1, 1); }
        }
      }
    }
    return cv.toDataURL();
  } catch (e) { return ''; }
}

function saveDraftNow(id, withThumb) {
  if (!artwork || !id) return false;
  var payload = {
    artwork: JSON.parse(serializeArtwork()),
    current_layer_id: currentLayerId,
    saved_at: Date.now()
  };
  try {
    localStorage.setItem(DRAFT_ITEM_PREFIX + id, JSON.stringify(payload));
  } catch (e) {
    setSaveStatus('草稿存不下');
    if (!draftFullWarned) {
      draftFullWarned = true;
      toast('草稿存不下：浏览器本地空间满了。先「导出」备份一份，再删掉别的草稿。', 'err');
    }
    return false;
  }
  var list = readDraftIndex();
  var hit = null;
  list.forEach(function (d) { if (d.id === id) hit = d; });
  if (!hit) {
    hit = { id: id, name: '未命名 OC', updated: Date.now(), thumb: '', progress: null };
    list.push(hit);
  }
  hit.updated = payload.saved_at;
  if (withThumb || !hit.progress) {
    hit.thumb = draftThumbOf(artwork);
    hit.progress = draftProgressOf(artwork);
  }
  writeDraftIndex(list);
  return true;
}

function timeAgo(ts) {
  var d = Date.now() - ts;
  if (!isFinite(d) || d < 0) return '刚刚';
  if (d < 60000) return '刚刚';
  if (d < 3600000) return Math.floor(d / 60000) + ' 分钟前';
  if (d < 86400000) return Math.floor(d / 3600000) + ' 小时前';
  return Math.floor(d / 86400000) + ' 天前';
}

function ensureDraftBoot() {
  var list = readDraftIndex();
  var saved = null;
  try { saved = localStorage.getItem(DRAFT_CURRENT_KEY); } catch (e) { saved = null; }
  if (list.length) {
    var hit = null;
    list.forEach(function (d) { if (d.id === saved) hit = d; });
    if (!hit) {
      hit = list.slice().sort(function (a, b) { return b.updated - a.updated; })[0];
    }
    currentDraftId = hit.id;
    try { localStorage.setItem(DRAFT_CURRENT_KEY, hit.id); } catch (e) { /* 忽略 */ }
    return;
  }
  var id = uid('D');
  currentDraftId = id;
  try { localStorage.setItem(DRAFT_CURRENT_KEY, id); } catch (e) { /* 忽略 */ }
  saveDraftNow(id, true);
  var l2 = readDraftIndex();
  l2.forEach(function (d) { if (d.id === id) d.name = '未命名 OC'; });
  writeDraftIndex(l2);
}

function loadDraft(id) {
  if (!id) return;
  if (id === currentDraftId) { closeModal(); return; }
  var raw = null;
  try { raw = localStorage.getItem(DRAFT_ITEM_PREFIX + id); } catch (e) { raw = null; }
  if (!raw) { toast('这个草稿读不出来', 'err'); return; }
  var payload = null;
  try { payload = JSON.parse(raw); } catch (e) { payload = null; }
  if (!payload || !payload.artwork) { toast('草稿内容不完整', 'err'); return; }
  var next = null;
  try { next = normalizeV2(payload.artwork); } catch (e) { next = null; }
  if (!next) { toast('草稿格式认不出来', 'err'); return; }
  if (currentDraftId) saveDraftNow(currentDraftId, true);
  currentDraftId = id;
  try { localStorage.setItem(DRAFT_CURRENT_KEY, id); } catch (e) { /* 忽略 */ }
  closeModal();
  bootArtwork(next, '已切到另一个草稿');
  if (payload.current_layer_id && layerById(payload.current_layer_id)) {
    currentLayerId = payload.current_layer_id;
    refreshAllUI();
    requestRender();
  }
}

function newDraftFromCurrent() {
  var list = readDraftIndex();
  if (list.length >= DRAFT_MAX) {
    toast('最多 ' + DRAFT_MAX + ' 个草稿。先删掉一个不再需要的，或者「导出」成文件存着。', 'err');
    return;
  }
  if (currentDraftId) saveDraftNow(currentDraftId, true);
  var id = uid('D');
  currentDraftId = id;
  try { localStorage.setItem(DRAFT_CURRENT_KEY, id); } catch (e) { /* 忽略 */ }
  saveDraftNow(id, true);
  var l = readDraftIndex();
  var nm = 'OC ' + l.length;
  l.forEach(function (d) { if (d.id === id) d.name = nm; });
  writeDraftIndex(l);
  closeModal();
  toast('已存为「' + nm + '」', 'ok');
}

function deleteDraft(id) {
  if (!id) return;
  var list = readDraftIndex();
  var hit = null;
  list.forEach(function (d) { if (d.id === id) hit = d; });
  var nm = hit ? hit.name : '这个草稿';
  if (currentDraftId === id) {
    toast('不能删当前正在编辑的草稿。先切到别的草稿再删它。', 'warn');
    return;
  }
  try { localStorage.removeItem(DRAFT_ITEM_PREFIX + id); } catch (e) { /* 忽略 */ }
  writeDraftIndex(list.filter(function (d) { return d.id !== id; }));
  toast('已删除「' + nm + '」', 'ok');
  openDraftsModal();
}

function openDraftsModal() {
  if (currentDraftId) saveDraftNow(currentDraftId, true);
  var list = readDraftIndex().slice().sort(function (a, b) { return b.updated - a.updated; });
  var body = '';
  if (!list.length) {
    body = '<div class="type-note">还没有草稿。点下方「存为新草稿」把当前作品存成一份。</div>';
  } else {
    body = '<div class="draft-grid">' + list.map(function (d) {
      var pr = d.progress || { must: 0, painted: 0, total: 0 };
      return '<div class="draft-item' + (d.id === currentDraftId ? ' active' : '') + '" data-draft-id="' + esc(d.id) + '">' +
        (d.thumb ? '<img class="draft-thumb" src="' + d.thumb + '" alt="">' : '<div class="draft-thumb"></div>') +
        '<div class="draft-name">' + esc(d.name) + '</div>' +
        '<div class="draft-meta">必填 ' + pr.must + '/2 · 已画 ' + pr.painted + '/' + pr.total + ' 层</div>' +
        '<div class="draft-meta">' + timeAgo(d.updated) + '</div>' +
        '<button class="draft-del" data-del="' + esc(d.id) + '" title="删除这个草稿">✕</button>' +
        '</div>';
    }).join('') + '</div>' +
      '<div class="draft-note">点一个卡片就切过去，切之前当前作品会自动存好。<br>' +
      '最多 ' + DRAFT_MAX + ' 个。存不下了就删旧的，或者用「导出」存成文件——文件比只放在浏览器里安全。</div>';
  }
  showModal({
    title: '作品 · 草稿',
    width: '560px',
    body: body,
    buttons: [
      { label: '关闭', kind: 'ghost' },
      { label: '存为新草稿', primary: true, onClick: function () { newDraftFromCurrent(); return false; } }
    ],
    onMount: function (api) {
      $$('.draft-item', api.root).forEach(function (el) {
        el.addEventListener('click', function (e) {
          if (e.target.closest('.draft-del')) return;
          loadDraft(el.getAttribute('data-draft-id'));
        });
      });
      $$('.draft-del', api.root).forEach(function (btn) {
        btn.addEventListener('click', function (e) {
          e.stopPropagation();
          var did = btn.getAttribute('data-del');
          if (btn.getAttribute('data-armed') === '1') { deleteDraft(did); return; }
          btn.setAttribute('data-armed', '1');
          btn.textContent = '确定?';
          btn.style.width = 'auto';
          btn.style.padding = '0 4px';
          setTimeout(function () {
            if (!btn.parentNode) return;
            btn.removeAttribute('data-armed');
            btn.textContent = '✕';
            btn.style.width = '18px';
            btn.style.padding = '0';
          }, 2500);
        });
      });
    }
  });
}

function addFrameFromLayer() {'''
edits.append((a, r, '草稿函数群'))

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
