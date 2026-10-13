# -*- coding: utf-8 -*-
"""综合榜（第十三个板块）：档案 + 榜单 + 大师提名，男孩向合排前 100。

2026-10-13 老板拍板口径：
- 综合 100 名与「诗经」等书目同级 → 作为 qiming.html 第十三个板块（tab）
- 筛选出的 100 名参与「全部」排名（合入 DATA）
- 老二是男孩 → 剔除女孩名（档案·女孩名 53 + 榜单女 17 = 70 名）

数据源：
- 档案：naming/score_data.js（score_all.py 产出）
- 榜单：naming/board_scores.json（board_score.py 产出，口径=十二典批次）
- 分组：解析 score_all.py 的 NAMES 段落注释
- 注释：naming/archive_notes.json（档案页条目 line/meaning/eggs）
输出：naming/top100_data.json {meta, list, zonghe, entries}
- list：前100（男孩向）排名
- zonghe：100 个名字（供页面 tab 过滤）
- entries：尚不在十二典 534 中的名字 → 完整卡片字段（供合入页面 DATA）
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

# 大师名出处 (引文, 出处) —— 引文取自核实脚本 _verify_quotes.py 清单
MASTER_NOTE = {
    '王瞰云': ('飘然乘云气，俯首视世寰', '白玉蟾《少年行》'),
    '王御纬': ('笔蘸天河，手扪象纬', '周权《沁园春》'),
    '王撼岳': ('列缺霹雳，丘峦崩摧', '李白《梦游天姥吟留别》'),
    '王啸风': ('长啸万里风，扫清胸中忧', '李白《留别贾舍人至》'),
    '王决云': ('挥剑决浮云', '李白《古风》'),
    '王挹江': ('尽挹西江，细斟北斗', '张孝祥《念奴娇·过洞庭》'),
    '王枕风': ('清风一枕南窗卧', '于谦《初度》'),
    '王浸阳': ('浪浸斜阳，千里溶溶', '柳永《雪梅香》'),
    '王闻雨': ('日照虹霓似，天清风雨闻', '张九龄《湖口望庐山瀑布泉》'),
    '王鹤如': ('散幽经以验物，伟胎化之仙禽', '鲍照《舞鹤赋》'),
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
            # 只认"大组注释"；A/B/C、清雅型、接点等子注释不动 cur
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


def tones_of(name):
    from pypinyin import Style, pinyin as tp
    return ''.join(tp(ch, style=Style.TONE3)[0][0][-1] for ch in name)


def main():
    # ── 档案 ──
    t = (ROOT / 'score_data.js').read_text(encoding='utf-8')
    archive = json.loads(t[t.index('{'):t.rindex('}') + 1])
    groups = parse_groups()

    miss = [n for n in MASTER if n not in archive]
    if miss:
        print(f'⚠️ score_data.js 尚无 {len(miss)} 个大师名，启用同公式兜底自算')
        strokes = B.load_all_strokes()
        todo = sorted(c for c in set(''.join(MASTER)) | {'王'} if c not in strokes)
        if todo:
            got, fails = B.fetch_missing(todo)
            if fails:
                sys.exit(f'❌ 笔画抓取失败: {"".join(fails)}')
            strokes.update(got)
        for nm in miss:
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
        rows.append({'n': nm, 'score': rec['score'], 'tier': rec['tier'],
                     'grp': g, 'src': '大师提名' if g == '大师提名' else f'档案·{g}',
                     'f': '女' if g == '女孩名' else ''})
    for n0, x in board.items():
        nm = '王' + n0
        rec = bscores[nm]
        rows.append({'n': nm, 'score': rec['score'], 'tier': rec['tier'],
                     'grp': SRC_NAME.get(x['s'], x['s']), 'src': f'榜单·{SRC_NAME.get(x["s"], x["s"])}',
                     'f': '女' if x.get('g') == '女' else ''})

    all_n = len(rows)
    girls = [r for r in rows if r['f'] == '女']
    rows = [r for r in rows if r['f'] != '女']
    assert len(rows) == all_n - len(girls)
    print(f'池 {all_n} 名 → 剔除女孩名 {len(girls)} → 男孩向 {len(rows)} 名')

    def stotal(r):
        rec = archive.get(r['n']) or bscores.get(r['n'])
        return sum(rec.get('strokes', [0])) if rec else 0

    rows.sort(key=lambda r: (-r['score'], TIER_RANK.get(r['tier'], 9), stotal(r), r['n']))
    for i, r in enumerate(rows, 1):
        r['rank'] = i
    top = rows[:100]

    order = {m: i for i, m in enumerate(MASTER)}
    master_ranks = [{'n': r['n'], 'rank': r['rank'], 'score': r['score']}
                    for r in rows if r['grp'] == '大师提名']
    master_ranks.sort(key=lambda x: order[x['n']])

    # ── 卡片记录（不在十二典 534 中的名字才需新增进页面 DATA）──
    ct = (ROOT / 'classics' / 'score_data.js').read_text(encoding='utf-8')
    classics = json.loads(ct[ct.index('{'):ct.rindex('}') + 1])
    zonghe = [r['n'] for r in top]
    entries = {}
    for r in top:
        nm = r['n']
        if nm in classics:
            continue
        is_board = nm[1:] in board and nm not in archive
        if is_board:
            x = board[nm[1:]]
            rec = bscores[nm]
            loc = f'{SRC_NAME.get(x["s"], x["s"])}{x["src"]}'
            quote = x['q']
            pick = ''
            meaning = x['m']
        else:
            rec = archive[nm]
            loc = r['grp']
            quote = notes.get(nm, {}).get('line', '')
            pick = ' / '.join(notes.get(nm, {}).get('eggs', []))
            meaning = notes.get(nm, {}).get('meaning', '')
            if nm in MASTER:
                q, src = MASTER_NOTE[nm]
                quote = q
                pick = src
        entries[nm] = {
            'strokes': rec['strokes'], 'score': rec['score'], 'tier': rec['tier'],
            'sancai': rec['sancai'], 'wuge': rec['wuge'], 'brk': rec['brk'],
            'wuxing': rec['wuxing'], 'tones': tones_of(nm),
            'source_book': '综合榜', 'source_loc': loc,
            'source_quote': quote, 'pick_reason': pick, 'meaning': meaning,
            'flag': '',
        }

    payload = {
        'meta': {
            'date': '2026-10-13',
            'pool': len(rows), 'cut': len(top),
            'archive_n': sum(1 for r in rows if r['src'].startswith('档案')),
            'board_n': sum(1 for r in rows if r['src'].startswith('榜单')),
            'master_n': len(MASTER), 'girls_excluded': len(girls),
            'master_ranks': master_ranks,
        },
        'list': [{'rank': r['rank'], 'name': r['n'], 'score': r['score'],
                  'tier': r['tier'], 'src': r['src']} for r in top],
        'zonghe': zonghe,
        'entries': entries,
    }
    (ROOT / 'top100_data.json').write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'✅ 写入 top100_data.json（前100 / 男孩向池 {len(rows)}；新增卡片 {len(entries)} 个，'
          f'{len(top)-len(entries)} 个已在十二典）')
    print('\n前16：')
    for r in top[:16]:
        mark = '★' if r['grp'] == '大师提名' else ' '
        print(f'  {r["rank"]:>3}. {mark}{r["n"]} {r["score"]} {r["tier"]:<4} {r["src"]}')
    print('\n大师提名位次（男孩向 178 池）：')
    for m in master_ranks:
        flag = '入围' if m['rank'] <= 100 else '未入前100'
        print(f'  {m["n"]} #{m["rank"]} ({m["score"]}) {flag}')


if __name__ == '__main__':
    main()
