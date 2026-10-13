# -*- coding: utf-8 -*-
"""三源合并排名：档案（173）+ 榜单（75）+ 大师提名（10）→ 前 100。

数据源：
- 档案：naming/score_data.js（score_all.py 产出；大师 10 名若尚未落盘则本脚本
  用同一公式自算兜底——两窗口并行期间不阻塞，落盘后重跑比对）
- 榜单：naming/board_scores.json（board_score.py 产出，口径=十二典批次）
- 分组：解析 score_all.py 的 NAMES 段落注释（家族池/传承向/五劫向/中药向/
  兄弟对仗/老板提名/大师提名/女孩名）
输出：naming/top100_data.json
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import score_all as SA
import board_score as B

MASTER = ['王瞰云', '王御纬', '王撼岳', '王啸风', '王决云',
          '王挹江', '王枕风', '王浸阳', '王闻雨', '王鹤如']

# 大师名出处短注（来自核实脚本 _verify_quotes.py 的引文清单；index.html 落盘后优先用其条目）
MASTER_NOTE = {
    '王瞰云': '「飘然乘云气，俯首视世寰」白玉蟾《少年行》',
    '王御纬': '「笔蘸天河，手扪象纬，笑傲风云」周权《沁园春》',
    '王撼岳': '「列缺霹雳，丘峦崩摧」李白《梦游天姥吟留别》',
    '王啸风': '「长啸万里风，扫清胸中忧」李白《留别贾舍人至》',
    '王决云': '「挥剑决浮云，诸侯尽西来」李白《古风》',
    '王挹江': '「尽挹西江，细斟北斗」张孝祥《念奴娇·过洞庭》',
    '王枕风': '「清风一枕南窗卧」于谦《初度》',
    '王浸阳': '「浪浸斜阳，千里溶溶」柳永《雪梅香》',
    '王闻雨': '「日照虹霓似，天清风雨闻」张九龄《湖口望庐山瀑布泉》',
    '王鹤如': '「散幽经以验物，伟胎化之仙禽」鲍照《舞鹤赋》',
}

SRC_NAME = {'shijing': '诗经', 'chuci': '楚辞', 'tangshi': '唐诗',
            'songci': '宋词', 'songshi': '宋诗', 'other': '诸子典籍'}

TIER_RANK = {'全绿': 0, '一⚠️': 1, '多⚠️': 2, '慎用': 3}


def parse_groups():
    """解析 score_all.py 的 NAMES 段落 → {name: 组名}。"""
    src = (ROOT / 'score_all.py').read_text(encoding='utf-8')
    i = src.index('NAMES = [')
    j = src.index('\n]', i)
    block = src[i:j]
    groups, cur = {}, '家族池'
    for line in block.splitlines():
        t = line.strip()
        if t.startswith('#'):
            # 只认"大组注释"（含关键词的才切换分组）；A/B/C、清雅型、接点等子注释不动 cur
            if '已定名' in t: cur = '家族池'
            elif '老板提名 2026-10-13' in t: cur = '大师提名'
            elif '老板提名 2026-10-12' in t: cur = '老板提名'
            elif '传承向' in t: cur = '传承向'
            elif '五劫向' in t: cur = '五劫向'
            elif '中药名向' in t: cur = '中药向'
            elif '兄弟对仗' in t: cur = '兄弟对仗'
            elif '女孩名' in t: cur = '女孩名'
        for nm in re.findall(r"'(王[一-鿿]{1,3})'", line):
            groups[nm] = cur
    return groups


def main():
    # ── 档案 ──
    t = (ROOT / 'score_data.js').read_text(encoding='utf-8')
    archive = json.loads(t[t.index('{'):t.rindex('}') + 1])
    groups = parse_groups()

    missing_master = [n for n in MASTER if n not in archive]
    fallback_used = False
    if missing_master:
        # 兜底：用同一公式自算（score_all 尚未重跑时）。字符集无差异，
        # 结果应与对方落盘一致；其 score_data.js 更新后重跑本脚本比对。
        fallback_used = True
        print(f'⚠️ score_data.js 尚无 {len(missing_master)} 个大师名，启用同公式兜底自算')
        strokes = B.load_all_strokes()
        chars = set(''.join(MASTER)) | {'王'}
        todo = sorted(c for c in chars if c not in strokes)
        if todo:
            print(f'  补抓大师名字符笔画 {len(todo)} 个：{"".join(todo)}')
            got, fails = B.fetch_missing(todo)
            strokes.update(got)
            if fails:
                sys.exit(f'❌ 笔画抓取失败: {"".join(fails)}')
            p = B.CLS_DIR / 'strokes_cache.json'
            cache = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
            cache.update(got)
            p.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding='utf-8')
        for nm in missing_master:
            archive[nm] = B.score_name(nm, strokes)

    # ── 榜单 ──
    board = {x['n']: x for x in json.loads((ROOT / 'board_names.json').read_text(encoding='utf-8'))}
    bscores = json.loads((ROOT / 'board_scores.json').read_text(encoding='utf-8'))

    # ── 注释 ──
    notes = {}
    np_ = ROOT / 'archive_notes.json'
    if np_.exists():
        notes = json.loads(np_.read_text(encoding='utf-8'))

    # ── 合并 ──
    rows = []
    for nm, rec in archive.items():
        g = groups.get(nm, '家族池')
        src = '大师提名' if g == '大师提名' else f'档案·{g}'
        note = ''
        if nm in MASTER:
            note = (notes.get(nm, {}).get('line') or MASTER_NOTE.get(nm, ''))
        else:
            note = notes.get(nm, {}).get('line', '')
        rows.append({'n': nm, 'score': rec['score'], 'tier': rec['tier'],
                     'src': src, 'note': note,
                     'f': '女' if g == '女孩名' else ''})
    for n0, x in board.items():
        nm = '王' + n0
        rec = bscores[nm]
        rows.append({'n': nm, 'score': rec['score'], 'tier': rec['tier'],
                     'src': f'榜单·{SRC_NAME.get(x["s"], x["s"])}',
                     'note': '「' + x['q'] + '」',
                     'f': '女' if x.get('g') == '女' else ''})

    assert len(rows) == len(archive) + len(board), '合并数量异常'
    dup = len(rows) - len({r['n'] for r in rows})
    assert dup == 0, f'跨源重名 {dup} 个'
    print(f'合并池 {len(rows)} 名（档案 {len(archive)} + 榜单 {len(board)}）')

    def stotal(r):
        rec = archive.get(r['n']) or bscores.get(r['n'])
        return sum(rec.get('strokes', [0])) if rec else 0

    rows.sort(key=lambda r: (-r['score'], TIER_RANK.get(r['tier'], 9), stotal(r), r['n']))

    for i, r in enumerate(rows, 1):
        r['rank'] = i
    top = rows[:100]

    master_ranks = [{'n': r['n'], 'rank': r['rank'], 'score': r['score']}
                    for r in rows if r['src'] == '大师提名']
    # 保持 MASTER 原顺序输出
    order = {m: i for i, m in enumerate(MASTER)}
    master_ranks.sort(key=lambda x: order[x['n']])

    date = '2026-10-13'
    payload = {
        'meta': {
            'date': date,
            'pool': len(rows),
            'archive_n': len(archive),
            'board_n': len(board),
            'master_n': len(MASTER),
            'cut': len(top),
            'master_ranks': master_ranks,
            'fallback': fallback_used,
        },
        'list': [{'rank': r['rank'], 'name': r['n'], 'score': r['score'],
                  'tier': r['tier'], 'src': r['src'], 'note': r['note'],
                  'f': r['f']} for r in top],
    }
    (ROOT / 'top100_data.json').write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'✅ 写入 top100_data.json（前100 / 池 {len(rows)}）')
    print('\n前20：')
    for r in top[:20]:
        mark = '★' if r['src'] == '大师提名' else ' '
        print(f'  {r["rank"]:>3}. {mark}{r["n"]} {r["score"]} {r["tier"]:<4} {r["src"]}  {r["note"][:30]}')
    print('\n大师提名位次：')
    for m in master_ranks:
        flag = '入围' if m['rank'] <= 100 else '未入前100'
        print(f'  {m["n"]} #{m["rank"]} ({m["score"]}) {flag}')


if __name__ == '__main__':
    main()
