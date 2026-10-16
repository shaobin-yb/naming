# -*- coding: utf-8 -*-
"""轻灵少年气 30 候选查重:档案池+十二典+综合+占用653+池内627。"""
import glob, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

occupied = {}
def add(name, src):
    occupied.setdefault(name, []).append(src)

src = open(f"{BASE}/score_all.py", encoding="utf-8").read()
for m in re.findall(r"'王[^']{1,2}'", src):
    add(m.strip("'"), "档案池")
for f in glob.glob(f"{BASE}/classics/candidates_*.json"):
    for it in json.load(open(f, encoding="utf-8")):
        add(it["name"], "十二典")
d = json.load(open(f"{BASE}/top100_data.json", encoding="utf-8"))
for it in d["list"]:
    add(it["name"], "Top100")
for k in d.get("entries", {}):
    add(k, "综合93")
for line in open(f"{BASE}/classics/occupied_v2.txt", encoding="utf-8"):
    ln = line.strip()
    if ln:
        add(ln, "占用653")
# 池内 627(同一集合的补充确认)
pool = json.load(open(f"{BASE}/_review2_pool.json", encoding="utf-8"))
for x in pool["names"]:
    add(x["name"], "池627")

print("全量名字集合:", len(occupied))
cands = ["王既白", "王晴川", "王轻舟", "王振鹭", "王南风", "王春涧", "王清和",
         "王远帆", "王云帆", "王一苇", "王景明", "王鹤鸣", "王听雨", "王春山",
         "王青崖", "王听松", "王听泉", "王咏归", "王鹿鸣", "王清越", "王朗川",
         "王弈舟", "王澄川", "王砚秋", "王沙鸥", "王初航", "王见山", "王溪山",
         "王青野", "王步青"]
free, hit = [], []
for c in cands:
    if occupied.get(c):
        hit.append((c, sorted(set(occupied[c]))))
    else:
        free.append(c)
print(f"\n占用: {len(hit)} 个")
for c, s in hit:
    print(f"  ✗ {c}: {'/'.join(s)}")
print(f"\n可用 {len(free)} 个: {' '.join(free)}")
open(f"{BASE}/_review2_cands_free.txt", "w", encoding="utf-8").write("\n".join(free))
