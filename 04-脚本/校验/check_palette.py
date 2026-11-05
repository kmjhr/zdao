# -*- coding: utf-8 -*-
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
t = io.open(os.path.join(ROOT, '02-原型', '拼豆板编辑器原型.html'), 'r', encoding='utf-8').read()
m = re.search(r'palette:\{([^}]*)\}', t)
pairs = re.findall(r'"([A-Z0-9]+)":"(#[0-9A-F]{6})"', m.group(1))
keys = [k for k, v in pairs]
mard = ['H1','H2','H3','H4','H5','H6','H7','G3','G7','G8','G9','G12','G14','G17',
        'E2','E4','E6','F2','F3','F8','F14','F19','A4','A6','A7','B5','B12','B14',
        'C4','C7','C8','C11','C17','C24','D4','D13','D18','D20']
print('palette 键数:', len(pairs))
print('缺失:', [k for k in mard if k not in keys])
print('多余:', [k for k in keys if k not in mard])
print('重复:', len(keys) - len(set(keys)))
# 检查姐姐 color 矩阵中的色号是否都在 palette
cm = re.search(r'color:JSON\.parse\(\'(\[.*?\])\'\)', t)
import json
mat = json.loads(cm.group(1).replace("'", '"'))
used = set()
for row in mat:
    for c in row:
        used.add(c)
print('矩阵用色:', sorted(used))
print('矩阵缺失色:', [c for c in sorted(used) if c not in keys])
