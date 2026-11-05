# -*- coding: utf-8 -*-
"""把 youxi 目录按职责分好类，并同步修正脚本内的硬编码路径。
用法： python reorganize.py          仅预检，不动文件
       python reorganize.py --go     执行整理
"""
import io, os, re, sys, shutil

D = r"D:\codex\codex-data\youxi"
GO = "--go" in sys.argv

FOLDERS = [
    "01-需求文档",
    "02-原型",
    "03-美术资产",
    "03-美术资产/手建模",
    "03-美术资产/OC数据",
    "03-美术资产/参考图",
    "04-脚本",
    "04-脚本/手建模",
    "04-脚本/校验",
    "04-脚本/OC数据",
    "05-截图",
    "06-备份",
]

MOVES = [
    ("01-需求文档", ["纸上岛-项目需求与功能书.md", "纸上岛-产品设计书.md",
                      "功能设计-完整功能设计.md", "功能设计-拼豆图纸库与导入导出闭环.md",
                      "社区好友功能规划.md", "项目开发功能书.md"]),
    ("02-原型", ["拼豆板编辑器原型.html", "上帝之手-demo.html"]),
    ("03-美术资产/手建模", ["hand_3d_alpha.png", "hand_3d_preview.png", "hand_3d_smooth.png",
                           "hand_3d_views.png", "hand_3d_x2.png"]),
    ("03-美术资产/OC数据", ["bead_oc29_jiejie.json", "bead_oc_jiejie.png"]),
    ("03-美术资产/参考图", ["eva_bead_ref_crop.png"]),
    ("04-脚本/手建模", ["make_hand_3d.py", "make_hand_3d_views.py", "make_hand_blender.py",
                      "_blender_test.py"]),
    ("04-脚本/校验", ["check_v14.py", "check_palette.py", "verify_js_syntax.py",
                    "verify_hand_static.py"]),
    ("04-脚本/OC数据", ["bead_oc29_json.py", "bead_art.py", "embed_v04.py"]),
    ("05-截图", ["shot_static.png", "shot_longname.png", "shot_put_run.png", "_blender_test.png"]),
    ("06-备份", ["纸上岛-项目需求与功能书_v1.3备份.md"]),
]

R = 'ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'

REPL = {
    "make_hand_3d.py": [
        (r'OUT = r"D:\codex\codex-data\youxi"',
         R + '\nOUT = os.path.join(ROOT, "03-美术资产", "手建模")'),
    ],
    "make_hand_3d_views.py": [
        (r'OUT = r"D:\codex\codex-data\youxi"',
         R + '\nOUT = os.path.join(ROOT, "03-美术资产", "手建模")'),
    ],
    "make_hand_blender.py": [
        (r'D = r"D:\codex\codex-data\youxi"',
         R + '\nD = os.path.join(ROOT, "03-美术资产", "手建模")'),
    ],
    "verify_hand_static.py": [
        (r'D = r"D:\codex\codex-data\youxi"',
         R + '\nDEMO = os.path.join(ROOT, "02-原型", "上帝之手-demo.html")\n'
         'SHOT = os.path.join(ROOT, "05-截图", "shot_static.png")'),
        ('s = io.open(os.path.join(D, "上帝之手-demo.html"), encoding="utf-8").read()',
         's = io.open(DEMO, encoding="utf-8").read()'),
        (r'p = os.path.join(D, "_demo_static.html")',
         'p = os.path.join(tempfile.gettempdir(), "_demo_static.html")'),
        (r'shot = os.path.join(D, "shot_static.png")', 'shot = SHOT'),
        ('import io, os, subprocess, sys', 'import io, os, subprocess, sys, tempfile'),
    ],
    "verify_js_syntax.py": [
        (r'P = r"D:\codex\codex-data\youxi\拼豆板编辑器原型.html"',
         R + '\nP = os.path.join(ROOT, "02-原型", "拼豆板编辑器原型.html")'),
        (r'io.open(r"D:\codex\codex-data\youxi\_editor_js_check.js", "w", encoding="utf-8")',
         'io.open(os.path.join(tempfile.gettempdir(), "_editor_js_check.js"), "w", encoding="utf-8")'),
        ('import io, re', 'import io, os, re, tempfile'),
    ],
    "check_palette.py": [
        (r"t = io.open(r'D:\codex\codex-data\youxi\拼豆板编辑器原型.html', 'r', encoding='utf-8').read()",
         R + "\nt = io.open(os.path.join(ROOT, '02-原型', '拼豆板编辑器原型.html'), 'r', encoding='utf-8').read()"),
        ('import io, re', 'import io, os, re'),
    ],
    "check_v14.py": [
        (r'P = r"D:\codex\codex-data\youxi\纸上岛-项目需求与功能书.md"',
         R + '\nP = os.path.join(ROOT, "01-需求文档", "纸上岛-项目需求与功能书.md")'),
        ('import io, re', 'import io, os, re'),
    ],
    "bead_oc29_json.py": [
        (r'out = r"D:\codex\codex-data\youxi\bead_oc29_jiejie.json"',
         "import os\n" + R + '\nout = os.path.join(ROOT, "03-美术资产", "OC数据", "bead_oc29_jiejie.json")'),
    ],
    "bead_art.py": [
        (r'out = r"D:\codex\codex-data\youxi\bead_oc_jiejie.png"',
         "import os\n" + R + '\nout = os.path.join(ROOT, "03-美术资产", "OC数据", "bead_oc_jiejie.png")'),
    ],
    "embed_v04.py": [
        (r"j = json.load(open(r'D:\codex\codex-data\youxi\bead_oc29_jiejie.json', encoding='utf-8'))",
         R + "\nj = json.load(open(os.path.join(ROOT, '03-美术资产', 'OC数据', 'bead_oc29_jiejie.json'), encoding='utf-8'))"),
        (r"p = r'D:\codex\codex-data\youxi\拼豆板编辑器原型.html'",
         "p = os.path.join(ROOT, '02-原型', '拼豆板编辑器原型.html')"),
        ('import json, re', 'import json, os, re'),
    ],
    "_blender_test.py": [
        (r'OUT = r"D:\codex\codex-data\youxi\_blender_test.png"',
         R + '\nOUT = os.path.join(ROOT, "05-截图", "_blender_test.png")'),
    ],
}

# ---------- 1. 预检 ----------
errs = []
for folder, files in MOVES:
    for f in files:
        if not os.path.exists(os.path.join(D, f)):
            errs.append("MISSING SRC: " + f)
            continue
        if f not in REPL:
            continue
        s = io.open(os.path.join(D, f), encoding="utf-8").read()
        for old, new in REPL[f]:
            n = s.count(old)
            if n != 1:
                errs.append("ANCHOR %d time(s) in %s: %s" % (n, f, old[:60]))
            s = s.replace(old, new, 1)
        if f.endswith(".py") and not re.search(r"(?m)^(import|from)\s+.*\bos\b", s):
            errs.append("WILL LACK import os: " + f)

if errs:
    print("PREFLIGHT FAILED")
    for e in errs:
        print("  ", e)
    sys.exit(1)
print("预检通过：%d 个文件待归位，%d 个脚本待改路径" % (
    sum(len(v) for _, v in MOVES), len(REPL)))

if not GO:
    print("（未执行，加 --go 落盘）")
    sys.exit(0)

# ---------- 2. 建目录并移动 ----------
for folder in FOLDERS:
    os.makedirs(os.path.join(D, folder), exist_ok=True)
for folder, files in MOVES:
    for f in files:
        shutil.move(os.path.join(D, f), os.path.join(D, folder, f))

# ---------- 3. 改脚本路径 ----------
where = {}
for folder, files in MOVES:
    for f in files:
        where[f] = folder
for f, pairs in REPL.items():
    p = os.path.join(D, where[f], f)
    s = io.open(p, encoding="utf-8").read()
    for old, new in pairs:
        s = s.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ---------- 4. 清掉空缓存目录 ----------
cache = os.path.join(D, ".screenshots")
if os.path.isdir(cache) and not [x for x in os.listdir(cache) if os.listdir(os.path.join(cache, x))]:
    shutil.rmtree(cache, ignore_errors=True)

print("完成")
for folder in FOLDERS:
    n = len([x for x in os.listdir(os.path.join(D, folder)) if os.path.isfile(os.path.join(D, folder, x))])
    if n:
        print("  %-24s %d" % (folder, n))
root_files = [x for x in os.listdir(D) if os.path.isfile(os.path.join(D, x))]
print("根目录残留文件：", root_files if root_files else "无")
