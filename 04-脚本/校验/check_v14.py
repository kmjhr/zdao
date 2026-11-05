# -*- coding: utf-8 -*-
"""v1.4 交付前校验：结构、需求计数、表格列数、残留词"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "01-需求文档", "纸上岛-项目需求与功能书.md")
s = io.open(P, encoding="utf-8").read()
lines = s.split("\n")

print("LEN %d LINES %d" % (len(s), len(lines)))
print("R 标题 %d" % len(re.findall(r"(?m)^#### R0\d\d", s)))
print("R083 占位 %s" % ("有" if "R083 已删除" in s else "无"))
print("H2:")
for m in re.finditer(r"(?m)^## .+$", s):
    print("   ", s.count("\n", 0, m.start()) + 1, m.group())

bad = []
inblock = []
infence = False
for i, ln in enumerate(lines, 1):
    if ln.strip().startswith("```"):
        infence = not infence
        inblock = []
        continue
    if infence:
        continue
    if ln.startswith("|"):
        inblock.append((i, ln.count("|")))
    else:
        if inblock:
            w = inblock[0][1]
            for n, c in inblock:
                if c != w:
                    bad.append((n, c, w))
            inblock = []

print("表格列不一致行:", bad[:12], "共", len(bad))

words = ["演出", "演绎", "BYO", "API", "LLM", "调模型", "符号文本", "performance", "R074", "R037"]
for w in words:
    hits = [(s.count("\n", 0, m.start()) + 1) for m in re.finditer(w, s)]
    print("  %-12s %d %s" % (w, len(hits), hits[:8]))
