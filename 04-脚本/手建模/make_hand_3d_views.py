# -*- coding: utf-8 -*-
"""多视角渲染 3D 手（证明是立体模型），输出 2x2 拼图"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "03-美术资产", "手建模")
RW, RH = 224, 288
HX, HY = 28.0, 36.0
SS = 1

PALM_C = (1.0, -9.5, 0.0)
PALM_H = (14.5, 12.5, 5.8)
PALM_R = 6.0
THENAR_C = (-7.0, -13.0, -0.5)
THENAR_R = (6.5, 5.0, 5.0)

# 每根手指拆两段：近节粗、远节略细 → 出现指节
# 手指起点统一在手掌顶边内，指间距压紧但至少留 1.4 格缝
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
SLOT_X = [7.0, -0.75, -8.5]


def sd_rbox(p, c, h, r):
    q = np.abs(p - np.array(c, float)) - (np.array(h, float) - r)
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=1)
    inside = np.minimum(np.max(q, axis=1), 0.0)
    return outside + inside - r


def sd_capsule(p, a, b, r):
    pa = p - np.array(a, float)
    ba = np.array(b, float) - np.array(a, float)
    h = np.clip((pa @ ba) / (ba @ ba), 0.0, 1.0)
    return np.linalg.norm(pa - np.outer(h, ba), axis=1) - r


def sd_ellipsoid(p, c, r):
    q = (p - np.array(c, float)) / np.array(r, float)
    k0 = np.linalg.norm(q, axis=1)
    k1 = np.linalg.norm(q / np.array(r, float), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def sdf_model(p):
    d = sd_rbox(p, PALM_C, PALM_H, PALM_R)
    d = smin(d, sd_ellipsoid(p, THENAR_C, THENAR_R), 2.5)
    for a, b, r in FINGERS:
        d = smin(d, sd_capsule(p, a, b, r), 1.0)
    for sx in SLOT_X:
        d = smax(d, -sd_rbox(p, (sx, 1.6, 0.0), (0.50, 2.9, 7.0), 0.45), 0.9)
    return d


def rot_y(deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def render(deg):
    xs = (np.arange(RW) + 0.5) / RW * (2 * HX) - HX
    ys = HY - (np.arange(RH) + 0.5) / RH * (2 * HY)
    X, Y = np.meshgrid(xs, ys)
    Xf, Yf = X.ravel(), Y.ravel()
    R = rot_y(deg)

    hit = np.full(Xf.size, np.nan)
    for z in np.arange(40.0, -46.0, -1.1):
        if np.all(~np.isnan(hit)):
            break
        pend = np.isnan(hit)
        if not pend.any():
            break
        pw = np.stack([Xf[pend], Yf[pend], np.full(pend.sum(), z)], axis=1)
        d = sdf_model(pw @ R)
        idx = np.where(pend)[0]
        hit[idx[d < 0]] = z

    mask = ~np.isnan(hit)
    z_in = np.where(mask, hit, 0.0)
    z_out = z_in + 1.1
    for _ in range(9):
        if not mask.any():
            break
        zm = 0.5 * (z_in + z_out)
        pw = np.stack([Xf[mask], Yf[mask], zm[mask]], axis=1)
        d = sdf_model(pw @ R)
        idx = np.where(mask)[0]
        zi, zo = idx[d < 0], idx[d >= 0]
        z_in[zi] = zm[zi]
        z_out[zo] = zm[zo]
    Z = np.where(mask, z_in, 0.0)

    eps = 0.6
    base = np.stack([Xf, Yf, Z], axis=1) @ R
    gx = sdf_model(base + [eps, 0, 0]) - sdf_model(base - [eps, 0, 0])
    gy = sdf_model(base + [0, eps, 0]) - sdf_model(base - [0, eps, 0])
    gz = sdf_model(base + [0, 0, eps]) - sdf_model(base - [0, 0, eps])
    n = np.stack([gx, gy, gz], axis=1)
    nl = np.linalg.norm(n, axis=1); nl[nl < 1e-6] = 1
    n = n / nl[:, None]
    nw = n @ R.T

    L = np.array([0.55, 0.45, 0.42]); L = L / np.linalg.norm(L)
    lam = np.clip(nw @ L, 0, 1)

    img = np.tile(np.array([58, 54, 50], float), (Xf.size, 1))
    t = 0.18 + 0.85 * lam
    diff = np.array([234, 203, 164], float)[None, :] * t[:, None]
    img[mask] = diff[mask]
    rim = (nw[:, 2] < 0.18) & mask
    img[rim] = np.array([38, 34, 32], float)

    return img.reshape(RH, RW, 3).astype(np.uint8), mask.reshape(RH, RW)


VIEWS = [(0, "正面 0°"), (-30, "左转 30°"), (-60, "左转 60°"), (30, "右转 30°")]
tiles = []
for deg, _ in VIEWS:
    im, _m = render(deg)
    tiles.append(im)

PAD, LBL = 10, 26
W = RW * 2 + PAD * 3
H = (RH + LBL) * 2 + PAD * 3
sheet = Image.new("RGB", (W, H), (32, 30, 28))
dr = ImageDraw.Draw(sheet)
font = None
for fp in ("C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc"):
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 20)
            break
        except Exception:
            pass

for i, (deg, label) in enumerate(VIEWS):
    cx = PAD + (i % 2) * (RW + PAD)
    cy = PAD + (i // 2) * (RH + LBL + PAD)
    sheet.paste(Image.fromarray(tiles[i]), (cx, cy))
    txt = label
    if font:
        dr.text((cx + 6, cy + RH + 2), txt, fill=(200, 196, 188), font=font)

sheet = sheet.resize((W * 2, H * 2), Image.NEAREST)
sheet.save(os.path.join(OUT, "hand_3d_views.png"))
print("saved", sheet.size)
