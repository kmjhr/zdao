# -*- coding: utf-8 -*-
"""静态定格验证：手停在屏中、卡已落定，检查手图加载与卡布局"""
import io, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEMO = os.path.join(ROOT, "02-原型", "上帝之手-demo.html")
SHOT = os.path.join(ROOT, "05-截图", "shot_static.png")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
s = io.open(DEMO, encoding="utf-8").read()
if "</html>" not in s:
    sys.exit("HTML INCOMPLETE")

s = s.replace("transform:translateY(-240px) rotate(180deg)", "transform:translateY(-64px) rotate(180deg)")
if "translateY(-64px) rotate(180deg)" not in s:
    sys.exit("STATIC PATCH MISSED")
s = s.replace("box-shadow:0 8px 0 rgba(0,0,0,.4);transform:translateY(-120px)",
              "box-shadow:0 8px 0 rgba(0,0,0,.4);transform:translateY(0px);opacity:1")
s = s.replace("<div class=\"log\" id=\"log\"></div>", "<div class=\"log\" id=\"log\">静态定格检查</div>")

p = os.path.join(tempfile.gettempdir(), "_demo_static.html")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
shot = SHOT
cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--window-size=980,900",
       "--virtual-time-budget=1500", "--screenshot=%s" % shot,
       "file:///" + p.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, text=True)
print("rc", r.returncode, "exists", os.path.exists(shot))
