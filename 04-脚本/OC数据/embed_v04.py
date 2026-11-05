# -*- coding: utf-8 -*-
"""把新版 29x29 双矩阵（eyes/mouth 拆分）嵌入编辑器 v0.4"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
j = json.load(open(os.path.join(ROOT, '03-美术资产', 'OC数据', 'bead_oc29_jiejie.json'), encoding='utf-8'))
p = os.path.join(ROOT, '02-原型', '拼豆板编辑器原型.html')
html = open(p, encoding='utf-8').read()

c = json.dumps(j['color'], separators=(',', ':'))
pt = json.dumps(j['part'], separators=(',', ':'))

pat_c = re.compile(r"color:JSON\.parse\('[^']*'\)")
pat_p = re.compile(r"part:JSON\.parse\('[^']*'\)")
n1, n2 = len(pat_c.findall(html)), len(pat_p.findall(html))
assert n1 == 1 and n2 == 1, (n1, n2)

html = pat_c.sub('color:JSON.parse(\'' + c + '\')', html, count=1)
html = pat_p.sub('part:JSON.parse(\'' + pt + '\')', html, count=1)
open(p, 'w', encoding='utf-8').write(html)

assert 'face' not in pt, 'face still in part data'
print('ok: data embedded, part tags:', sorted(set(t for row in j['part'] for t in row)))
