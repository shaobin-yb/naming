# -*- coding: utf-8 -*-
"""对照 Seiya skill 反网红字库扫描 Top100+大师10名。"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

CORE_2020S = set("梓涵轩睿沐晨辰熙佳")          # 2020s 核心烂大街
SEC_2020S = set("子宇泽悦然可昕萱瑶桐")          # 2020s 次级标签
MID_2010S = set("嘉浩思雨")                      # 2010s
OLD_2000S = set("婷倩颖雪静健伟强龙")            # 2000s
AGE_8090S = set("建伟强军丽芳娟慧国华文卫忠志玉淑桂英霞")  # 80-90s
DUOYIN = set("重乐和行饮")                       # 多音字(和/行/乐/重/饮 —— 台账已知口径)
CLASSIC = set("安宁和明清远之若知行谦逊敬慎敏博毅勤")  # 跨时代经典(男女或男孩向)
RARE_GOOD = set("砚桐栎桑楷檀楸砺砾磬磐翊翎翙翯旸晙旻旰晗泠泫淼潋滟")  # 低使用率好字

d = json.load(open(f"{BASE}/top100_data.json", encoding="utf-8"))
lst = d["list"]
MASTER_EXTRA = ["王啸风", "王决云", "王枕风", "王闻雨"]

def scan(name):
    given = name[1:]
    hit = {"core": [], "sec": [], "mid": [], "old": [], "age": [],
           "duoyin": [], "classic": [], "rare_good": []}
    for ch in given:
        if ch in CORE_2020S: hit["core"].append(ch)
        if ch in SEC_2020S: hit["sec"].append(ch)
        if ch in MID_2010S: hit["mid"].append(ch)
        if ch in OLD_2000S: hit["old"].append(ch)
        if ch in AGE_8090S: hit["age"].append(ch)
        if ch in DUOYIN: hit["duoyin"].append(ch)
        if ch in CLASSIC: hit["classic"].append(ch)
        if ch in RARE_GOOD: hit["rare_good"].append(ch)
    return hit

out = []
for it in lst:
    h = scan(it["name"])
    tags = []
    if h["core"]: tags.append(f"核心网红字×{len(h['core'])}({''.join(h['core'])})")
    if h["sec"]: tags.append(f"次级标签({''.join(h['sec'])})")
    if h["mid"]: tags.append(f"2010s字({''.join(h['mid'])})")
    if h["old"]: tags.append(f"2000s字({''.join(h['old'])})")
    if h["age"]: tags.append(f"80/90s字({''.join(h['age'])})")
    if h["duoyin"]: tags.append(f"多音字({''.join(h['duoyin'])})")
    if h["classic"]: tags.append(f"经典字+({''.join(h['classic'])})")
    if h["rare_good"]: tags.append(f"低使用率好字({''.join(h['rare_good'])})")
    out.append({"rank": it["rank"], "name": it["name"], "score": it["score"], "tags": tags})

print("=== 命中网红/时代标签/多音的字 ===")
any_hit = False
for o in out:
    bad = [t for t in o["tags"] if "网红" in t or "标签" in t or "s字" in t or "多音" in t]
    if bad:
        any_hit = True
        print(f"#{o['rank']:>3} {o['name']} {o['score']} | {', '.join(bad)}")
if not any_hit:
    print("(无)")

print()
print("=== 命中经典字/低使用率好字 ===")
for o in out:
    good = [t for t in o["tags"] if "经典" in t or "低使用率" in t]
    if good:
        print(f"#{o['rank']:>3} {o['name']} | {', '.join(good)}")

json.dump(out, open(f"{BASE}/_review_scan.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n存 _review_scan.json,共", len(out), "名")
