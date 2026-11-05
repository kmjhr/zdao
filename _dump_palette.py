# -*- coding: utf-8 -*-
import io, json

P = r"D:\codex\codex-data\youxi\编辑器原型\mard-colors.sample.json"
d = json.load(io.open(P, encoding="utf-8"))
print("count", len(d["colors"]))
pairs = []
for c in d["colors"]:
    pairs.append('"' + c["code"] + '":"' + c["hex"] + '"')
line = ",".join(pairs)
print(line)
print("len", len(line))
