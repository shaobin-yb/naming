# -*- coding: utf-8 -*-
"""由 _review_final.json(+可选 _review_candidates.json)生成「Skill 视角重估」单文件 HTML。"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

final = json.load(open(f"{BASE}/_review_final.json", encoding="utf-8"))
rows = final["rows"]
try:
    cand = json.load(open(f"{BASE}/_review_candidates.json", encoding="utf-8"))["items"]
except FileNotFoundError:
    cand = []

data_json = json.dumps(rows, ensure_ascii=False)
cand_json = json.dumps(cand, ensure_ascii=False)

# ── 发现区统计 ──────────────────────────────────────────────
top100 = [r for r in rows if r["rank0"]]
n_all = len(rows)
n_clean = sum(1 for r in top100 if not r["a_hits"])
duoyin_names = [r for r in rows if r["duoyin"]]
rare_names = [r for r in rows if any("生僻" in m or "未收录" in m for m in r["b_marks"])]
heavy_names = [r for r in rows if any("画" in m for m in r["b_marks"])]
best = sorted(top100, key=lambda r: -r["total"])[:3]
ups = sorted(top100, key=lambda r: r["rank1"] - r["rank0"])[:5]
downs = sorted(top100, key=lambda r: -(r["rank1"] - r["rank0"]))[:5]
freq_dist = {}
qx_dist = {}
for r in top100:
    qx_dist[r["qx"].split("(")[0]] = qx_dist.get(r["qx"].split("(")[0], 0) + 1

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# 网红命中名单文本
trendy_list = [r for r in top100 if any("核心" in h or "标签" in h or "年代" in h or "s·" in h.replace("2010s", "2010s·") or "2010s" in h or "2000s" in h for h in r["a_hits"])]
trendy_txt = " · ".join(f"<b>{esc(r['name'])}</b>({'/'.join(esc(h) for h in r['a_hits'])})" for r in trendy_list) or "(无)"

duoyin_txt = " · ".join(
    f"<b>{esc(r['name'])}</b>({'/'.join(r['duoyin'])})" for r in duoyin_names) or "(无)"

rare_txt = " · ".join(
    f"<b>{esc(r['name'])}</b>({'/'.join(esc(m) for m in r['b_marks'])})" for r in rare_names) or "(无)"
if len(rare_names) > 8:
    rare_txt = " · ".join(
        f"<b>{esc(r['name'])}</b>({'/'.join(esc(m) for m in r['b_marks'])})" for r in rare_names[:8]) \
        + f"　…等共 {len(rare_names)} 名"

up_txt = " · ".join(
    f"<b>{esc(r['name'])}</b> 原#{r['rank0']}→新#{r['rank1']}({r['rank1']-r['rank0']:+d})"
    for r in ups if r["rank1"] - r["rank0"] < 0) or "(无)"
down_txt = " · ".join(
    f"<b>{esc(r['name'])}</b> 原#{r['rank0']}→新#{r['rank1']}({r['rank1']-r['rank0']:+d})"
    for r in downs if r["rank1"] - r["rank0"] > 0) or "(无)"

best_txt = " · ".join(f"<b>{esc(r['name'])}</b> {r['total']}" for r in best)

qx_txt = " · ".join(f"{esc(k)} {v}" for k, v in sorted(qx_dist.items(), key=lambda x: -x[1]))

# 候选区 html
cand_html = ""
for c in cand:
    cand_html += f'''<div class="ccard">
  <div class="ctop"><span class="cnm">{esc(c["name"])}</span>
  <span class="cqx">{esc(c.get("qx",""))}</span></div>
  <p class="cnote">{esc(c.get("note",""))}</p>
  <p class="cquote">{esc(c.get("quote",""))}</p>
</div>'''

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skill 视角重估 · 十二典综合榜</title>
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
.tab .n{font-size:11px;opacity:.72;margin-left:3px}
.gap{flex:1}
select,input[type=search]{border:1px solid var(--line);background:var(--surf);
  border-radius:8px;padding:6px 10px;font-size:13.5px;color:var(--ink);font-family:inherit}
input[type=search]{width:128px}
.rows{margin-top:8px;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--surf)}
.row{display:grid;grid-template-columns:96px 106px 58px 168px 86px 1fr 150px;gap:8px;align-items:center;
  padding:9px 14px;border-bottom:1px solid var(--line);cursor:pointer;font-size:13.5px}
.row:last-child{border-bottom:none}
.row:hover{background:#f4f4f0}
.row .rk{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.row .rk .d{font-weight:700}
.d.up{color:var(--tai)} .d.dn{color:var(--bad)} .d.eq{color:var(--muted)}
.row .nm{font-size:19px;font-weight:700;letter-spacing:.06em;
  font-family:"Songti SC","STSong","SimSun",serif;white-space:nowrap}
.row .tot{font-size:16px;font-weight:700;font-variant-numeric:tabular-nums;color:var(--ink)}
.bars{display:grid;grid-template-columns:repeat(4,1fr);gap:3px}
.bars .bar{height:16px;border-radius:4px;background:#eeede8;position:relative;overflow:hidden}
.bars .bar i{position:absolute;left:0;top:0;bottom:0;border-radius:4px;opacity:.85}
.barA i{background:#C79A2B}.barB i{background:#2d8f5f}.barC i{background:#2d5f8f}.barD i{background:#C23B2E}
.row .qx{font-size:12px;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row .note{font-size:12.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.row .mk{font-size:11px}
.row .mk .m{display:inline-block;border-radius:5px;padding:0 5px;margin-right:3px}
.m-warn{background:#faf0dd;color:#a3680a}.m-good{background:#e7f4ec;color:#217a4a}
.m-info{background:#e8eef5;color:#2d5f8f}.m-bad{background:#f8e7e2;color:#a33f2a}
.det{display:none;grid-column:1/-1;padding:8px 4px 2px;font-size:12.5px;color:var(--ink2);
  border-top:1px dashed var(--line);margin-top:2px}
.row.open .det{display:block}
.ccards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.ccard{background:var(--surf);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.ctop{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}
.cnm{font-size:22px;font-weight:700;letter-spacing:.08em;
  font-family:"Songti SC","STSong","SimSun",serif}
.cqx{margin-left:auto;font-size:12px;color:var(--blue);background:#e8eef5;border-radius:6px;padding:1px 8px}
.cnote{font-size:13.5px;margin:0 0 6px}
.cquote{font-size:12.5px;color:var(--ink2);margin:0;padding-left:10px;border-left:2px solid var(--line)}
footer{margin-top:46px;padding-top:18px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--muted);line-height:1.9}
footer b{color:var(--ink2)}
@media (max-width:760px){
  .row{grid-template-columns:92px 82px 44px 1fr}
  .row .bars,.row .qx,.row .mk{display:none}
  .fcards,.ccards{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Skill 视角重估<span class="seal">王</span></h1>
  <p class="sub">综合榜 Top100（+大师提名 4 名）· 用新装起名 Skill 的方法论做一次换视角体检：<b>时代穿透 / 日常可用 / 音律 / 意象气质</b> 四维各 25 分 · 与原五格评分<b>并行参考、不替代</b> · 原页未做任何改动</p>
  <div class="stats" id="stats"></div>
</header>

<h2>六点新思路</h2>
<div class="fcards">
  <div class="fcard">
    <h3>① 时代穿透：这是池子的隐藏优势</h3>
    <span class="tag t-good">核心网红字 0 命中</span>
    <p>Top100 中"梓涵轩睿沐晨辰熙佳"这类 2020s 烂大街核心字 <b>零命中</b>（全网重名率最高的字完全避开）。仅少量次级/年代标签字需留意：<br>__TRENDY__</p>
  </div>
  <div class="fcard">
    <h3>② 多音字盲区（字库比原口径查出的更多）</h3>
    <span class="tag t-warn">建议补进口径</span>
    <p>原评分口径的杜撰风险表（重/乐/和/行/饮）之外，字库还查出：<br>__DUOYIN__<br>读音不确定的名字自我介绍会被反复追问。</p>
  </div>
  <div class="fcard">
    <h3>③ 生僻度与书写负担</h3>
    <span class="tag t-info">字频/笔画客观数据</span>
    <p>字库标注"rare"的字与 ≥20 画的字：<br>__RARE__<br>__HEAVY__</p>
  </div>
  <div class="fcard">
    <h3>④ 五格数理 vs 审美意象：两把尺子的错位</h3>
    <span class="tag t-info">最大发现</span>
    <p>五格体系下"结构系"（元/午系等家族结构名）吃数理红利；<b>豪放/清幽派</b>（大师批+楚辞批）受数理压制排名偏低。Skill 视角下后者普遍上升——<b>两条路线（结构建设 vs 意象审美）建议分开看，不必相互降权</b>。</p>
    <p>上升最多：__UPS__<br>下降最多：__DOWNS__</p>
  </div>
  <div class="fcard">
    <h3>⑤ 气质光谱分布</h3>
    <span class="tag t-info">按意象归类</span>
    <p>__QX__</p>
    <p>草木自然（中药系）与五劫古奥系为两翼，中间"温润/书卷"层最厚——整体气质偏"老成持重"，<b>轻灵少年气</b>方向偏薄。</p>
  </div>
  <div class="fcard">
    <h3>⑥ 方言与谐音</h3>
    <span class="tag t-warn">需家庭方言信息</span>
    <p>跨方言通用雷区已扫（尸系音/三连同调/平仄），本批<b>无高危命中</b>。粤语/闽南/潮汕/四川等 13 种方言的定向深扫需要知道<b>家庭实际使用的方言</b>——告诉铁蛋方言种类即可补扫。</p>
  </div>
</div>

<h2>重估榜（104 名）</h2>
<div class="controls">
  <div class="tabs" id="tabs"></div>
  <div class="gap"></div>
  <input type="search" id="q" placeholder="搜名字/用字…">
  <select id="sort">
    <option value="new">Skill 总分 高→低</option>
    <option value="old">原榜序</option>
    <option value="up">上升最多</option>
    <option value="down">下降最多</option>
  </select>
</div>
<div class="rows" id="rows"></div>

__CAND_SEC__

<footer>
  <b>口径说明</b>：四维分 = 时代穿透 25（网红/年代标签字扣分，经典字加分）＋日常可用 25（字库字频与笔画）＋音律 25（声调收尾/同调/多音）＋意象气质 25（人工逐名评审）。与原五格分<b>口径不同、不构成替代</b>，两者并行参考。<br>
  <b>数据来源</b>：字库字频/五行/笔画/声调来自 liki.hk 起名引擎（qiming_char，2026-10-13 实测）；网红字库来自 chinese-baby-naming Skill（Seiya89757）；气质评审参照 chinese-naming Skill（zhangjk1207）五宜十忌与风格原型；方言雷区来自 chinese-baby-naming 13 方言库。<br>
  <b>红线</b>：本页所有名字均为<b>候选</b>；大名小名均未定，出生后结合真八字收网。原「十二典撷名」与「综合榜」页未做任何改动，本页为独立评估参考。<br>
  <b>生成</b>：2026-10-13 · 铁蛋 · 本页由 naming/_review_build_html.py 自动生成
</footer>
</div>
<script>
const DATA = __DATA__;
const CAND_N = 0;
const QX_COLORS = {};
function dcls(d){ return d<0?"up":(d>0?"dn":"eq"); }
function qxGroup(q){ q=(q||"").split("(")[0]; if(/豪放|五劫|古奥|气象/.test(q)) return "豪放气象"; if(/清幽|空灵/.test(q)) return "清幽空灵"; if(/道家|古朴|玄|虚白/.test(q)) return "道家古朴"; if(/传承|本元|家族/.test(q)) return "本元传承"; if(/书卷|诗经|楚辞|论语|中庸|易经|庄子|抱朴|经典|致敬|光明|月神|云程/.test(q)) return "经典书卷"; if(/中药|草木|植物|自然/.test(q)) return "草木自然"; if(/温润|德性|心学/.test(q)) return "温润德性"; return "其他"; }
let curQx = "全部", curQ = "", curSort = "new";

function badgeMarks(r){
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
  let list = DATA.slice();
  if (curQx !== "全部") list = list.filter(r => qxGroup(r.qx) === curQx);
  if (curQ) list = list.filter(r => r.name.includes(curQ) || (r.note||"").includes(curQ) || (r.qx||"").includes(curQ));
  if (curSort === "new") list.sort((a,b)=> b.total - a.total);
  else if (curSort === "old") list.sort((a,b)=> (a.rank0||999) - (b.rank0||999));
  else if (curSort === "up") list.sort((a,b)=> (a.rank0&&a.rank1? a.rank1-a.rank0 : 999) - (b.rank0&&b.rank1? b.rank1-b.rank0 : 999));
  else if (curSort === "down") list.sort((a,b)=> (b.rank0&&b.rank1? b.rank1-b.rank0 : -999) - (a.rank0&&a.rank1? a.rank1-a.rank0 : -999));

  const box = document.getElementById("rows");
  box.innerHTML = list.map(r => {
    const d = (r.rank0 && r.rank1) ? (r.rank1 - r.rank0) : null;
    const dhtml = d === null ? '<span class="d eq">未入榜</span>'
      : '<span class="d '+dcls(d)+'">'+(d>0?"↓"+d:(d<0?"↑"+(-d):"—"))+'</span>';
    const rk = r.rank0 ? "原#"+r.rank0+" → 新#"+(r.rank1||"-") : "大师提名·未入前100";
    const bars = ['A','B','C','D'].map(k =>
      '<div class="bar bar'+k+'" title="'+k+' '+r[k]+'/25"><i style="width:'+(r[k]/25*100)+'%"></i></div>').join("");
    const det = '<div class="det">四维：时代穿透 '+r.A+' · 日常可用 '+r.B+' · 音律 '+r.C+' · 意象气质 '+r.D
      + '　|　声调序列 '+((r.tones||[]).join("-"))
      + (r.a_hits.length? '　|　'+r.a_hits.join("、"):"")
      + (r.b_marks.length? '　|　'+r.b_marks.join("、"):"")
      + '　|　原五格分 '+(r.score0||"—")+'　'+r.src+'</div>';
    return '<div class="row" onclick="this.classList.toggle(&quot;open&quot;)">'
      + '<span class="rk">'+rk+'<br>'+dhtml+'</span>'
      + '<span class="nm">'+r.name+'</span>'
      + '<span class="tot">'+r.total+'</span>'
      + '<div class="bars">'+bars+'</div>'
      + '<span class="qx">'+(r.qx||"")+'</span>'
      + '<span class="note" title="'+r.note+'">'+r.note+'</span>'
      + '<span class="mk">'+badgeMarks(r)+'</span>'
      + det + '</div>';
  }).join("");
}

const qxSet = {};
DATA.forEach(r => { const k=qxGroup(r.qx); if(k) qxSet[k]=(qxSet[k]||0)+1; });
const tabs = ['全部'].concat(Object.keys(qxSet).sort((a,b)=>qxSet[b]-qxSet[a]));
document.getElementById("tabs").innerHTML = tabs.map(t =>
  '<span class="tab'+(t===curQx?" on":"")+'" data-qx="'+t+'">'+t+(t==="全部"?"":'<span class="n">'+qxSet[t]+"</span>")+'</span>').join("");
document.querySelectorAll(".tab").forEach(el => el.onclick = () => {
  curQx = el.dataset.qx;
  document.querySelectorAll(".tab").forEach(x => x.classList.toggle("on", x===el));
  render();
});
document.getElementById("q").oninput = e => { curQ = e.target.value.trim(); render(); };
document.getElementById("sort").onchange = e => { curSort = e.target.value; render(); };

const nA = DATA.filter(r => r.A >= 25).length;
const nD = DATA.filter(r => r.D >= 22).length;
document.getElementById("stats").innerHTML =
  '<span class="stat"><b>'+DATA.length+'</b>名重估</span>'
  + '<span class="stat g"><b>'+nA+'</b>名时代穿透满分</span>'
  + '<span class="stat w"><b>'+DATA.filter(r=>r.duoyin.length).length+'</b>名多音提醒</span>'
  + '<span class="stat r"><b>'+DATA.filter(r=>r.a_hits.some(h=>h.includes("核心"))).length+'</b>名网红核心字</span>'
  + '<span class="stat"><b>'+nD+'</b>名气质优秀(D≥22)</span>';

render();
</script>
</body>
</html>
"""

# 候选区
if cand:
    cand_sec = ("<h2>Skill 新候选（补充生成 · 未入池未评分）</h2>\n"
                "<p style='font-size:13px;color:var(--muted);margin:0 0 10px'>"
                "按 Skill 方法论生成，方向为补池子缺位气质；均为草案，未走五格评分，供找方向用。</p>\n"
                f"<div class='ccards'>{cand_html}</div>")
else:
    cand_sec = ""

html = (HTML
        .replace("__DATA__", data_json)
        .replace("__TRENDY__", trendy_txt)
        .replace("__DUOYIN__", duoyin_txt)
        .replace("__RARE__", rare_txt)
        .replace("__HEAVY__", "笔画偏重：" + (" · ".join(f"<b>{esc(r['name'])}</b>({'/'.join(esc(m) for m in r['b_marks'] if '画' in m)})" for r in heavy_names) if heavy_names else "(无)"))
        .replace("__UPS__", up_txt)
        .replace("__DOWNS__", down_txt)
        .replace("__QX__", qx_txt)
        .replace("__CAND_SEC__", cand_sec)
        )

out = f"{BASE}/skill-review.html"
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out, len(html), "字符")
