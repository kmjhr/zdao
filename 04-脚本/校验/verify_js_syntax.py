# -*- coding: utf-8 -*-
import io, os, re, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "02-原型", "拼豆板编辑器原型.html")
s = io.open(P, encoding="utf-8").read()
blocks = re.findall(r"<script>(.*?)</script>", s, re.S)
io.open(os.path.join(tempfile.gettempdir(), "_editor_js_check.js"), "w", encoding="utf-8").write("\n".join(blocks))
print("blocks=%d chars=%d" % (len(blocks), sum(len(b) for b in blocks)))
