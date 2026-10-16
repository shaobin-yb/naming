# -*- coding: utf-8 -*-
"""刚骨三十 → yanggang.html"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

yg = json.load(open(f"{BASE}/_yanggang.json", encoding="utf-8"))

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

cards = ""
for i, it in enumerate(yg["items"], 1):
    cards += f'''<div class="ccard">
  <div class="ctop"><span class="num">{i:02d}</span><span class="cnm">{esc(it["name"])}</span></div>
  <p class="cnote">{esc(it["note"])}</p>
</div>
'''

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>刚骨三十 · 阳刚向 · 王姓男孩</title>
<style>
:root{
  --surf:#fcfcfb; --page:#f9f9f7; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
  --line:#e1e0d9; --jiang:#C23B2E; --gold:#C79A2B;
  --tai:#2d8f5f; --warn:#c07a1a; --blue:#2d5f8f;
}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;line-height:1.6}
.wrap{max-width:1120px;margin:0 auto;padding:28px 20px 80px}
header{padding:30px 4px 22px;border-bottom:1px solid var(--line);margin-bottom:14px}
h1{margin:0 0 8px;font-size:clamp(26px,4.6vw,40px);letter-spacing:.14em;
  font-family:"Songti SC","STSong","SimSun",serif;font-weight:700}
h1 .seal{display:inline-block;background:var(--jiang);color:#fff;font-size:.5em;
  padding:.28em .5em;border-radius:4px;vertical-align:.62em;letter-spacing:.1em;
  margin-left:14px;font-family:inherit}
.sub{color:var(--ink2);font-size:14.5px;margin:2px 0 0}
.sub b{color:var(--jiang)}
.sub a{color:var(--blue);text-decoration:none;border-bottom:1px solid var(--blue)}
.intro{font-size:13.5px;color:var(--ink2);background:var(--surf);border:1px solid var(--line);
  border-left:3px solid var(--jiang);border-radius:10px;padding:14px 18px;margin:18px 0;
  line-height:2}
.intro b{color:var(--ink)}
.ccards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:10px}
.ccard{background:var(--surf);border:1px solid var(--line);border-radius:11px;padding:11px 15px}
.ctop{display:flex;align-items:baseline;gap:10px;margin-bottom:2px}
.num{font-size:11.5px;color:var(--jiang);font-weight:700;font-variant-numeric:tabular-nums}
.cnm{font-size:21px;font-weight:700;letter-spacing:.08em;
  font-family:"Songti SC","STSong","SimSun",serif}
.cnote{font-size:12.5px;color:var(--ink2);margin:0}
footer{margin-top:46px;padding-top:18px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--muted);line-height:1.9}
footer b{color:var(--ink2)}
@media (max-width:560px){ .ccards{grid-template-columns:1fr} }
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>刚骨三十<span class="seal">王</span></h1>
  <p class="sub">阳刚向 30 名 · 与百名帖配对（一帖文脉，一帖骨相）· 已查重 · 出生后以真八字收网 &nbsp;|&nbsp; <a href="overview.html">总览</a> · <a href="baiming.html">百名帖</a> · <a href="directions.html">起名方向</a> · <a href="review-top100.html">前100卡片</a></p>
</header>

<p class="intro">百名帖给二宝备的是「文」，这三十个补的是「骨」——<b>出将入相的风骨、山河金石的重量、少年腾空的姿势</b>。<br>
壮的取诗经，刚的取尚书周易，远的取班超与楚辞；一样对过原文、过过查重和方言筛子，一样等出生后的真八字。</p>

<div class="ccards">
__CARDS__
</div>

<footer>
  <b>口径</b>：本页 30 个为叔叔命名草案（阳刚向），未走五格评分；全部对 856 名占用集合查重通过；「长」为已知多音字（名中读 cháng）。<br>
  <b>红线</b>：所有名字均为候选；大名小名均未定，拟议名不得升格；出生后结合真八字收网。<br>
  <b>生成</b>：2026-10-16 · 铁蛋 · naming/_yanggang_build.py
</footer>
</div>
</body>
</html>
"""

html = HTML.replace("__CARDS__", cards)
out = f"{BASE}/yanggang.html"
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out, len(html), "字符")
