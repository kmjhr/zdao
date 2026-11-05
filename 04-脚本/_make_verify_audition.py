# -*- coding: utf-8 -*-
import io

SRC = r'D:\codex\codex-data\youxi\编辑器原型\index.html'
OUT = r'D:\codex\codex-data\youxi\编辑器原型\_verify_audition.html'

src = io.open(SRC, 'r', encoding='utf-8').read()

inject = '''<script>
(function () {
  var rep = [];
  setTimeout(function () {
    switchTab('character');
    rep.push('角色页=' + (document.getElementById('pane-character') ? 'ok' : 'missing'));
    if (typeof auditionMotion === 'function') {
      auditionMotion('blink');
      rep.push('试播 previewState=' + (previewState ? 'yes' : 'no') +
               ' tracks=' + (previewState && previewState.tracks ? Object.keys(previewState.tracks).length : 0));
      rep.push('timer=' + (auditionTimer ? 'on' : 'off'));
    } else {
      rep.push('auditionMotion 缺失');
    }
  }, 300);
  setTimeout(function () {
    if (typeof renderCharacter === 'function') {
      rep.push('renderCharacter 存在');
    }
    var el = document.createElement('div');
    el.style.cssText = 'position:fixed;left:8px;bottom:36px;z-index:99999;background:#111;color:#fff;font:11px monospace;padding:6px 10px;border-radius:3px;line-height:1.7';
    el.textContent = 'TEST: ' + rep.join(' | ');
    document.body.appendChild(el);
  }, 700);
})();
</script>
</body>'''

assert src.count('</body>') == 1
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(src.replace('</body>', inject, 1))
print('AUDITION VERIFY WRITTEN')
