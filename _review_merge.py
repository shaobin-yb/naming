# -*- coding: utf-8 -*-
"""合并四维重估:liki字库 + 网红扫描 + 人工气质评审 → _review_final.json

四维各 25 分:
A 时代穿透: core -12/sec -5/mid -2/old -3/age -2 每字;经典或低使用率好字 +1(封顶+3);起点 25
B 日常可用: freq common 12.5 / standard 8 / rare 3 / 未收录 5(两字平均);字≥20画 -3;总笔≥30 -2
C 音律顺口: 起评 20;末字 4声+3、1/2声+2;两字相邻同调 -2;多音字 -3/字(LIKI pinyin 逗号)
D 意象气质: 人工评审 q4
"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

top = json.load(open(f"{BASE}/top100_data.json", encoding="utf-8"))
liki = json.load(open(f"{BASE}/_liki_chars.json", encoding="utf-8"))
scan = {o["name"]: o for o in json.load(open(f"{BASE}/_review_scan.json", encoding="utf-8"))}
mine = {o["name"]: o for o in json.load(open(f"{BASE}/_review_mine.json", encoding="utf-8"))["items"]}

FREQ_SCORE = {"common": 12.5, "standard": 8, "rare": 3}
DUOYIN_QX = set("重乐和行饮")  # 台账既有口径(另用 liki pinyin 逗号判多音,更全)

def dim_a(name):
    s = scan.get(name, {})
    tags = " ".join(s.get("tags", []))
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
    given = name[1:]
    sc = []
    rare_chars = []
    for ch in given:
        info = liki.get(ch)
        if info is None or info.get("unlisted"):
            sc.append(3); rare_chars.append(f"{ch}未收录")
        else:
            f = info.get("frequency", "standard")
            sc.append(FREQ_SCORE.get(f, 8))
            if f == "rare":
                rare_chars.append(f"{ch}生僻")
    B = sum(sc) / len(sc)
    total_stroke = 0
    heavy = []
    for ch in given:
        info = liki.get(ch) or {}
        st = info.get("stroke") or 0
        total_stroke += st
        if st >= 20: heavy.append(f"{ch}{st}画")
    if heavy: B -= 3
    if total_stroke >= 30: B -= 2
    return max(0.0, min(25.0, B)), rare_chars + heavy

def dim_c(name):
    C = 20.0
    tones = []
    for ch in name:  # 含姓王
        if ch == "王":
            tones.append(2)  # 王=阳平二声,不入 liki 查询集
            continue
        info = liki.get(ch) or {}
        tones.append(info.get("tone"))
    given_tones = tones[1:]
    duoyin = []
    for ch in name[1:]:
        info = liki.get(ch) or {}
        py = info.get("pinyin", "") or ""
        if "," in py or ch in DUOYIN_QX:
            C -= 3; duoyin.append(ch)
    if len(given_tones) == 2 and given_tones[0] == given_tones[1]:
        C -= 2
    last = given_tones[-1] if given_tones else None
    if last == 4: C += 3
    elif last in (1, 2): C += 2
    return max(0.0, min(25.0, C)), duoyin, tones

rows = []
for it in top["list"]:
    name = it["name"]
    A, a_hits = dim_a(name)
    B, b_marks = dim_b(name)
    C, duoyin, tones = dim_c(name)
    D = (mine.get(name) or {}).get("q4", 18)
    total = round(A + B + C + D, 1)
    rows.append({
        "rank0": it["rank"], "name": name, "score0": it["score"], "src": it.get("src", ""),
        "A": round(A, 1), "B": round(B, 1), "C": round(C, 1), "D": D,
        "total": total,
        "qx": (mine.get(name) or {}).get("qx", ""),
        "note": (mine.get(name) or {}).get("note", ""),
        "a_hits": a_hits, "b_marks": b_marks, "duoyin": duoyin,
        "tones": tones,
    })

# 大师未入 4 名
for r in (121, 139, 144, 170):
    pass  # 大师 4 名不在 top100 list 里,单独补
MASTER_EXTRA = ["王啸风", "王决云", "王枕风", "王闻雨"]
for mn in MASTER_EXTRA:
    A, a_hits = dim_a(mn)
    B, b_marks = dim_b(mn)
    C, duoyin, tones = dim_c(mn)
    D = (mine.get(mn) or {}).get("q4", 18)
    rows.append({
        "rank0": None, "name": mn, "score0": None, "src": "大师提名(未入前100)",
        "A": round(A, 1), "B": round(B, 1), "C": round(C, 1), "D": D,
        "total": round(A + B + C + D, 1),
        "qx": (mine.get(mn) or {}).get("qx", ""),
        "note": (mine.get(mn) or {}).get("note", ""),
        "a_hits": a_hits, "b_marks": b_marks, "duoyin": duoyin, "tones": tones,
    })

# 新名次(按四维总分,top100 内排;大师4名单独展示)
ranked = sorted([r for r in rows if r["rank0"]], key=lambda r: -r["total"])
for i, r in enumerate(ranked, 1):
    r["rank1"] = i
for r in rows:
    if r["rank0"] is None:
        r["rank1"] = None

out = {"meta": {"date": "2026-10-13", "n": len(rows),
                "rules": "A时代穿透25 B日常可用25 C音律25 D意象气质25"},
       "rows": rows}
json.dump(out, open(f"{BASE}/_review_final.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"完成 {len(rows)} 名")
print("\n=== 四维总分 Top15 ===")
for r in ranked[:15]:
    delta = (r["rank0"] - r["rank1"]) if r["rank0"] else 0
    print(f"新#{r['rank1']:>3} 原#{r['rank0']:>3} {r['name']} {r['total']} (A{r['A']} B{r['B']} C{r['C']} D{r['D']}) qx={r['qx']}")
print("\n=== 上升最多(新# - 原# <= -10) ===")
for r in sorted(ranked, key=lambda x: x["rank1"] - x["rank0"]):
    d = r["rank1"] - r["rank0"]
    if d <= -10:
        print(f"{r['name']} 原#{r['rank0']} -> 新#{r['rank1']} ({d:+d})")
print("\n=== 下降最多(新# - 原# >= 10) ===")
for r in sorted(ranked, key=lambda x: x["rank1"] - x["rank0"], reverse=True):
    d = r["rank1"] - r["rank0"]
    if d >= 10:
        print(f"{r['name']} 原#{r['rank0']} -> 新#{r['rank1']} ({d:+d})")
