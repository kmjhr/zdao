# -*- coding: utf-8 -*-
import io

SRC = r"D:\codex\codex-data\youxi\02-原型\上帝之手-demo.html"
with io.open(SRC, "r", encoding="utf-8", newline="") as f:
    s = f.read()

probe = """
<script>
(function () {
  var L = [];
  function flush() {
    var d = document.getElementById('__probe');
    if (!d) {
      d = document.createElement('div');
      d.id = '__probe';
      d.style.cssText = 'position:fixed;left:6px;top:6px;z-index:999;background:#000;font:11px/1.65 monospace;padding:8px;max-width:720px;white-space:pre-wrap;color:#4dff4d';
      document.body.appendChild(d);
    }
    d.textContent = L.join('\\n');
  }
  function clickTab(t) {
    var b = document.querySelector('.tab[data-tab="' + t + '"]');
    if (b) { b.click(); return true; }
    return false;
  }
  function fire(el) {
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }
  function onChips() {
    var a = document.querySelectorAll('#wordChips .chip.on');
    return Array.prototype.map.call(a, function (x) { return x.textContent; }).join('/');
  }

  setTimeout(function () {
    L.push('cardVisible=' + (card.style.opacity === '1' ? 'YES' : 'NO:' + card.style.opacity));
    L.push('putDisabled=' + putBtn.disabled);
    L.push('badgeOn=' + badge.classList.contains('on'));

    document.getElementById('info').click();
    setTimeout(function () {
      L.push('detOpen=' + detMask.classList.contains('on'));
      L.push('tabCount=' + document.querySelectorAll('.tab').length);
      L.push('hasNameInput=' + !!document.getElementById('fName'));

      var n = document.getElementById('fName');
      n.value = '阿岚'; fire(n);
      var bd = document.getElementById('fBirth');
      bd.value = '04-12'; fire(bd);
      L.push('nameOnCard=' + document.getElementById('ocname').textContent);
      L.push('metaOnCard=' + document.getElementById('meta').textContent);

      clickTab('pers');
      setTimeout(function () {
        L.push('wordChipCount=' + document.querySelectorAll('#wordChips [data-w]').length);

        document.querySelector('#wordChips [data-w="话痨"]').click();
        setTimeout(function () {
          document.querySelector('#wordChips [data-w="急性子"]').click();
          setTimeout(function () {
            document.querySelector('#wordChips [data-w="心软"]').click();
            setTimeout(function () {
              L.push('wordsOn=' + onChips());
              L.push('express=' + (document.querySelector('[data-axv="express"]') || {}).textContent);
              L.push('tempo=' + (document.querySelector('[data-axv="tempo"]') || {}).textContent);
              L.push('social=' + (document.querySelector('[data-axv="social"]') || {}).textContent);
              L.push('volatile=' + (document.querySelector('[data-axv="volatile"]') || {}).textContent);
              L.push('sliderDisabled=' + (document.querySelector('[data-ax="express"]') || {}).disabled);
              var cf = document.querySelector('#cfChips .chip.on');
              L.push('conflictOn=' + (cf ? cf.textContent : 'NONE'));

              document.getElementById('detSave').click();
              setTimeout(function () {
                L.push('detClosed=' + !detMask.classList.contains('on'));
                L.push('wordsOnCard=' + document.getElementById('words').textContent);
                L.push('wordsClass=' + document.getElementById('words').className);

                document.getElementById('photo').click();
                setTimeout(function () {
                  L.push('imgOpen=' + imgMask.classList.contains('on'));
                  L.push('imgPrevText=' + document.getElementById('imgprev').textContent.trim());
                  L.push('badgeAfter=' + badge.classList.contains('on'));
                  L.push('putDisabledAfter=' + putBtn.disabled);
                  flush();
                }, 200);
              }, 220);
            }, 140);
          }, 140);
        }, 140);
      }, 240);
    }, 300);
  }, 2600);
})();
</script>
"""

body = s.replace("</body>", probe + "</body>", 1)
out = r"D:\codex\codex-data\youxi\_verify_card.html"
with io.open(out, "w", encoding="utf-8", newline="") as f:
    f.write(body)
print("ok")
