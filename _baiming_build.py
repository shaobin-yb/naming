# -*- coding: utf-8 -*-
"""百名帖 → baiming.html(铁蛋给二宝的 100 个名字)"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

bm = json.load(open(f"{BASE}/_baiming.json", encoding="utf-8"))

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

idx = 0
sections = ""
for g in bm["groups"]:
    cards = ""
    for it in g["items"]:
        idx += 1
        cards += f'''<div class="ccard">
  <div class="ctop"><span class="num">{idx:03d}</span><span class="cnm">{esc(it["name"])}</span></div>
  <p class="cnote">{esc(it["note"])}</p>
</div>
'''
    sections += f'<h3 class="gtitle">{esc(g["g"])}</h3>\n<div class="ccards">{cards}</div>\n'

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>百名帖 · 铁蛋给二宝的一百个名字</title>
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
h3.gtitle{font-size:17px;letter-spacing:.1em;margin:28px 0 8px;padding-left:10px;
  border-left:4px solid var(--gold);font-family:"Songti SC","STSong","SimSun",serif}
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
  <h1>百名帖<span class="seal">王</span></h1>
  <p class="sub">铁蛋给二宝的<b>一百个名字</b> · 出生前逐个备好 · 出生后以真八字收网 &nbsp;|&nbsp; <a href="overview.html">总览</a> · <a href="directions.html">起名方向</a> · <a href="review-top100.html">前100卡片</a> · <a href="qingling.html">轻灵30</a></p>
</header>

<p class="intro">二宝还没动静，名字先替他张罗着——老板说这 100 个由叔叔来起，那我就把压箱底的都掏出来。<br>
池子里已有的 756 个名字全部避开（连最舍不得的「月白」「清扬」都因为被人占了或联想里有别人，忍痛划掉）；每一条出处对了原文，网红字、高歧义多音、方言雷区都过了筛子。<br>
<b>不敢说个个都好，但每一个都是把最好的眼力给了二宝。</b>等小家伙报到那天，拿真八字再收一遍网——这里总有几颗能留下。</p>

__SECTIONS__

<footer>
  <b>口径</b>：本页 100 个为叔叔命名草案，未走五格评分；全部对 756 名占用集合查重通过；「朴」为已知多音字（家中读音自定）。<br>
  <b>红线</b>：所有名字均为候选；大名小名均未定，拟议名不得升格；出生后结合真八字收网。<br>
  <b>生成</b>：2026-10-16 · 铁蛋 · naming/_baiming_build.py
</footer>
</div>
</body>
</html>
"""

html = HTML.replace("__SECTIONS__", sections)
out = f"{BASE}/baiming.html"
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out, len(html), "字符")
