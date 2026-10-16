# -*- coding: utf-8 -*-
"""627 全量四维合并(快通道版):
B 字频 ← liki freqpool(5池全表,口径与 char 接口一致 191/191);
B 笔画 ← qiming 康熙笔画; C 声调/多音 ← pypinyin(普通话常用读音);
A ← 网红扫描; D ← 人工评审总表。
"""
import json, sys
from pypinyin import pinyin as py, Style

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

pool = json.load(open(f"{BASE}/_review2_pool.json", encoding="utf-8"))
freq = json.load(open(f"{BASE}/_liki_freqpool.json", encoding="utf-8"))
strokes_data = json.load(open(f"{BASE}/_review2_strokes.json", encoding="utf-8"))
scan = {o["name"]: o for o in json.load(open(f"{BASE}/_review2_scan.json", encoding="utf-8"))}
dmap = json.load(open(f"{BASE}/_review2_dmap.json", encoding="utf-8"))
scores = json.load(open(f"{BASE}/_review2_scores.json", encoding="utf-8"))

FREQ_SCORE = {"common": 12.5, "standard": 8, "rare": 3}
DUOYIN_QX = set("重乐和行饮") | set("行乐参朴柏朝单解盖查仇尉区翟缪兴长种相宁华")

def dim_a(name):
    s = scan.get(name, {})
    A = 25.0
    hits = []
    for ch in name[1:]:
        if ch in "梓涵轩睿沐晨辰熙佳": A -= 12; hits.append(f"网红核心·{ch}")
        elif ch in "子宇泽悦然可昕萱瑶桐": A -= 5; hits.append(f"次级标签·{ch}")
        if ch in "嘉浩思雨": A -= 2; hits.append(f"2010s·{ch}")
        if ch in "婷倩颖雪静健伟强龙": A -= 3; hits.append(f"2000s·{ch}")
        if ch in "建伟强军丽芳娟慧国华文卫忠志玉淑桂英霞": A -= 2; hits.append(f"年代字·{ch}")
    cl = [t for t in s.get("tags", []) if "经典字" in t or "低使用率" in t]
    if cl: A = min(25.0, A + min(3, len(cl)))
    return max(0.0, A), hits

def dim_b(name):
    sc, marks = [], []
    for ch in name[1:]:
        f = freq.get(ch)
        if f is None:
            sc.append(8); marks.append(f"{ch}库外")
        else:
            sc.append(FREQ_SCORE.get(f, 8))
            if f == "rare":
                marks.append(f"{ch}生僻")
    B = sum(sc) / len(sc)
    sts = strokes_data.get(name) or []
    total_stroke = sum(sts[1:]) if len(sts) >= 3 else 0
    heavy = []
    for k, ch in enumerate(name[1:]):
        st = sts[1 + k] if len(sts) >= 3 else 0
        if st and st >= 20:
            heavy.append(f"{ch}{st}画")
    if heavy: B -= 3
    if total_stroke >= 30: B -= 2
    return max(0.0, min(25.0, B)), marks + heavy

def tone_of(ch):
    s = py(ch, style=Style.TONE3, strict=False)[0][0]
    if s and s[-1].isdigit():
        return int(s[-1])
    return None

def dim_c(name):
    C = 20.0
    tones = [2]
    for ch in name[1:]:
        tones.append(tone_of(ch))
    gt = tones[1:]
    duoyin = []
    for ch in name[1:]:
        if ch in DUOYIN_QX:
            C -= 3; duoyin.append(ch)
    if len(gt) == 2 and gt[0] is not None and gt[0] == gt[1]:
        C -= 2
    last = gt[-1] if gt else None
    if last == 4: C += 3
    elif last in (1, 2): C += 2
    return max(0.0, min(25.0, C)), duoyin, tones

rows = []
for x in pool["names"]:
    name = x["name"]
    A, a_hits = dim_a(name)
    B, b_marks = dim_b(name)
    C, duoyin, tones = dim_c(name)
    D = dmap.get(name, 18)
    total = round(A + B + C + D, 1)
    o = scores.get(name, {})
    rows.append({
        "name": name, "src": x["src"], "book": x.get("book", ""),
        "score0": o.get("score"), "tier0": o.get("tier"),
        "A": round(A, 1), "B": round(B, 1), "C": round(C, 1), "D": D,
        "total": total,
        "a_hits": a_hits, "b_marks": b_marks, "duoyin": duoyin, "tones": tones,
        "meaning": (x.get("meaning") or "")[:80],
    })

rows.sort(key=lambda r: (-r["total"], -r["D"], -r["B"], r["name"]))  # 同分按意象气质→日常可用→名 稳定排序
for i, r in enumerate(rows, 1):
    r["rank2"] = i
    r["top200"] = i <= 200

out = {"meta": {"date": "2026-10-14", "n": len(rows),
                "note": "四维25分制: A时代穿透 B日常可用(字频=liki全库表/笔画=康熙) C音律(声调=普通话) D意象气质(人工评审)"},
       "rows": rows}
json.dump(out, open(f"{BASE}/_review2_final.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"完成 {len(rows)} 名")
print("\n=== 四维总分 Top24 ===")
for r in rows[:24]:
    print(f"#{r['rank2']:>3} {r['name']} {r['total']} (A{r['A']} B{r['B']} C{r['C']} D{r['D']}) 五格{r['score0']} [{r['book'][:10] or r['src']}]")
print(f"\n第 200 名门槛: #{rows[199]['rank2']} {rows[199]['name']} {rows[199]['total']}")
print(f"第 201 名: #{rows[200]['rank2']} {rows[200]['name']} {rows[200]['total']}")
# 分布
from collections import Counter
c = Counter(r["total"] for r in rows[:200])
print("前200 分数分布:", dict(sorted(c.items(), reverse=True)))
