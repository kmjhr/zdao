# -*- coding: utf-8 -*-
"""29x29 市面拼豆图纸样式：姐姐（深灰大衣·栗色卷发）
palette 键 = 市面图纸色号（字母+数字），每格标色号，玩家照图纸拼
part 标签：hair/head/eyes/mouth/upper/lower/top/pants/coat/shoes/acc（眼睛/嘴巴独立层，驱动眨眼/说话动画）
"""
import json

N = 29
PAL = {
    'B2': '#F6F1E7',   # 板底
    'F5': '#F2C9A0',   # 肤色亮
    'F6': '#EAC18F',   # 肤色
    'F7': '#DAAC7A',   # 肤色影
    'P1': '#E9B5AA',   # 腮红
    'P2': '#C67C70',   # 唇
    'H1': '#925E3E',   # 发高光
    'H2': '#7B4A2F',   # 栗发
    'H3': '#56321D',   # 发影
    'E1': '#34261C',   # 眼
    'E2': '#FFFFFF',   # 高光
    'C1': '#707070',   # 大衣亮
    'C2': '#585858',   # 大衣
    'C3': '#383838',   # 大衣暗
    'C4': '#242424',   # 深影
    'L1': '#F4F4F4',   # 内衬
    'D1': '#414141',   # 裤
    'D2': '#2E2E2E',   # 鞋
}

grid = [['B2'] * N for _ in range(N)]
part = [['none'] * N for _ in range(N)]

def fill(y0, y1, x0, x1, ch, pt):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grid[y][x] = ch
            part[y][x] = pt

def hgrad(y0, y1, x0, x1, c_mid, c_edge, pt, edge=2):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = min(x - x0, x1 - x)
            grid[y][x] = c_edge if d < edge else c_mid
            part[y][x] = pt

# ---------- 头发（发顶 + 齐刘海） ----------
fill(1, 5, 6, 21, 'H2', 'hair')
hgrad(1, 5, 6, 21, 'H2', 'H3', 'hair')
fill(1, 2, 9, 17, 'H1', 'hair')          # 顶部高光
# 侧发 + 发尾垂肩
fill(4, 10, 6, 8, 'H3', 'hair')
fill(4, 10, 20, 22, 'H3', 'hair')
fill(6, 10, 7, 8, 'H2', 'hair')
fill(6, 10, 20, 21, 'H2', 'hair')
fill(10, 12, 6, 7, 'H3', 'hair')          # 左发尾
fill(10, 12, 21, 22, 'H3', 'hair')        # 右发尾
# ---------- 头·脸 ----------
fill(6, 10, 8, 20, 'F5', 'head')
hgrad(6, 10, 8, 20, 'F5', 'F7', 'head', 1)
fill(11, 11, 8, 20, 'F6', 'head')         # 下巴（连到侧发内侧）
fill(12, 12, 11, 17, 'F7', 'head')        # 颈上
fill(13, 13, 12, 16, 'F7', 'head')        # 颈
# ---------- 五官（独立部件层：眼睛/嘴巴，动画按层驱动） ----------
for ey in (7, 8):
    fill(ey, ey, 11, 12, 'E1', 'eyes')
    fill(ey, ey, 16, 17, 'E1', 'eyes')
fill(7, 7, 11, 11, 'E2', 'eyes')          # 高光
fill(7, 7, 16, 16, 'E2', 'eyes')
fill(9, 9, 9, 10, 'P1', 'head')           # 腮红（归头·脸）
fill(9, 9, 18, 19, 'P1', 'head')
fill(10, 10, 13, 14, 'P2', 'mouth')       # 抿唇
# ---------- 外套（大衣） ----------
fill(14, 14, 4, 23, 'C2', 'coat')         # 肩
hgrad(15, 22, 7, 20, 'C2', 'C3', 'coat')
fill(19, 22, 10, 17, 'C1', 'coat')        # 胸亮部
fill(23, 24, 9, 18, 'C3', 'coat')         # 下摆
# ---------- 衣服（V 领 + 衣扣） ----------
fill(15, 15, 12, 16, 'L1', 'top')
fill(16, 16, 11, 17, 'L1', 'top')
fill(17, 17, 10, 18, 'L1', 'top')
fill(18, 18, 13, 14, 'L1', 'top')         # 领尖
fill(19, 19, 13, 14, 'L1', 'top')         # 扣1
fill(21, 21, 13, 14, 'L1', 'top')         # 扣2
# ---------- 裤子 / 鞋 ----------
fill(25, 27, 9, 12, 'D1', 'pants')
fill(25, 27, 16, 19, 'D1', 'pants')
fill(27, 27, 9, 12, 'D2', 'shoes')
fill(27, 27, 16, 19, 'D2', 'shoes')

data = {
    "name": "姐姐",
    "cols": N, "rows": N,
    "palette": PAL,
    "color": grid,
    "part": part,
}
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = os.path.join(ROOT, "03-美术资产", "OC数据", "bead_oc29_jiejie.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
print("saved", out)

from collections import Counter
cnt = Counter(p for row in part for p in row)
print(dict(cnt))
