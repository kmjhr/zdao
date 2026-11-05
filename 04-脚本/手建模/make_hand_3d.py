# -*- coding: utf-8 -*-
"""
3D 手 -> 三渲二 -> 像素化 56x72
纯 numpy 软件渲染，不依赖任何 3D 库：
  1. SDF 建模（圆角盒手掌 + 鱼际椭球 + 11 段胶囊手指/手腕，smin 平滑并集）
  2. 正交射线求交（-z 步进 1.1，再用 9 次二分夹逼细化）
  3. SDF 梯度求法线
  4. 三渲二：n·L 硬切三档；法线几乎平行视线(<0.22)处判黑 = 描边
  5. 4x 超采样后取众数降采样（不是取平均，取平均会把 1 格宽的指缝糊掉）
     黑色占比 >=22% 的格子直接判黑，保证描边闭合

改姿态：把某根手指的终点 y 压到 8 以下、z 推到 -8，它就会蜷进掌心，
        正面只剩竖起的指头（见 FINGERS 表，每根手指两段：近节粗 / 远节细）。
改尺寸：改 CW/CH（当前 56x72）。地图内只露指尖时用 32x32，卡面用 56x72。
改配色：C_SHADE / C_MID / C_LIGHT / C_INK，阈值 lam>0.52 亮、lam<0.34 暗。
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "03-美术资产", "手建模")
CW, CH = 56, 72
SS = 4                       # 超采样倍数
RW, RH = CW * SS, CH * SS

HX = 28.0                    # 画布半宽（单位=格）
HY = 36.0

# ---- SDF 基元 ----
def sd_capsule(p, a, b, r):
    a = np.array(a, float); b = np.array(b, float)
    pa = p - a
    ba = b - a
    h = np.clip((pa @ ba) / (ba @ ba), 0.0, 1.0)
    return np.linalg.norm(pa - np.outer(h, ba), axis=1) - r


def sd_rbox(p, c, h, r):
    q = np.abs(p - np.array(c, float)) - (np.array(h, float) - r)
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=1)
    inside = np.minimum(np.max(q, axis=1), 0.0)
    return outside + inside - r


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


# ---- 手的几何：手掌加大 / 拇指下沉 / 手指紧凑 ----
PALM_C = (1.0, -9.5, 0.0)
PALM_H = (14.5, 12.5, 5.8)
PALM_R = 6.0
SLOT_X = [7.0, -0.75, -8.5]
THENAR_C = (-7.0, -13.0, -0.5)
THENAR_R = (6.5, 5.0, 5.0)

FINGERS = [
    ((-10.4, -2.5, 0.0), (-10.4, 22.0, 0.0), 3.1),
    ((-2.9, -2.5, 0.0),  (-2.9, 27.0, 0.0),  3.2),
    ((4.6, -2.2, 0.0),   (4.6, 23.5, 0.0),   3.1),
    ((11.8, -1.6, 0.0),  (11.8, 17.5, 0.0),  2.9),
    ((-12.0, -9.0, 0.5), (-17.5, -5.0, 1.0), 3.3),
    ((-17.5, -5.0, 1.0), (-23.0, 0.0, 1.0),  2.9),
    ((0.5, -22.0, 0.0),  (0.5, -36.0, 0.0),  8.0),
]
SLOT_X = [8.2, 0.85, -6.65]
SLOT_X = [7.0, -0.45, -7.7]
SLOT_X = [7.0, -0.25, -7.5]


def sd_ellipsoid(p, c, r):
    q = (p - np.array(c, float)) / np.array(r, float)
    k0 = np.linalg.norm(q, axis=1)
    k1 = np.linalg.norm(q / np.array(r, float), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def sdf(p):
    d = sd_rbox(p, PALM_C, PALM_H, PALM_R)
    d = smin(d, sd_ellipsoid(p, THENAR_C, THENAR_R), 2.5)
    for a, b, r in FINGERS:
        d = smin(d, sd_capsule(p, a, b, r), 1.0)
    for sx in SLOT_X:
        d = smax(d, -sd_rbox(p, (sx, 1.6, 0.0), (0.50, 2.9, 7.0), 0.45), 0.9)
    return d


# ---- 正交 ray march ----
xs = (np.arange(RW) + 0.5) / RW * (2 * HX) - HX
ys = HY - (np.arange(RH) + 0.5) / RH * (2 * HY)
X, Y = np.meshgrid(xs, ys)
Xf, Yf = X.ravel(), Y.ravel()

ZS = np.arange(40.0, -46.0, -1.1)
hit_z = np.full(Xf.size, np.nan)
for z in ZS:
    if np.all(~np.isnan(hit_z)):
        break
    pending = np.isnan(hit_z)
    p = np.stack([Xf[pending], Yf[pending], np.full(pending.sum(), z)], axis=1)
    d = sdf(p)
    idx = np.where(pending)[0]
    hit_z[idx[d < 0]] = z

# 二分细化：z_out 在外(sdf>=0)，z_in 在内(sdf<0)，收敛到真实表面
mask = ~np.isnan(hit_z)
z_in = np.where(mask, hit_z, 0.0)
z_out = z_in + 1.1
for _ in range(9):
    if not mask.any():
        break
    zm = 0.5 * (z_in + z_out)
    p = np.stack([Xf[mask], Yf[mask], zm[mask]], axis=1)
    d = sdf(p)
    inner = d < 0
    idx = np.where(mask)[0]
    zi, zo = idx[inner], idx[~inner]
    z_in[zi] = zm[zi]
    z_out[zo] = zm[zo]
Z = np.where(mask, z_in, 0.0)

# ---- 法线（SDF 梯度） ----
eps = 0.6
px_all = np.stack([Xf, Yf, Z], axis=1)
nx = sdf(px_all + [eps, 0, 0]) - sdf(px_all - [eps, 0, 0])
ny = sdf(px_all + [0, eps, 0]) - sdf(px_all - [0, eps, 0])
nz = sdf(px_all + [0, 0, eps]) - sdf(px_all - [0, 0, eps])
N = np.stack([nx, ny, nz], axis=1)
nl = np.linalg.norm(N, axis=1)
nl[nl < 1e-6] = 1.0
N = N / nl[:, None]

# ---- 三渲二：硬色阶 ----
L = np.array([0.62, 0.42, 0.40]); L = L / np.linalg.norm(L)
lam = np.clip((N @ L), 0.0, 1.0)

C_SHADE = np.array([212, 178, 140], float)
C_MID   = np.array([234, 203, 164], float)
C_LIGHT = np.array([246, 218, 182], float)
C_INK   = np.array([26, 26, 26], float)

col = np.empty((Xf.size, 3), float)
col[:] = C_MID
col[lam > 0.52] = C_LIGHT
col[lam < 0.34] = C_SHADE

# 掠射描边：法线几乎平行视线 → 轮廓黑线
rim = (N[:, 2] < 0.22) & mask
col[rim] = C_INK

# 只在外侧补 1 格，保证闭合，不做二次加粗（rim 已经有一格）
grid = np.zeros((RH, RW), bool)
grid.ravel()[:] = mask
def dilate(g):
    out = g.copy()
    out[1:, :] |= g[:-1, :]
    out[:-1, :] |= g[1:, :]
    out[:, 1:] |= g[:, :-1]
    out[:, :-1] |= g[:, 1:]
    out[1:, 1:] |= g[:-1, :-1]
    out[1:, :-1] |= g[:-1, 1:]
    out[:-1, 1:] |= g[1:, :-1]
    out[:-1, :-1] |= g[1:, 1:]
    return out


grid_c = dilate(grid)
edge = grid_c & ~grid
col[edge.ravel()] = C_INK
mask_all = grid_c.ravel()

# ---- 降采样：取众数，保持纯色 ----
def mode_down(cols_flat, valid_flat, w, h, s):
    q = np.zeros((h, w, 3), np.uint8)
    valid = valid_flat.reshape(h, s, w, s)
    rgb = cols_flat.reshape(h, s, w, s, 3)
    for j in range(h):
        for i in range(w):
            vv = valid[j, :, i, :].ravel()
            if not vv.any():
                continue
            cand = rgb[j, :, i, :].reshape(-1, 3)[vv]
            ink = ((cand[:, 0] < 60) & (cand[:, 1] < 60) & (cand[:, 2] < 60)).sum()
            if ink >= len(cand) * 0.22:
                q[j, i] = [26, 26, 26]
                continue
            # 众数（按颜色打包比较）
            packed = (cand[:, 0].astype(np.int32) << 16) | (cand[:, 1].astype(np.int32) << 8) | cand[:, 2].astype(np.int32)
            vals, cnt = np.unique(packed, return_counts=True)
            best = vals[np.argmax(cnt)]
            q[j, i] = [(best >> 16) & 255, (best >> 8) & 255, best & 255]
    return q


img = mode_down(col, mask_all, CW, CH, SS)

# 补洞：被不透明包围的透明格填黑，防止指缝里漏出白点
filled = img.sum(axis=2) > 0
outside = np.zeros((CH, CW), bool)
stack = []
for i in range(CW):
    for jj in (0, CH - 1):
        if not filled[jj, i] and not outside[jj, i]:
            outside[jj, i] = True
            stack.append((jj, i))
for jj in range(CH):
    for i in (0, CW - 1):
        if not filled[jj, i] and not outside[jj, i]:
            outside[jj, i] = True
            stack.append((jj, i))
while stack:
    jj, ii = stack.pop()
    for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nj, ni = jj + dj, ii + di
        if 0 <= nj < CH and 0 <= ni < CW and not filled[nj, ni] and not outside[nj, ni]:
            outside[nj, ni] = True
            stack.append((nj, ni))
hole = (~filled) & (~outside)
img[hole] = [26, 26, 26]

for j in range(CH):
    line = ""
    for i in range(CW):
        c = img[j, i]
        if c.sum() == 0:
            line += " "
        elif abs(int(c[0]) - 26) < 8 and abs(int(c[1]) - 26) < 8:
            line += "#"
        elif c[0] > 232:
            line += "O"
        elif c[0] > 212:
            line += "."
        else:
            line += "+"
    print("%02d %s" % (j, line))

rgba = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
rp = rgba.load()
for j in range(CH):
    for i in range(CW):
        c = img[j, i]
        if c.sum() == 0:
            continue
        rp[i, j] = (int(c[0]), int(c[1]), int(c[2]), 255)
rgba.save(os.path.join(OUT, "hand_3d_alpha.png"))

S = 9
prev = Image.new("RGB", (CW * S, CH * S), (247, 247, 245))
pp = prev.load()
for y in range(CH * S):
    for x in range(CW * S):
        pp[x, y] = (255, 255, 255) if ((x // S) + (y // S)) % 2 == 0 else (236, 236, 232)
for j in range(CH):
    for i in range(CW):
        c = rp[i, j]
        if c[3] == 0:
            continue
        for y in range(j * S, j * S + S):
            for x in range(i * S, i * S + S):
                pp[x, y] = c[:3]
prev.save(os.path.join(OUT, "hand_3d_preview.png"))
rgba.resize((CW * 2, CH * 2), Image.NEAREST).save(os.path.join(OUT, "hand_3d_x2.png"))

# 连续色调版本（证明这是 3D 曲面而不是手绘平面）
smooth = np.tile(np.array([58, 54, 50], float), (Xf.size, 1))
t = 0.22 + 0.78 * lam
diff = np.array([234, 203, 164], float)[None, :] * t[:, None]
smooth[mask] = diff[mask]
smooth[rim] = np.array([42, 38, 36], float)
Image.fromarray(smooth.reshape(RH, RW, 3).astype(np.uint8)).save(
    os.path.join(OUT, "hand_3d_smooth.png"))
print("saved")
