# -*- coding: utf-8 -*-
"""重估榜·前100 卡片版(h轻灵页版式) → review-top100.html"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

final = json.load(open(f"{BASE}/_review2_final.json", encoding="utf-8"))["rows"]
pool = {x["name"]: x for x in json.load(open(f"{BASE}/_review2_pool.json", encoding="utf-8"))["names"]}
top100 = [r for r in final if r["rank2"] <= 100]

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def qx_of(r):
    t = (r["book"] or "") + "|" + (r.get("meaning") or "") + "|" + r["name"]
    RULES = [
        ("草木自然", ["本草","甘棠","杜若","空青","辛夷","茯苓","苁蓉","桔梗","玉竹","马兰","丹参","赤芝","药","草","竹","兰","芝","苓","花","木","棠","松"]),
        ("道家古朴", ["道德经","抱朴","太一","守静","谷神","虚白","朴","玄","虚","道","真"]),
        ("清幽空灵", ["望舒","浸阳","月","雨","雪","露","夜","幽","静","晚","烟","泉","溪","鹤","舟","浸"]),
        ("豪放气象", ["岳","霄","龙","鹏","江","海","川","山","云","风","雷","星","翔","飞","天"]),
        ("本元传承", ["五劫","劫","承","继","绍","兄弟","家族","元","斯"]),
        ("经典书卷", ["诗经","楚辞","周易","尚书","礼记","左传","中庸","论语","观止","诗","书","礼","易","文","明","知","思","学","贤","哲"]),
        ("温润德性", ["德","善","温","和","安","宁","仁","义","忠","恕","谦","恭","敬","孝"]),
    ]
    for qx, kws in RULES:
        if any(k in t for k in kws):
            return qx
    return "其他"

cards = ""
for r in top100:
    p = pool.get(r["name"], {})
    meaning = (p.get("meaning") or "").strip()
    quote = (p.get("quote") or "").strip()
    book = (r["book"] or "").strip()
    if len(meaning) > 110: meaning = meaning[:110] + "…"
    if len(quote) > 70: quote = quote[:70] + "…"
    if book and quote:
        qt = f"出处：《{esc(book)}》「{esc(quote)}」"
    elif quote:
        qt = esc(quote)
    else:
        qt = ""
    meta = f"四维 {r['total']}（穿透{r['A']} · 日常{r['B']} · 音律{r['C']} · 气质{r['D']}）" + (f" ｜ 原五格 {r['score0']}" if r["score0"] else "")
    cards += f'''<div class="ccard">
  <div class="ctop"><span class="num">{r['rank2']:02d}</span><span class="cnm">{esc(r['name'])}</span>
  <span class="cqx">{qx_of(r)}</span></div>
  <p class="cnote">{esc(meaning)}</p>
  <p class="cquote">{qt}</p>
  <p class="cmeta">{meta}</p>
</div>
'''

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>重估榜 · 前一百 · 王姓男孩</title>
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
.num{font-size:12.5px;color:var(--jiang);font-weight:700;font-variant-numeric:tabular-nums}
.cnm{font-size:23px;font-weight:700;letter-spacing:.08em;
  font-family:"Songti SC","STSong","SimSun",serif}
.cqx{margin-left:auto;font-size:12px;color:var(--blue);background:#e8eef5;border-radius:6px;padding:1px 8px;white-space:nowrap}
.cnote{font-size:13.5px;margin:0 0 6px}
.cquote{font-size:12.5px;color:var(--ink2);margin:0 0 6px;padding-left:10px;border-left:2px solid var(--line)}
.cmeta{font-size:11.5px;color:var(--muted);margin:6px 0 0;padding-top:6px;border-top:1px dashed var(--line);font-variant-numeric:tabular-nums}
footer{margin-top:46px;padding-top:18px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--muted);line-height:1.9}
footer b{color:var(--ink2)}
@media (max-width:560px){ .ccards{grid-template-columns:1fr} }
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>重估榜 · 前一百<span class="seal">王</span></h1>
  <p class="sub">十二典+综合榜 627 名全量四维重估 · <b>收录前 100</b> · 卡片按重估名次排列 · <a href="overview.html">总览</a> · <a href="skill-review.html">完整重估榜（627 名）→</a></p>
</header>

<p class="intro">本页为 <b>Skill 视角重估</b>（时代穿透 / 日常可用 / 音律 / 意象气质，各 25 分）627 名全量中的<b>前 100 名</b>卡片版。每张卡：名字 + 气质归类（粗分，供快速浏览）+ 寓意 / 出处 + 四维与五格明细。与原五格评分<b>并行参考、不替代</b>；所有名字均为候选，出生后结合真八字收网。</p>

<div class="ccards">
__CARDS__
</div>

<footer>
  <b>口径</b>：四维各 25 分——时代穿透（网红字库）＋日常可用（字频全库表 + 康熙笔画）＋音律（普通话声调与多读音）＋意象气质（人工逐名评审）。收录门槛 __DOOR__ 分。<br>
  <b>数据</b>：字频/取字池来自 liki.hk 起名引擎；网红字库与方言雷区来自 chinese-baby-naming Skill；气质评审参照 chinese-naming Skill。<br>
  <b>生成</b>：2026-10-16 · 铁蛋 · naming/_review2_build_top100.py
</footer>
</div>
</body>
</html>
"""

door = top100[-1]["total"]
html = HTML.replace("__CARDS__", cards).replace("__DOOR__", f"{door:.1f}")
out = f"{BASE}/review-top100.html"
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out, len(html), "字符; 门槛", door)
