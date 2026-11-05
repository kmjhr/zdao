# -*- coding: utf-8 -*-
import io, re

P = r"D:\codex\codex-data\youxi\02-原型\上帝之手-demo.html"
with io.open(P, "r", encoding="utf-8", newline="") as f:
    s = f.read()

# 取最后一个裸 <script> 块
blocks = re.findall(r"<script>(.*?)</script>", s, re.S)
print("script blocks=", len(blocks))
js = blocks[-1]
out = r"D:\codex\codex-data\youxi\_demo_check.js"
with io.open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)
print("js chars=", len(js))
print("html bytes=", len(s.encode("utf-8")))
