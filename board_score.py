# -*- coding: utf-8 -*-
"""给「好听名字榜单」75 名评分（口径与 score_all.py 完全一致）。

- 评分逻辑复刻 score_all.main() 的内层循环（五格+三才+音形义，出处彩蛋 +1）
- 榜单 15 个与十二典重合的名字用于验证：分数必须与 classics/score_data.js 一致
- 输出 naming/board_scores.json
"""
import json
import re
import socket
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# 2026-10-13 踩坑：本机到 kangxizidian.org 的 IPv6 路由不通（https 连接超时），
# urllib 默认解析到 IPv6 导致整批抓取挂死。强制 IPv4 后实测 200/2.8s。
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_getaddrinfo

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pypinyin import Style, lazy_pinyin
from pypinyin import pinyin as to_pinyin
import score_all as SA

CLS_DIR = ROOT / 'classics'

# 多音字：采用十二典批次口径（score_classics.py 的 DUOYIN 超集），
# 区别于 score_all.py 的家里口径（无 行/乐 等）。榜单与十二典同池比较，
# 口径必须一致——王景行 验证用（十二典 86：行 −1）。
DUOYIN = {'得', '和', '正', '桔', '翘', '长', '乐', '行', '兴', '相', '令',
          '胜', '载', '省', '干'}


def load_all_strokes():
    cache = {}
    # 1) 十二典笔画缓存
    p = CLS_DIR / 'strokes_cache.json'
    if p.exists():
        cache.update(json.loads(p.read_text(encoding='utf-8')))
    # 2) 十二典已评名字的笔画
    t = (CLS_DIR / 'score_data.js').read_text(encoding='utf-8')
    for nm, v in json.loads(t[t.index('{'):t.rindex('}') + 1]).items():
        for ch, n in zip(nm, v.get('strokes') or []):
            if isinstance(n, int):
                cache.setdefault(ch, n)
    # 3) 档案评分器的缓存/已知表
    for d in (SA.load_stroke_cache(), SA.KNOWN_STROKES, SA.OVERRIDE):
        for k, v in d.items():
            cache.setdefault(k, v)
    return cache


def fetch_once(url, timeout=20):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', errors='replace')


def stroke_kangxi(ch):
    """从 kangxizidian.org 抓康熙笔画。

    2026-10-13 页面改版：老正则 `康熙笔画[^0-9]{0,15}?(\\d)` 已失效；
    现字段为 badge「笔画」= 康熙口径（实测 芳10/阿13/饮13，饮=飮13 非繁体飲12）。
    另注：本机 IPv6 路由不通，必须强制 IPv4（见文件头 patch）。
    """
    candidates = list(lazy_pinyin(ch))
    try:
        for grp in to_pinyin(ch, heteronym=True):
            candidates += grp
    except Exception:
        pass
    seen = set()
    for py in candidates:
        if py in seen:
            continue
        seen.add(py)
        url = f'https://kangxizidian.org/hanzi/{py}/{urllib.parse.quote(ch)}.html'
        try:
            html = fetch_once(url)
        except Exception:
            continue
        m = re.search(r'badge-label">笔画</span><span class="badge-value">(\d{1,2})', html)
        if m:
            return int(m.group(1))
        m = re.search(r'繁体笔画</span>\s*<strong><a[^>]*>(\d{1,2})', html)
        if m:
            return int(m.group(1))
    return None


def fetch_missing(chars):
    got = {}
    fails = []
    for i, ch in enumerate(sorted(chars)):
        n = None
        for attempt in range(3):
            try:
                n = stroke_kangxi(ch)
            except Exception:
                n = None
            if n is not None:
                break
            time.sleep(1.5)
        if n is None:
            fails.append(ch)
            print(f'  [{i+1}/{len(chars)}] {ch}: ✗', flush=True)
        else:
            got[ch] = n
            print(f'  [{i+1}/{len(chars)}] {ch}: {n}', flush=True)
        time.sleep(0.25)
    return got, fails


def score_name(name, strokes):
    """复刻 score_all.main() 内层评分循环（含出处彩蛋 +1）。"""
    a, b, c = name[0], name[1], name[2]
    sa, sb, sc = strokes[a], strokes[b], strokes[c]
    tian = sa + 1
    ren = sa + sb
    di = sb + sc
    wai = sc + 1
    zong = sa + sb + sc
    wuge = {'天': tian, '人': ren, '地': di, '外': wai, '总': zong}

    def cat(v):
        if v in SA.DAJI: return '大吉'
        if v in SA.JI: return '吉'
        if v in SA.FENQI: return '分歧⚠️'
        if v in SA.XIONG: return '凶'
        raise SystemExit(f'❌ 数理 {v}（{name}）未归入吉凶表')

    tags = {k: cat(v) for k, v in wuge.items()}

    we = {'天': SA.wuxing_of(tian), '人': SA.wuxing_of(ren), '地': SA.wuxing_of(di)}
    rels = []
    for x, y in [('天', '人'), ('人', '地')]:
        ex, ey = we[x], we[y]
        if ex == ey or SA.SHENG[ex] == ey or SA.SHENG[ey] == ex:
            rels.append('吉')
        else:
            rels.append('克')
    if rels == ['吉', '吉']:
        sancai = f'{we["天"]}{we["人"]}{we["地"]} · 相生比和（吉配）'
        sc_sancai = 30
    else:
        sancai = f'{we["天"]}{we["人"]}{we["地"]} · 有相克（⚠️）'
        sc_sancai = 12

    def sc_ge(k, v):
        t = tags[k]
        if k == '人':
            return {'大吉': 19, '吉': 18, '分歧⚠️': 13, '凶': 8}[t]
        if k == '地':
            return {'大吉': 15, '吉': 14, '分歧⚠️': 10, '凶': 6}[t]
        if k == '总':
            return {'大吉': 15, '吉': 13, '分歧⚠️': 8, '凶': 5}[t]
        return {'大吉': 9, '吉': 8, '分歧⚠️': 4, '凶': 2}[t]

    sc_ren, sc_di, sc_zong, sc_wai = (sc_ge('人', ren), sc_ge('地', di),
                                      sc_ge('总', zong), sc_ge('外', wai))

    tones = [to_pinyin(ch, style=Style.TONE3)[0][0][-1] for ch in name]
    sc_yin = 8
    if len(set(tones)) == 3: sc_yin += 1
    elif len(set(tones)) == 1: sc_yin -= 1
    if any(ch in SA.RARE for ch in name): sc_yin -= 1
    if any(ch in DUOYIN for ch in name): sc_yin -= 1
    sc_yin += 1  # 榜单全部名字均可考出处（诗经/楚辞/唐诗宋词等）→ 彩蛋 +1
    sc_yin = max(6, min(10, sc_yin))

    score = sc_sancai + sc_ren + sc_di + sc_zong + sc_wai + sc_yin

    n_xiong = sum(1 for t in tags.values() if t == '凶')
    n_fenqi = sum(1 for t in tags.values() if t == '分歧⚠️')
    if n_xiong >= 3: tier = '慎用'
    elif n_xiong == 2: tier = '多⚠️'
    elif n_xiong == 1 or n_fenqi >= 1: tier = '一⚠️'
    else: tier = '全绿'

    char_wx = [SA.wuxing_of(sa), SA.wuxing_of(sb), SA.wuxing_of(sc)]
    missing = [e for e in SA.ELEM if e not in char_wx]
    wuge_out = {}
    for k in ('天', '人', '地', '外', '总'):
        v = wuge[k]
        nm = SA.SHULI_NAME.get(v, '')
        wuge_out[k] = [f'{v} {nm}'.strip(), tags[k]]

    return {
        'strokes': [sa, sb, sc],
        'score': score,
        'tier': tier,
        'sancai': sancai,
        'wuge': wuge_out,
        'brk': [sc_sancai, sc_ren, sc_di, sc_zong, sc_wai, sc_yin],
        'wuxing': {
            'chars': ''.join(char_wx),
            'missing': ''.join(missing) or '无',
            'wuge': ''.join(SA.wuxing_of(v) for v in wuge.values()),
        },
    }


def main():
    board = json.loads((ROOT / 'board_names.json').read_text(encoding='utf-8'))
    names = ['王' + x['n'] for x in board]

    strokes = load_all_strokes()
    chars = set(''.join(names))
    missing = sorted(ch for ch in chars if ch not in strokes)
    print(f'共 {len(chars)} 字：已有 {len(chars)-len(missing)}，待抓 {len(missing)}')
    if missing:
        got, fails = fetch_missing(missing)
        strokes.update(got)
        if fails:
            sys.exit(f'❌ 抓取失败: {"".join(fails)} —— 需人工查证后写入 OVERRIDE')
        # 合并回缓存
        p = CLS_DIR / 'strokes_cache.json'
        cache = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
        cache.update(got)
        p.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding='utf-8')
        print(f'新增 {len(got)} 字笔画写入 strokes_cache.json')

    # 十二典重合名验证
    t = (CLS_DIR / 'score_data.js').read_text(encoding='utf-8')
    cls = json.loads(t[t.index('{'):t.rindex('}') + 1])

    result = {}
    mismatch = []
    for nm in names:
        rec = score_name(nm, strokes)
        result[nm] = rec
        if nm in cls:
            want = cls[nm]
            if (rec['score'], rec['tier']) != (want['score'], want['tier']):
                mismatch.append((nm, rec['score'], want['score'], rec['tier'], want['tier']))

    print(f'\n写入 board_scores.json，共 {len(result)} 名')
    if mismatch:
        print('❌ 与十二典口径不一致:')
        for m in mismatch:
            print('   ', m)
        sys.exit(1)
    print('✅ 与十二典重合的 15 名分数、档位完全一致')

    (ROOT / 'board_scores.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')

    print('\n名字 | 笔画 | 五格(天/人/地/外/总) | 评分 | 档')
    for nm in sorted(names, key=lambda n: -result[n]['score']):
        r = result[nm]
        print(f'{nm} | {"".join(map(str, r["strokes"]))} | '
              f'{"/".join(r["wuge"][k][0].split()[0] for k in ("天","人","地","外","总"))} | '
              f'{r["score"]} | {r["tier"]}')


if __name__ == '__main__':
    main()
