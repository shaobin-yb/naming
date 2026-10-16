# -*- coding: utf-8 -*-
"""skill-review.html v2:十二典+综合榜 627 全量重估 → 前 200 榜。"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

final = json.load(open(f"{BASE}/_review2_final.json", encoding="utf-8"))
rows = final["rows"]
top200 = [r for r in rows if r["top200"]]

data_json = json.dumps(rows, ensure_ascii=False)

# ── 统计 ──
n_all = len(rows)
n_clean = sum(1 for r in rows if not any("网红" in h or "标签" in h or "年代" in h for h in r["a_hits"]))
duoyin_rows = [r for r in rows if r["duoyin"]]  # 数据已按高歧义 UNION 表过滤
rare_rows = [r for r in rows if any("生僻" in m or "库外" in m for m in r["b_marks"])]
heavy_rows = [r for r in rows if any("画" in m for m in r["b_marks"])]
core_rows = [r for r in rows if any("网红核心" in h for h in r["a_hits"])]
door = rows[199]

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

TRENDY = set("梓涵轩睿沐晨辰熙佳")
SEC = set("子宇泽悦然可昕萱瑶桐")
MID = set("嘉浩思雨")
OLD = set("婷倩颖雪静健伟强龙")
AGE = set("建伟强军丽芳娟慧国华文卫忠志玉淑桂英霞")

def tag_txt(r):
    hits = []
    for ch in r["name"][1:]:
        if ch in TRENDY: hits.append(f"网红核心·{ch}")
        elif ch in SEC: hits.append(f"次级标签·{ch}")
        if ch in MID: hits.append(f"2010s·{ch}")
        if ch in OLD: hits.append(f"2000s·{ch}")
        if ch in AGE: hits.append(f"年代字·{ch}")
    return hits

trendy_rows = [r for r in rows if tag_txt(r)]
trendy_sample = " · ".join(f"<b>{esc(r['name'])}</b>({'/'.join(tag_txt(r))})" for r in trendy_rows[:10])
if len(trendy_rows) > 10:
    trendy_sample += f"　…等共 {len(trendy_rows)} 名"

duoyin_sample = " · ".join(f"<b>{esc(r['name'])}</b>({'/'.join(r['duoyin'])})" for r in duoyin_rows[:10])
if len(duoyin_rows) > 10:
    duoyin_sample += f"　…等共 {len(duoyin_rows)} 名"

rare_names = [r for r in rare_rows if any("生僻" in m for m in r["b_marks"])]
rare_sample = " · ".join(f"<b>{esc(r['name'])}</b>({'/'.join(m for m in r['b_marks'] if '生僻' in m)})" for r in rare_names[:8]) or "(无)"
heavy_sample = " · ".join(f"<b>{esc(r['name'])}</b>({'/'.join(m for m in r['b_marks'] if '画' in m)})" for r in heavy_rows[:8]) or "(无)"

# 黑马:五格低分高排(前50内五格最低5个)/ 五格高分低排(五格>=90 且 rank2>200)
top50 = rows[:50]
darkhorse = sorted([r for r in top50 if r["score0"]], key=lambda r: r["score0"])[:6]
dh_txt = " · ".join(f"<b>{esc(r['name'])}</b>(五格{r['score0']} → 四维#{r['rank2']})" for r in darkhorse)
highwuge_low = sorted([r for r in rows if (r["score0"] or 0) >= 90 and r["rank2"] > 150], key=lambda r: -r["score0"])[:6]
hl_txt = " · ".join(f"<b>{esc(r['name'])}</b>(五格{r['score0']} → 四维#{r['rank2']})" for r in highwuge_low) or "(无)"

# 气质分布(627 口径,用 meaning/book 关键词粗分)
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

from collections import Counter
qxc = Counter(qx_of(r) for r in rows)
qx_txt = " · ".join(f"{k} {v}" for k, v in qxc.most_common())

# 三连同调(王2+名两字同调且为2)
t3 = [r for r in rows if r["tones"] and len(r["tones"]) == 3 and len(set(x for x in r["tones"] if x)) == 1 and r["tones"][0] == 2]
t3_txt = " · ".join(f"<b>{esc(r['name'])}</b>" for r in t3[:12]) or "(无)"

# 入声字(晋语区发音短促;常用入声字简表)
RUSHENG = set("一七八十白竹玉月石德福食急活跃触发达北国别绝略协学 及 独 复 物 质 实 直 积 习 集 立 力 日\n及".replace("\n", "").replace(" ", ""))
rush_rows = []
for r in rows[:200]:
    hit = [ch for ch in r["name"] if ch in RUSHENG]
    if hit:
        rush_rows.append((r["name"], "".join(hit)))
rush_txt = " · ".join(f"<b>{esc(n)}</b>({'/'.join(h)})" for n, h in rush_rows[:12])
if len(rush_rows) > 12:
    rush_txt += f"　…等共 {len(rush_rows)} 名"

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skill 视角重估 v2 · 十二典+综合榜 627 名</title>
<style>
:root{
  --surf:#fcfcfb; --page:#f9f9f7; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
  --line:#e1e0d9; --jiang:#C23B2E; --gold:#C79A2B;
  --tai:#2d8f5f; --warn:#c07a1a; --bad:#b3543f; --blue:#2d5f8f;
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
.stats{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px}
.stat{background:var(--surf);border:1px solid var(--line);border-radius:10px;
  padding:8px 14px;font-size:13px;color:var(--ink2)}
.stat b{font-size:17px;color:var(--ink);margin-right:4px;font-variant-numeric:tabular-nums}
.stat.g b{color:var(--tai)} .stat.w b{color:var(--warn)} .stat.r b{color:var(--bad)}
h2{font-size:19px;letter-spacing:.08em;margin:34px 0 10px;
  font-family:"Songti SC","STSong","SimSun",serif}
.fcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.fcard{background:var(--surf);border:1px solid var(--line);border-radius:12px;
  padding:14px 16px;font-size:13.5px;color:var(--ink2)}
.fcard h3{margin:0 0 6px;font-size:14.5px;color:var(--ink)}
.fcard b{color:var(--ink)}
.fcard .tag{display:inline-block;font-size:11px;border-radius:6px;padding:1px 7px;margin-right:6px}
.t-good{background:#e7f4ec;color:#217a4a}.t-warn{background:#faf0dd;color:#a3680a}
.t-info{background:#e8eef5;color:#2d5f8f}
.controls{position:sticky;top:0;z-index:20;background:linear-gradient(var(--page) 82%,transparent);
  padding:12px 0 10px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}
.tabs{display:flex;flex-wrap:wrap;gap:6px}
.tab{border:1px solid var(--line);background:var(--surf);border-radius:999px;
  padding:6px 13px;font-size:13px;cursor:pointer;color:var(--ink2);transition:all .15s}
.tab:hover{border-color:#bbb}
.tab.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.gap{flex:1}
select,input[type=search]{border:1px solid var(--line);background:var(--surf);
  border-radius:8px;padding:6px 10px;font-size:13.5px;color:var(--ink);font-family:inherit}
input[type=search]{width:128px}
.rows{margin-top:8px;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--surf)}
.row{display:grid;grid-template-columns:58px 104px 58px 168px 66px 88px 1fr;gap:8px;align-items:center;
  padding:8px 14px;border-bottom:1px solid var(--line);cursor:pointer;font-size:13.5px}
.row:last-child{border-bottom:none}
.row:hover{background:#f4f4f0}
.row .rk{font-size:12.5px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:600}
.row .rk.door{color:var(--jiang)}
.row .nm{font-size:19px;font-weight:700;letter-spacing:.06em;
  font-family:"Songti SC","STSong","SimSun",serif;white-space:nowrap}
.row .tot{font-size:16px;font-weight:700;font-variant-numeric:tabular-nums;color:var(--ink)}
.bars{display:grid;grid-template-columns:repeat(4,1fr);gap:3px}
.bars .bar{height:15px;border-radius:4px;background:#eeede8;position:relative;overflow:hidden}
.bars .bar i{position:absolute;left:0;top:0;bottom:0;border-radius:4px;opacity:.85}
.barA i{background:#C79A2B}.barB i{background:#2d8f5f}.barC i{background:#2d5f8f}.barD i{background:#C23B2E}
.row .w5{font-size:12.5px;color:var(--ink2);font-variant-numeric:tabular-nums;white-space:nowrap}
.row .src{font-size:12px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.row .mk{font-size:11px;white-space:nowrap;overflow:hidden}
.row .mk .m{display:inline-block;border-radius:5px;padding:0 5px;margin-right:3px}
.m-warn{background:#faf0dd;color:#a3680a}.m-good{background:#e7f4ec;color:#217a4a}
.m-info{background:#e8eef5;color:#2d5f8f}.m-bad{background:#f8e7e2;color:#a33f2a}
.det{display:none;grid-column:1/-1;padding:8px 4px 2px;font-size:12.5px;color:var(--ink2);
  border-top:1px dashed var(--line);margin-top:2px;line-height:1.8}
.row.open .det{display:block}
.candlink{display:block;background:var(--surf);border:1px solid var(--line);border-radius:12px;
  padding:16px 20px;text-decoration:none;color:var(--ink);margin-top:8px;
  border-left:3px solid var(--gold);transition:box-shadow .15s}
.candlink:hover{box-shadow:0 4px 16px rgba(20,20,10,.08)}
.candlink b{font-size:15.5px}
.candlink span{color:var(--ink2);font-size:13px}
footer{margin-top:46px;padding-top:18px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--muted);line-height:1.9}
footer b{color:var(--ink2)}
@media (max-width:860px){
  .row{grid-template-columns:52px 84px 46px 1fr}
  .row .bars,.row .w5,.row .mk{display:none}
  .row .src{font-size:11.5px}
  .fcards{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Skill 视角重估<span class="seal">王</span></h1>
  <p class="sub">十二典+综合榜<b>全部 627 名</b> · 用起名 Skill 方法论做换视角体检：<b>时代穿透 / 日常可用 / 音律 / 意象气质</b> 四维各 25 分 · 全部重估后<b>收录前 200</b> · 与原五格评分<b>并行参考、不替代</b> · 原页未做任何改动 &nbsp;|&nbsp; <a href="overview.html">总览</a> | <a href="qingling.html">轻灵少年气 30 候选 →</a></p>
  <div class="stats" id="stats"></div>
</header>

<h2>六点新思路</h2>
<div class="fcards">
  <div class="fcard">
    <h3>① 时代穿透：池子的隐藏优势（627 口径）</h3>
    <span class="tag t-good">__NCLEAN__ / 627 满分</span>
    <p>627 名中"梓涵轩睿沐晨辰熙佳"这类 2020s 核心字仅 <b>1 名</b>命中：<b>王缉熙</b>（诗经"缉熙敬止"撞上热搜字"熙"，古典出处也难免疫）。次级/年代标签字共 __NTRENDY__ 名：<br>__TRENDY__</p>
  </div>
  <div class="fcard">
    <h3>② 多音字盲区：日常高歧义字</h3>
    <span class="tag t-warn">__NDUOYIN__ 名命中</span>
    <p>日常高歧义多音字（行/乐/参/朴/柏/朝/兴/长…类，会真被念错）扫描命中：<br>__DUOYIN__<br>读音不确定的名字，自我介绍会被反复追问。</p>
  </div>
  <div class="fcard">
    <h3>③ 生僻度与书写负担</h3>
    <span class="tag t-info">字频全库客观数据</span>
    <p>字库标注"rare"的字：__RARE__<br>≥20 画字：__HEAVY__</p>
  </div>
  <div class="fcard">
    <h3>④ 五格数理 vs 审美意象：两把尺子的错位</h3>
    <span class="tag t-info">最大发现</span>
    <p>五格体系下"结构系"吃数理红利、豪放/清幽派受数理压制；Skill 视角下系统性翻转。前 50 的"低分黑马"：<br>__DARKHORSE__</p>
    <p>反向（五格 ≥90 但四维跌出前 150）：__HIGHWUGE__</p>
  </div>
  <div class="fcard">
    <h3>⑤ 气质光谱分布（627 口径）</h3>
    <span class="tag t-info">按意象归类·粗分</span>
    <p>__QX__</p>
    <p>整体偏"老成持重"，<b>轻灵少年气方向偏薄</b>——30 个补位候选见独立页（页首链接）。</p>
  </div>
  <div class="fcard">
    <h3>⑥ 陕西方言扫描（关中 / 陕北）</h3>
    <span class="tag t-warn">低置信项需长辈核</span>
    <p><b>关中</b>（中原官话）：与普通话谐音雷区高度重合，全池未发现关中音特有雷区（个别地区"诗/湿"类感较强，池中无命中）。<br><b>陕北</b>（晋语，入声保留）：入声字念感短促，前 200 中命中：__RUSH__——建议家中长辈用家乡话念一遍候选名。<br>三连同调（普通话）：__T3__</p>
  </div>
</div>

<h2>重估榜 · 前 200</h2>
<div class="controls">
  <div class="tabs">
    <span class="tab on" data-scope="200">前 200</span>
    <span class="tab" data-scope="all">全部 627</span>
  </div>
  <div class="gap"></div>
  <input type="search" id="q" placeholder="搜名字/寓意…">
  <select id="sort">
    <option value="new">四维总分 高→低</option>
    <option value="w5">原五格分 高→低</option>
    <option value="book">按来源序</option>
  </select>
</div>
<div class="rows" id="rows"></div>

<h2>灵少年气 · 独立候选页</h2>
<a class="candlink" href="qingling.html">
  <b>轻灵少年气 · 王姓男孩 30 个备选参考 →</b>
  <span>　补池子缺位方向：明快/清亮/少年感 · 清越/朗川/既白/鹿鸣/云帆/听松… 含出处与肌理，全部已查重</span>
</a>

<footer>
  <b>口径说明</b>：四维各 25 分——<b>时代穿透</b>（网红字库扣分、经典字加分）＋<b>日常可用</b>（字频：liki 起名引擎全库 7649 字表；笔画：康熙口径）＋<b>音律</b>（声调按普通话常用读音、多读音与同调扣分）＋<b>意象气质</b>（人工逐名评审）。总分 100，与原五格分<b>口径不同、不构成替代</b>。<br>
  <b>数据来源</b>：字频/取字池来自 liki.hk 起名引擎（2026-10-14 实测，五池全表）；网红字库与方言雷区库来自 chinese-baby-naming Skill（Seiya89757）；气质评审参照 chinese-naming Skill（zhangjk1207）；声调/多读音为 pypinyin 标准普通话。<br>
  <b>红线</b>：本页所有名字均为<b>候选</b>；大名小名均未定，出生后结合真八字收网。原「十二典撷名」页未做任何改动，本页为独立评估参考。<br>
  <b>生成</b>：2026-10-14 · 铁蛋 · naming/_review2_build_v2.py
</footer>
</div>
<script>
const DATA = __DATA__;
const DOOR = __DOOR__;
let scope = "200", curQ = "", curSort = "new";
function dcls(d){ return d<0?"up":(d>0?"dn":"eq"); }

function marksOf(r){
  let h = "";
  for (const x of r.a_hits){
    if (x.includes("核心")) h += '<span class="m m-bad">'+x+'</span>';
    else h += '<span class="m m-warn">'+x+'</span>';
  }
  for (const x of r.duoyin) h += '<span class="m m-warn">多音·'+x+'</span>';
  for (const x of r.b_marks) h += '<span class="m m-info">'+x+'</span>';
  return h;
}

function render(){
  let list = (scope === "200") ? DATA.filter(r => r.top200) : DATA.slice();
  if (curQ) list = list.filter(r => r.name.includes(curQ) || (r.meaning||"").includes(curQ) || (r.book||"").includes(curQ));
  if (curSort === "new") list.sort((a,b)=> b.total - a.total);
  else if (curSort === "w5") list.sort((a,b)=> (b.score0||0) - (a.score0||0));
  else if (curSort === "book") list.sort((a,b)=> (a.book||"zz").localeCompare(b.book||"zz") || (a.rank2-b.rank2));
  const box = document.getElementById("rows");
  box.innerHTML = list.map(r => {
    const rk = '<span class="rk'+(r.rank2 === 200 ? ' door' : '')+'">#'+r.rank2+(r.rank2 === 200 ? ' 门槛' : '')+'</span>';
    const bars = ['A','B','C','D'].map(k =>
      '<div class="bar bar'+k+'" title="'+k+' '+r[k]+'/25"><i style="width:'+(r[k]/25*100)+'%"></i></div>').join("");
    const det = '<div class="det"><b>四维</b>：时代穿透 '+r.A+' · 日常可用 '+r.B+' · 音律 '+r.C+' · 意象气质 '+r.D
      + '　|　<b>声调</b> '+((r.tones||[]).join("-").replace(/null/g,"?"))
      + '　|　<b>原五格</b> '+(r.score0||"—")+' '+(r.tier0||"")+'　|　<b>来源</b> '+r.src+(r.book?(' '+r.book):'')
      + (r.meaning ? '<br><b>寓意</b>：'+r.meaning : "")
      + (r.a_hits.length ? '<br><b>标记</b>：'+r.a_hits.concat(r.b_marks).concat(r.duoyin.map(x=>"多音·"+x)).join("、") : "")
      + '</div>';
    return '<div class="row" onclick="this.classList.toggle(&quot;open&quot;)">'
      + rk
      + '<span class="nm">'+r.name+'</span>'
      + '<span class="tot">'+r.total+'</span>'
      + '<div class="bars">'+bars+'</div>'
      + '<span class="w5">'+(r.score0||"—")+'</span>'
      + '<span class="src">'+(r.book||r.src)+'</span>'
      + '<span class="mk">'+marksOf(r)+'</span>'
      + det + '</div>';
  }).join("");
}

document.querySelectorAll(".tab").forEach(el => el.onclick = () => {
  scope = el.dataset.scope;
  document.querySelectorAll(".tab").forEach(x => x.classList.toggle("on", x===el));
  render();
});
document.getElementById("q").oninput = e => { curQ = e.target.value.trim(); render(); };
document.getElementById("sort").onchange = e => { curSort = e.target.value; render(); };

document.getElementById("stats").innerHTML =
  '<span class="stat"><b>627</b>名全量重估</span>'
  + '<span class="stat g"><b>' + DATA.filter(r=>r.top200).length + '</b>名收录前200</span>'
  + '<span class="stat w"><b>' + DOOR + '</b>前200门槛分</span>'
  + '<span class="stat"><b>' + DATA.filter(r=>!r.a_hits.some(h=>h.includes("核心"))).length + '</b>名无网红核心字</span>'
  + '<span class="stat r"><b>1</b>名撞核心网红字(缉熙)</span>';

render();
</script>
</body>
</html>
"""

html = (HTML
        .replace("__NCLEAN__", str(n_clean))
        .replace("__NTRENDY__", str(len(trendy_rows)))
        .replace("__NDUOYIN__", str(len(duoyin_rows)))
        .replace("__TRENDY__", trendy_sample)
        .replace("__DUOYIN__", duoyin_sample)
        .replace("__RARE__", rare_sample)
        .replace("__HEAVY__", heavy_sample)
        .replace("__DARKHORSE__", dh_txt)
        .replace("__HIGHWUGE__", hl_txt)
        .replace("__QX__", qx_txt)
        .replace("__RUSH__", rush_txt)
        .replace("__T3__", t3_txt)
        .replace("__DATA__", data_json)
        .replace("__DOOR__", f"{door['total']:.1f}")
        )

out = f"{BASE}/skill-review.html"
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out, len(html), "字符")
print(f"统计: 穿透满分 {n_clean} | 标签 {len(trendy_rows)} | 多音 {len(duoyin_rows)} | rare {len(rare_rows)} | 门槛 {door['total']}")
