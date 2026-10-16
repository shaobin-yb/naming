# -*- coding: utf-8 -*-
"""627 全量池的网红字/时代标签扫描 → _review2_scan.json"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

CORE_2020S = set("梓涵轩睿沐晨辰熙佳")
SEC_2020S = set("子宇泽悦然可昕萱瑶桐")
MID_2010S = set("嘉浩思雨")
OLD_2000S = set("婷倩颖雪静健伟强龙")
AGE_8090S = set("建伟强军丽芳娟慧国华文卫忠志玉淑桂英霞")
DUOYIN_QX = set("重乐和行饮")
CLASSIC = set("安宁和明清远之若知行谦逊敬慎敏博毅勤")
RARE_GOOD = set("砚桐栎桑楷檀楸砺砾磬磐翊翎翙翯旸晙旻旰晗泠泫淼潋滟")

pool = json.load(open(f"{BASE}/_review2_pool.json", encoding="utf-8"))
out = []
for it in pool["names"]:
    name = it["name"]
    tags = []
    for ch in name[1:]:
        if ch in CORE_2020S: tags.append(f"网红核心·{ch}")
        elif ch in SEC_2020S: tags.append(f"次级标签·{ch}")
        if ch in MID_2010S: tags.append(f"2010s·{ch}")
        if ch in OLD_2000S: tags.append(f"2000s·{ch}")
        if ch in AGE_8090S: tags.append(f"年代字·{ch}")
        if ch in DUOYIN_QX: tags.append(f"多音(原口径)·{ch}")
        if ch in CLASSIC: tags.append(f"经典字+{ch}")
        if ch in RARE_GOOD: tags.append(f"低使用率好字+{ch}")
    out.append({"name": name, "src": it["src"], "tags": tags})

json.dump(out, open(f"{BASE}/_review2_scan.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

n_hit = sum(1 for o in out if any(("网红" in t) or ("s·" in t.replace("2010s", "s·‌")) or ("2000s" in t) or ("年代" in t) for t in o["tags"]))
print(f"扫描完成 {len(out)} 名;命中网红/年代标签: {n_hit}")
core_hits = [o["name"] for o in out if any("网红核心" in t for t in o["tags"])]
print("命中 2020s 核心字:", " ".join(core_hits) or "(无)")
