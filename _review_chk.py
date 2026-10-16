# -*- coding: utf-8 -*-
"""新候选查重:对 档案池(score_all.py NAMES)+ 十二典 534 + 综合新93 + occupied 653 全量查重。"""
import glob, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = "D:/cloude code/naming"

occupied = {}
def add(name, src):
    occupied.setdefault(name, []).append(src)

# 1) 档案池 + 全量 NAMES
src = open(f"{BASE}/score_all.py", encoding="utf-8").read()
for m in re.findall(r"'王[^']{1,2}'", src):
    add(m.strip("'"), "档案池")
# 2) 十二典 534
for f in glob.glob(f"{BASE}/classics/candidates_*.json"):
    for it in json.load(open(f, encoding="utf-8")):
        add(it["name"], "十二典")
# 3) 综合榜新93
d = json.load(open(f"{BASE}/top100_data.json", encoding="utf-8"))
for it in d["list"]:
    add(it["name"], "Top100")
ent = d.get("entries", {})
if isinstance(ent, dict):
    for k in ent:
        add(k, "综合新93")
elif isinstance(ent, list):
    for it in ent:
        add(it.get("name", "?"), "综合新93")
# 4) 占用名单
for line in open(f"{BASE}/classics/occupied_v2.txt", encoding="utf-8"):
    ln = line.strip()
    if ln:
        add(ln, "占用653")

print("全量名字集合:", len(occupied))

cands = ["王清越", "王朗川", "王弈舟", "王砚秋", "王南乔", "王鹿鸣", "王轻舟",
         "王南风", "王见山", "王青崖", "王澄川", "王庭柯", "王岱川", "王漱风",
         "王映川", "王松月", "王溪月", "王鸣川", "王鹤川", "王晚舟"]
print("\n=== 查重结果 ===")
free = []
for c in cands:
    hit = occupied.get(c)
    if hit:
        print(f"✗ {c} 已被占: {'/'.join(sorted(set(hit)))}")
    else:
        print(f"✓ {c} 未被占用")
        free.append(c)
print("\n可用的:", " ".join(free))
