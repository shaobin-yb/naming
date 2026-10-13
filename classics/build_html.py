# -*- coding: utf-8 -*-
"""十二典撷名 — 生成最终单文件 HTML（数据内联）。"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parent


def load_data():
    t = (ROOT / 'score_data.js').read_text(encoding='utf-8')
    d = json.loads(t[t.index('{'):t.rindex('}') + 1])
    flagged = {x[0]: x[1] for x in json.loads((ROOT / 'flagged.json').read_text(encoding='utf-8'))}
    for name, rec in d.items():
        rec['flag'] = flagged.get(name, '')
    return d


TIER_CLS = {"全绿": "b-tai", "一⚠️": "b-ok", "多⚠️": "b-warn", "慎用": "b-bad"}


def build_top100_section():
    """综合榜 · 前100（档案 + 榜单 + 大师提名 三源合排，数据见 naming/top100_data.json）。"""
    import html as H
    p = ROOT.parent / 'top100_data.json'
    if not p.exists():
        return ''
    d = json.loads(p.read_text(encoding='utf-8'))
    meta, lst = d['meta'], d['list']
    rows = []
    for r in lst:
        star = '<span class="star">★</span>' if r['src'] == '大师提名' else ''
        girl = '<span class="girl">女</span>' if r.get('f') == '女' else ''
        src = H.escape(r['src'])
        srccls = 'src mst' if r['src'] == '大师提名' else 'src'
        tier = TIER_CLS.get(r['tier'], '')
        rows.append(
            f'<tr>'
            f'<td class="rk">{r["rank"]}</td>'
            f'<td class="nm">{star}{H.escape(r["name"])}{girl}</td>'
            f'<td><span class="badge {tier}">{r["score"]} · {H.escape(r["tier"])}</span></td>'
            f'<td><span class="{srccls}">{src}</span></td>'
            f'<td class="nt ntcell">{H.escape(r["note"])}</td>'
            f'</tr>')
    miss = [m for m in meta['master_ranks'] if m['rank'] > meta['cut']]
    line = ''
    if miss:
        items = ' · '.join(f'{H.escape(m["n"])} #{m["rank"]}（{m["score"]}）' for m in miss)
        line = f'<p class="masterline"><b>★ 大师提名</b>其余位次：{items}</p>'
    return f'''
<section class="topsec" id="top100">
  <h2>综合榜 · 前 100</h2>
  <p class="tnote">档案 <b>{meta['archive_n']}</b> 名 + 榜单 <b>{meta['board_n']}</b> 名 + 大师提名 <b>{meta['master_n']}</b> 名 = <b>{meta['pool']}</b> 名不重复名字，统一口径合排（五格 + 三才 + 音形义，与十二典同标准），取前 {meta['cut']}。<span class="star">★</span> 为「寒假作业」提名名；<span class="girl">女</span> 为女孩名。{meta['date']}</p>
  <table class="t100">
    <thead><tr><th class="rk">#</th><th>名字</th><th>评分</th><th>来源</th><th class="ntcell">出处 / 一句话</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  {line}
</section>
<div class="divider">十二典精选 · 534 名（出处逐字可考）</div>
'''


def main():
    data = load_data()
    payload = json.dumps(data, ensure_ascii=False)
    html = TEMPLATE.replace('__DATA__', payload)
    html = html.replace('__TOP100__', build_top100_section())
    out1 = ROOT.parent / 'qiming.html'
    out2 = ROOT.parent / '十二典撷名-王姓男孩名字精选.html'
    for out in (out1, out2):
        out.write_text(html, encoding='utf-8')
    print(f'生成 {out1} 与 {out2}（{len(html):,} 字符，{len(data)} 名）')


TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>十二典撷名 · 王姓男孩名字精选</title>
<style>
:root{
  --surf:#fcfcfb; --page:#f9f9f7; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
  --line:#e1e0d9; --jiang:#C23B2E; --gold:#C79A2B;
  --tai:#2d8f5f; --warn:#c07a1a; --bad:#b3543f;
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
.controls{position:sticky;top:0;z-index:20;background:linear-gradient(var(--page) 82%,transparent);
  padding:12px 0 10px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
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
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
  gap:14px;margin-top:8px}
.card{background:var(--surf);border:1px solid var(--line);border-radius:14px;
  padding:16px 18px 13px;cursor:pointer;position:relative;
  transition:box-shadow .18s,transform .18s;border-top:3px solid var(--bk)}
.card:hover{box-shadow:0 6px 22px rgba(20,20,10,.08);transform:translateY(-2px)}
.card .top{display:flex;align-items:baseline;gap:10px;margin-bottom:2px}
.card .nm{font-size:25px;font-weight:700;letter-spacing:.1em;
  font-family:"Songti SC","STSong","SimSun",serif}
.card .badge{margin-left:auto;font-size:13px;font-weight:700;padding:2px 9px;
  border-radius:7px;font-variant-numeric:tabular-nums;white-space:nowrap}
.b-tai{background:#e7f4ec;color:#217a4a} .b-ok{background:#eef1e7;color:#6a7a35}
.b-warn{background:#faf0dd;color:#a3680a} .b-bad{background:#f8e7e2;color:#a33f2a}
.card .src{font-size:12.5px;color:var(--muted);margin:0 0 7px}
.card .src .bk{color:var(--bk);font-weight:600}
.card .quote{font-size:13.5px;color:var(--ink2);margin:0 0 7px;padding-left:10px;
  border-left:2px solid var(--line)}
.card .mean{font-size:13.5px;color:var(--ink)}
.card .pick{font-size:12.5px;color:var(--muted);margin-top:3px}
.card .flag{position:absolute;top:10px;right:12px;font-size:11px;color:var(--warn);
  background:#faf0dd;border-radius:6px;padding:1px 7px;display:none}
.card.has-flag .flag{display:inline}
.card .detail{display:none;margin-top:11px;padding-top:10px;border-top:1px dashed var(--line);
  font-size:12.5px;color:var(--ink2)}
.card.open .detail{display:block}
.wg{display:grid;grid-template-columns:repeat(5,1fr);gap:5px;margin-bottom:6px}
.wg div{background:var(--page);border-radius:7px;padding:4px 2px;text-align:center}
.wg .k{font-size:10.5px;color:var(--muted);display:block}
.wg .v{font-size:13px;font-variant-numeric:tabular-nums}
.wg .v.em{font-weight:700;color:var(--tai)}
.wg .v.xn{font-weight:700;color:var(--bad)}
.wg .v.fq{color:var(--warn)}
.dl{display:flex;flex-wrap:wrap;gap:4px 14px}
.dl span b{color:var(--ink)}
.empty{color:var(--muted);text-align:center;padding:60px 0;font-size:14px}
/* ── 综合榜 · 前100 ── */
.topsec{margin:22px 0 4px;border:1px solid var(--line);border-radius:16px;
  background:var(--surf);padding:18px 20px 12px}
.topsec h2{margin:0 0 6px;font-size:20px;letter-spacing:.1em;text-wrap:balance;
  font-family:"Songti SC","STSong","SimSun",serif}
.topsec .tnote{font-size:12.5px;color:var(--muted);margin:0 0 12px;line-height:1.9;text-wrap:pretty}
.topsec .tnote b{color:var(--ink2)}
.t100{width:100%;border-collapse:collapse;font-size:13.5px}
.t100 th{text-align:left;font-size:11.5px;color:var(--muted);font-weight:600;
  border-bottom:1px solid var(--line);padding:4px 8px 6px;white-space:nowrap}
.t100 th.rk{text-align:right}
.t100 td{padding:5px 8px;border-bottom:1px dashed var(--line);vertical-align:top}
.t100 tr:last-child td{border-bottom:none}
.t100 .rk{font-variant-numeric:tabular-nums;color:var(--muted);width:40px;text-align:right}
.t100 tr:nth-child(-n+3) .rk{color:var(--jiang);font-weight:700}
.t100 .nm{font-weight:700;letter-spacing:.06em;white-space:nowrap;
  font-family:"Songti SC","STSong","SimSun",serif;font-size:15px}
.t100 .badge{font-size:12px;padding:1px 8px}
.t100 .nt{color:var(--ink2);font-size:12.5px;text-wrap:pretty}
.t100 .src{display:inline-block;font-size:11px;border-radius:999px;padding:1px 8px;
  background:var(--page);border:1px solid var(--line);color:var(--ink2);white-space:nowrap}
.t100 .src.mst{background:#fdf6e3;border-color:#e3cf9b;color:#8a6d1f;font-weight:600}
.star{color:var(--gold);font-weight:700}
.girl{font-size:10.5px;color:#8c4a5c;background:#fdf0f3;border:1px solid #e7b9c4;
  border-radius:999px;padding:0 5px;margin-left:4px;vertical-align:1px}
.masterline{font-size:12.5px;color:var(--ink2);margin:10px 0 0;padding-top:9px;
  border-top:1px solid var(--line);line-height:1.9}
.masterline b{color:var(--jiang)}
.divider{display:flex;align-items:center;gap:12px;margin:24px 0 0;color:var(--muted);
  font-size:12.5px;letter-spacing:.05em}
.divider::before,.divider::after{content:"";flex:1;height:1px;background:var(--line)}
@media (max-width:560px){
  .t100 .ntcell{display:none}
  .topsec{padding:14px 12px 10px}
}
footer{margin-top:46px;padding-top:18px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--muted);line-height:1.9}
footer b{color:var(--ink2)}
@media (max-width:560px){
  .cards{grid-template-columns:1fr}
  .controls{gap:6px}
  input[type=search]{width:104px}
}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>十二典撷名<span class="seal">王</span></h1>
  <p class="sub">王姓男孩名字精选 · 取自 <b>抱朴子 · 道德经 · 论语 · 周易 · 诗经 · 古文观止 · 礼记 · 左传 · 尚书 · 大学 · 中庸 · 中药本草</b> · 出处逐字可考</p>
  <div class="stats" id="stats"></div>
</header>

__TOP100__

<div class="controls">
  <div class="tabs" id="tabs"></div>
  <div class="gap"></div>
  <input type="search" id="q" placeholder="搜名字/用字…">
  <select id="tier">
    <option value="">全部档位</option>
    <option value="全绿">全绿</option>
    <option value="一⚠️">一⚠️</option>
    <option value="多⚠️">多⚠️</option>
    <option value="慎用">慎用</option>
  </select>
  <select id="sort">
    <option value="score">评分 高→低</option>
    <option value="stroke">笔画 少→多</option>
    <option value="book">按书目序</option>
  </select>
</div>

<div class="cards" id="cards"></div>
<div class="empty" id="empty" style="display:none">没有符合条件的名字</div>

<footer>
  <b>评分口径</b>：五格数理（天/人/地/外/总）+ 三才 + 音形义，与家庭候选池既有标准一致；音形义含「经典出处」加分，本批全部具备明文出处。<br>
  <b>档位</b>：全绿 = 五格无凶、无分歧；一⚠️ = 一格分歧或一凶；多⚠️ = 两凶；慎用 = 三凶及以上。<br>
  <b>☆ 字根提示</b>：30 个名字含生肖命理忌用字根（氵/冫/忄/心部等，如慎/怀/温/恭/惠），出处与字义俱佳，保留待酌——待宝宝出生后结合八字再定去留。中药本草项个别用字（泉/游/沉）沿用上轮宽松口径。<br>
  <b>出处核验</b>：全部 534 条引文均已逐字回查原典语料（《抱朴子》据正统道藏太清部本；诸经诸子据通行本电子文本；中药据《神农本草经》《名医别录》《本草纲目》），未逐字命中者不收录。<br>
  <b>大学中庸</b>：两篇合计不足七千字，合并精选 50 名，质量不注水。
</footer>
</div>

<script>
const DATA = __DATA__;
const GROUPS = [
  ["道德经", ["道德经"], "#5B7C99"],
  ["论语", ["论语"], "#C23B2E"],
  ["周易", ["周易"], "#8A6D3B"],
  ["诗经", ["诗经"], "#4A7C59"],
  ["抱朴子·内篇", ["抱朴子内篇"], "#6F5EA8"],
  ["抱朴子·外篇", ["抱朴子外篇"], "#6F5EA8"],
  ["古文观止", ["古文观止"], "#2F5D8A"],
  ["礼记", ["礼记"], "#C87A3F"],
  ["左传", ["左传"], "#7C6BA0"],
  ["尚书", ["尚书"], "#AC4D3C"],
  ["大学中庸", ["大学", "中庸"], "#9A8B3B"],
  ["中药本草", ["神农本草经", "名医别录", "本草纲目"], "#3E7C5E"]
];
const TIER_CLS = {"全绿":"b-tai","一⚠️":"b-ok","多⚠️":"b-warn","慎用":"b-bad"};
function groupOf(book){ return GROUPS.find(g => g[1].includes(book)); }
const R = Object.entries(DATA).map(([name,d])=>({name,...d}));
let curGroup = "全部", curTier = "", curSort = "score", curQ = "";

(function(){
  const g = R.filter(r=>r.tier==="全绿").length;
  const w1 = R.filter(r=>r.tier==="一⚠️").length;
  const w2 = R.filter(r=>r.tier==="多⚠️").length;
  const b = R.filter(r=>r.tier==="慎用").length;
  const top = Math.max(...R.map(r=>r.score));
  document.getElementById("stats").innerHTML =
    `<div class="stat"><b>${R.length}</b>名 · 十二项</div>`+
    `<div class="stat g"><b>${g}</b>全绿</div>`+
    `<div class="stat"><b>${w1}</b>一⚠️</div>`+
    `<div class="stat w"><b>${w2}</b>多⚠️</div>`+
    `<div class="stat r"><b>${b}</b>慎用</div>`+
    `<div class="stat"><b>${top}</b>最高分</div>`;
})();

(function(){
  const tabs = document.getElementById("tabs");
  const mk = (key,label,n)=>{
    const el = document.createElement("button");
    el.className = "tab"+(key===curGroup?" on":"");
    el.dataset.key = key;
    el.innerHTML = label+`<span class="n">${n}</span>`;
    el.onclick = ()=>{curGroup=key; syncTabs(); render();};
    return el;
  };
  tabs.appendChild(mk("全部","全部",R.length));
  GROUPS.forEach(g=>{
    const n = R.filter(r=>g[1].includes(r.source_book)).length;
    if(n) tabs.appendChild(mk(g[0], g[0], n));
  });
})();
function syncTabs(){
  document.querySelectorAll(".tab").forEach(el=>{
    el.classList.toggle("on", el.dataset.key === curGroup);
  });
}

function wgCell(k,v){
  const cls = /大吉/.test(v[1]) ? "em" : v[1]==="凶" ? "xn" : v[1]==="分歧⚠️" ? "fq" : "";
  const num = v[0].split(" ")[0];
  const nm = v[0].split(" ")[1]||"";
  return `<div><span class="k">${k}</span><span class="v ${cls}" title="${nm} ${v[1]}">${num}</span></div>`;
}

function render(){
  let list = R.slice();
  if(curGroup!=="全部"){
    const g = GROUPS.find(x=>x[0]===curGroup);
    if(g) list = list.filter(r=>g[1].includes(r.source_book));
  }
  if(curTier) list = list.filter(r=>r.tier===curTier);
  if(curQ) list = list.filter(r=>r.name.includes(curQ)||
    (r.source_quote||"").includes(curQ)|| (r.meaning||"").includes(curQ));
  if(curSort==="score") list.sort((a,b)=>b.score-a.score);
  if(curSort==="stroke") list.sort((a,b)=>
    a.strokes.reduce((x,y)=>x+y,0)-b.strokes.reduce((x,y)=>x+y,0));
  if(curSort==="book") list.sort((a,b)=>{
    const ga = GROUPS.findIndex(g=>g[1].includes(a.source_book));
    const gb = GROUPS.findIndex(g=>g[1].includes(b.source_book));
    return ga-gb;
  });

  const box = document.getElementById("cards");
  document.getElementById("empty").style.display = list.length? "none":"block";
  box.innerHTML = list.map(r=>{
    const grp = groupOf(r.source_book);
    const col = grp ? grp[2] : "#888";
    const st = (r.strokes||[]).join("+");
    return `<div class="card ${r.flag?"has-flag":""}" style="--bk:${col}" onclick="this.classList.toggle('open')">
      <span class="flag">☆ ${r.flag}</span>
      <div class="top">
        <span class="nm">${r.name}</span>
        <span class="badge ${TIER_CLS[r.tier]||""}">${r.score} · ${r.tier}</span>
      </div>
      <p class="src"><span class="bk">${r.source_book} · ${r.source_loc}</span></p>
      <p class="quote">「${r.source_quote}」</p>
      <p class="mean">${r.meaning||""}</p>
      <p class="pick">${r.pick_reason||""}</p>
      <div class="detail">
        <div class="wg">
          ${wgCell("天",r.wuge["天"])}${wgCell("人",r.wuge["人"])}${wgCell("地",r.wuge["地"])}${wgCell("外",r.wuge["外"])}${wgCell("总",r.wuge["总"])}
        </div>
        <div class="dl">
          <span>三才 <b>${r.sancai}</b></span>
          <span>笔画 <b>${st}</b></span>
          <span>三字五行 <b>${r.wuxing.chars}</b></span>
          <span>音调 <b>${(r.tones||"").split("").join(" ")}</b></span>
        </div>
      </div>
    </div>`;
  }).join("");
}

document.getElementById("tier").onchange = e=>{curTier=e.target.value; render();};
document.getElementById("sort").onchange = e=>{curSort=e.target.value; render();};
document.getElementById("q").oninput = e=>{curQ=e.target.value.trim(); render();};
render();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    main()
