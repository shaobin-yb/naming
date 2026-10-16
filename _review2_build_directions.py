# -*- coding: utf-8 -*-
"""「起名方向」页:三 Skill 方法论视角的方向梳理 → directions.html"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

final = {r["name"]: r for r in json.load(open(f"{BASE}/_review2_final.json", encoding="utf-8"))["rows"]}

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def chips(names):
    h = ""
    for n in names:
        r = final.get(n)
        if r:
            h += f'<span class="chip">{esc(n)}<i>#{r["rank2"]} · {r["total"]}</i></span>'
        else:
            h += f'<span class="chip">{esc(n)}<i>候选页</i></span>'
    return h

DIRS = [
    {
        "name": "道家风骨", "tag": "简拙 · 自洽",
        "desc": "以《道德经》《抱朴子》《庄子》为源：朴、真、虚、玄、一——字面极简，气质一以贯之。",
        "why": "对应 Skill 审美框架中的“书卷自持 + 雅致内敛”；简拙字面耐看 60 年、零网红风险，且与家中已形成的“朴/元/一”用字倾向共振。",
        "reps": ["王抱朴", "王虚白", "王太一", "王若朴", "王善渊", "王谷安"],
        "warn": "道家词偏冷偏淡——“仙气”与“距离感”一线之隔，需自己念几遍感受亲和度。",
    },
    {
        "name": "经典书卷", "tag": "出处可考 · 学养",
        "desc": "诗经 / 楚辞 / 论语 / 周易 / 尚书 / 礼记 / 左传 / 古文观止——每名一句原文可考。",
        "why": "池子最大的一层（328 名），也是家庭主审美位；Skill 五宜中的“好讲”（有故事可讲）在此方向天然满分。",
        "reps": ["王既明", "王弘毅", "王致知", "王养正", "王惟一", "王耿介"],
        "warn": "面太宽容易挑花眼——建议加一道“意象画面”二次筛（念出来脑子里有没有画）。",
    },
    {
        "name": "家族承启", "tag": "结构 · 对仗斯卯",
        "desc": "以“斯系 / 午系 / 元系”结构字呼应老大王斯卯（卯时破晓·地支嵌字手法）。",
        "why": "Skill“家族传承”维度的自家玩法：兄弟成对而不撞；生肖（丙午马）与干支藏字，是只有这个家才讲得通的名字。",
        "reps": ["王斯午", "王午斯", "王午汉", "王元正", "王川元", "王驰元"],
        "warn": "结构先行容易“义胜于名”——结构名也要过“念着好不好听”这关（这正是 Skill 音律尺的作用）。",
    },
    {
        "name": "草木自然", "tag": "清新 · 生机",
        "desc": "本草 / 植物系：乔木、赤芝、辛夷、修竹、甘棠……清新生机的自然底色。",
        "why": "对应“温润清朗 + 自然灵动”；字面大都好写好记，与池中厚重的道系形成呼吸感互补。",
        "reps": ["王乔木", "王赤芝", "王辛夷", "王修竹", "王甘棠", "王杜若"],
        "warn": "“药感”有阈值——纯药名（如紫苏在四维中退到 #345）要考虑日常联想，草木意象名更稳。",
    },
    {
        "name": "清幽气象", "tag": "画面 · 留白",
        "desc": "山水风月一路：望舒（月神）、浸阳（浪浸斜阳）、鹤如、枕风、闻雨、春涧——名字自带画面。",
        "why": "大师批的主阵地，也是四维重估的头部（望舒/浸阳总分前二）；“含蓄留白”在 Skill 气质光谱中是高级感来源。",
        "reps": ["王望舒", "王浸阳", "王鹤如", "王枕风", "王闻雨", "王春涧"],
        "warn": "整体偏静偏老成——若想要少年感，需要与“轻灵”方向配比着看。",
    },
    {
        "name": "轻灵少年", "tag": "明快 · 补缺位",
        "desc": "本轮新开的方向：明快、清亮、有少年感——既白、晴川、轻舟、振鹭、鹿鸣、南风……",
        "why": "四维重估发现池子“老成持重、轻灵偏薄”，这 30 个正是按 Skill 方法论（反网红 + 气质补位 + 平仄）补出来的缺位方向。",
        "reps": ["王既白", "王晴川", "王轻舟", "王振鹭", "王鹿鸣", "王南风"],
        "warn": "均为草案未评分——看中哪个方向，拉进池子走正式评分流程。",
    },
]

cards = ""
for d in DIRS:
    cards += f'''<div class="dcard">
  <div class="dtop"><span class="dname">{d["name"]}</span><span class="dtag">{d["tag"]}</span></div>
  <p class="ddesc">{d["desc"]}</p>
  <p class="dwhy">{d["why"]}</p>
  <div class="dchips">{chips(d["reps"])}</div>
  <p class="dwarn">注意：{d["warn"]}</p>
</div>
'''

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>起名方向 · Skill 方法论视角</title>
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
h2{font-size:19px;letter-spacing:.08em;margin:34px 0 10px;
  font-family:"Songti SC","STSong","SimSun",serif}
.intro{font-size:13.5px;color:var(--ink2);background:var(--surf);border:1px solid var(--line);
  border-left:3px solid var(--gold);border-radius:10px;padding:12px 16px;margin:18px 0;
  line-height:1.9}
.rulers{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.rcard{background:var(--surf);border:1px solid var(--line);border-radius:12px;padding:12px 15px;font-size:13px;color:var(--ink2)}
.rcard h3{margin:0 0 5px;font-size:14px;color:var(--ink)}
.rcard b{color:var(--ink)}
.dcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px;margin-top:8px}
.dcard{background:var(--surf);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.dtop{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}
.dname{font-size:21px;font-weight:700;letter-spacing:.08em;
  font-family:"Songti SC","STSong","SimSun",serif}
.dtag{margin-left:auto;font-size:12px;color:var(--blue);background:#e8eef5;border-radius:6px;padding:1px 8px;white-space:nowrap}
.ddesc{font-size:13.5px;margin:0 0 6px}
.dwhy{font-size:12.5px;color:var(--ink2);margin:0 0 8px}
.dchips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
.chip{display:inline-flex;align-items:baseline;gap:4px;background:var(--page);border:1px solid var(--line);
  border-radius:8px;padding:3px 9px;font-size:13.5px;font-weight:600;
  font-family:"Songti SC","STSong","SimSun",serif}
.chip i{font-style:normal;font-size:10.5px;color:var(--muted);font-weight:400;font-family:system-ui}
.dwarn{font-size:12px;color:var(--warn);margin:0}
.steps{counter-reset:st;margin-top:8px}
.step{position:relative;background:var(--surf);border:1px solid var(--line);border-radius:12px;
  padding:12px 16px 12px 52px;margin-bottom:8px;font-size:13.5px;color:var(--ink2)}
.step::before{counter-increment:st;content:counter(st);position:absolute;left:14px;top:12px;
  width:24px;height:24px;border-radius:50%;background:var(--jiang);color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700}
.step b{color:var(--ink)}
footer{margin-top:46px;padding-top:18px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--muted);line-height:1.9}
footer b{color:var(--ink2)}
@media (max-width:560px){ .dcards{grid-template-columns:1fr} }
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>起名方向<span class="seal">王</span></h1>
  <p class="sub">用三个新装起名 Skill 的方法论（chinese-baby-naming / chinese-naming / liki 字库），把 627 名池子梳理成<b>四个尺子、六个方向、一条收网路线</b> &nbsp;|&nbsp; <a href="overview.html">总览</a> · <a href="review-top100.html">前100卡片</a> · <a href="skill-review.html">627重估</a> · <a href="qingling.html">轻灵30</a></p>
</header>

<p class="intro">这不是又一批名字，而是一张“怎么选”的地图。前面做的所有东西（十二典 627、重估榜、轻灵 30、方言扫描）都是弹药；本页把它们装进一个决策框架里——<b>先定尺子，再看方向，最后按路线收网</b>。</p>

<h2>四把尺子（Skill 方法论）</h2>
<div class="rulers">
  <div class="rcard"><h3>① 八字用神尺</h3>出生后拿精确时间排盘（扶抑+调候双口径核对）→ 定用神喜忌 → 五行选字。<b>这是出生后的第一动作</b>，前面的名字都要过这道尺。</div>
  <div class="rcard"><h3>② 家族结构尺</h3>老大斯卯的“卯时破晓·地支嵌字”手法；兄弟成对不撞、生肖（丙午马）藏字。<b>自家体系，外人无法复制</b>。</div>
  <div class="rcard"><h3>③ 气质审美尺</h3>六大方向（下表）。Skill 气质光谱 + 风格原型帮你看清“这个家到底偏好哪种味道”。</div>
  <div class="rcard"><h3>④ 实用红线尺</h3>网红字 / 高歧义多音 / 生僻 / 笔画负担 / 方言（关中无特有雷区；陕北入声需长辈念读）。已对 627 名全量扫过。</div>
</div>

<h2>六个方向（每方向附池内代表）</h2>
<div class="dcards">
__CARDS__
</div>

<h2>收网路线（出生后执行）</h2>
<div class="steps">
  <div class="step"><b>出生当天：</b>把精确出生时间（公历 + 时辰）交给铁蛋——排盘、双源校验、定用神喜忌（扶抑 + 调候），这一步先于一切。</div>
  <div class="step"><b>八字 × 字库：</b>用用神五行走 liki 字库圈“命理适配”的字，交叉到六个方向里——哪些方向天然补你所缺，哪些方向要放弃（这不是审美问题，是尺子优先）。</div>
  <div class="step"><b>勾方向 × 选短名单：</b>从六个方向里挑 2–3 个偏好，在重估榜前 100 / 轻灵 30 / 家族承启系里选出 8–10 个短名单。</div>
  <div class="step"><b>家人投票 × 念读：</b>短名单走一遍全家投票（页面已有）；读一遍普通话 + 老家话（长辈把关入声字）；五格评分复核 → 定名。</div>
</div>

<footer>
  <b>方法论来源</b>：chinese-baby-naming（Seiya89757：八字/字辈/方言/反网红四维、气质光谱）· chinese-naming（zhangjk1207：五宜十忌、风格原型、诗词出处）· liki.hk 起名引擎（字库字频/取字池/评估）。<br>
  <b>红线</b>：大名小名均未定；所有名字均为候选，拟议名不得升格；“出生后结合真八字收网”是唯一收口方式。<br>
  <b>生成</b>：2026-10-16 · 铁蛋 · naming/_review2_build_directions.py
</footer>
</div>
</body>
</html>
"""

html = HTML.replace("__CARDS__", cards)
out = f"{BASE}/directions.html"
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out, len(html), "字符")
