# -*- coding: utf-8 -*-
"""轻灵少年气 30 候选独立页 qingling.html"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

cands = json.load(open(f"{BASE}/_review2_cands30.json", encoding="utf-8"))["items"]

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

cand_html = ""
for i, c in enumerate(cands, 1):
    cand_html += f'''<div class="ccard">
  <div class="ctop"><span class="num">{i:02d}</span><span class="cnm">{esc(c["name"])}</span>
  <span class="cqx">{esc(c.get("qx",""))}</span></div>
  <p class="cnote">{esc(c.get("note",""))}</p>
  <p class="cquote">{esc(c.get("quote",""))}</p>
</div>
'''

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>轻灵少年气 · 王姓男孩 30 候选</title>
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
  border-left:3px solid var(--gold);border-radius:10px;padding:12px 16px;margin:18px 0;
  line-height:1.9}
.ccards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px;margin-top:8px}
.ccard{background:var(--surf);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.ctop{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}
.num{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.cnm{font-size:23px;font-weight:700;letter-spacing:.08em;
  font-family:"Songti SC","STSong","SimSun",serif}
.cqx{margin-left:auto;font-size:12px;color:var(--blue);background:#e8eef5;border-radius:6px;padding:1px 8px;white-space:nowrap}
.cnote{font-size:13.5px;margin:0 0 6px}
.cquote{font-size:12.5px;color:var(--ink2);margin:0;padding-left:10px;border-left:2px solid var(--line)}
footer{margin-top:46px;padding-top:18px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--muted);line-height:1.9}
footer b{color:var(--ink2)}
@media (max-width:560px){ .ccards{grid-template-columns:1fr} }
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>轻灵少年气<span class="seal">王</span></h1>
  <p class="sub">王姓男孩 · 30 个备选参考 · <b>补池子缺位方向</b>：明快、清亮、有少年感 · 全部已查重（726 名占用集合无重复）· <a href="overview.html">总览</a> · <a href="skill-review.html">重估榜</a></p>
</header>

<p class="intro">方向说明：现有池子整体偏“老成持重”（五劫/中药/道家/传承系厚重），<b>轻灵少年气方向偏薄</b>。本页 30 个候选按 chinese-baby-naming / chinese-naming 两个起名 Skill 的方法论生成——五宜十忌（好听/好讲/好写/好运/好相）、气质光谱补位、反网红字、平仄音律，逐条给出处与一句肌理。<b>均为草案，未走五格评分，供找方向用</b>；喜欢哪个方向，可以再拉进池子正式评分。</p>

<div class="ccards">
__CANDS__
</div>

<footer>
  <b>口径</b>：候选由 Skill 方法论生成；含 10-13 首批 6 个（清越/朗川/弈舟/砚秋/鹿鸣/澄川）＋ 10-14 新增 24 个。多音提示已标（如“和 hé”“兴 xìng”）。<br>
  <b>红线</b>：所有名字均为候选；大名小名均未定，出生后结合真八字收网。<br>
  <b>生成</b>：2026-10-14 · 铁蛋 · 本页由 naming/_review2_build_qingling.py 自动生成
</footer>
</div>
</body>
</html>
"""

html = HTML.replace("__CANDS__", cand_html)
out = f"{BASE}/qingling.html"
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out, len(html), "字符")
