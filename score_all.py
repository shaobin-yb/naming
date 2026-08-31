"""Batch-score all names in the naming archive.

1. 抓 kangxizidian.org 康熙笔画（逐字验证，不凭记忆）
2. 五格 + 五行 + 三才 + 评分（公式与 2026-08-17 会话口径一致）
3. 输出 naming/score_data.js 供 index.html 加载
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pypinyin import lazy_pinyin, Style
from pypinyin import pinyin as to_pinyin

ROOT = Path(__file__).resolve().parent

# ── 87 个名字（全部王姓三字名）──
NAMES = [
    # 已定名 / 讨论候选（34）
    '王斯卯', '王元一', '王驰元', '王元午', '王元壹', '王元正', '王太一',
    '王齐一', '王惟一', '王若朴', '王虚白', '王抱朴', '王善渊', '王得一',
    '王守一', '王道一', '王中和', '王知白', '王和光', '王玄一', '王致一',
    '王天一', '王心一', '王培元', '王善元', '王得元', '王斯元', '王元本',
    '王元玄', '王元方', '王川元', '王抱元', '王春元', '王聿午',
    # 女孩名（53，出自《女孩名字-王.xlsx》）
    '王瑾翕', '王简盈', '王简饶', '王简傲', '王岁安', '王浅素', '王乔幽',
    '王鹿芩', '王安晓', '王月白', '王唯月', '王子鸢', '王沐恩', '王颂恩',
    '王安禾', '王安隐', '王安饶', '王栀一', '王清一', '王伊闻', '王苏漾', '王简汀',
    '王晚萤', '王芸熹', '王艾之', '王染墨', '王点萤', '王芷凝', '王诗旅',
    '王枝意', '王亭晚', '王朵萤', '王未抒', '王晚漾', '王之棠', '王素浅',
    '王温善', '王清夏', '王徽颀', '王清丹', '王听澜', '王亦初', '王荷穗',
    '王槿之', '王染堤', '王初染', '王若婳', '王语清', '王仰灿', '王听禾',
    '王浅月', '王妤晴', '王安之',
]

# ── 会话已验证的康熙笔画（抓取结果须与这些一致，不一致即报警）──
KNOWN_STROKES = {
    '王': 4, '斯': 12, '卯': 5, '元': 4, '一': 1, '午': 4, '聿': 6,
    '驰': 13, '壹': 12, '正': 5, '太': 4, '齐': 14, '惟': 12, '若': 11,
    '朴': 16, '虚': 12, '白': 5, '抱': 9, '善': 12, '渊': 12, '得': 11,
    '守': 6, '道': 16, '中': 4, '和': 8, '知': 8, '光': 6, '玄': 5,
    '致': 9, '天': 4, '心': 4, '培': 11, '本': 5, '川': 3, '春': 9,
}

# 姓名学约定笔画覆盖（均经 WebSearch 双源查证，2026-08-24）：
# 朴: 起名语境义为「质朴」(樸) → 按繁体 樸 16 画（本字 朴 = 6 画）
# 玄: 康熙字典玄部 5 画（qianp 抓取 9 画为误）
# 婳: 按繁体 嫿 计 15 画（女3+畫12；简体 婳 11 画）
OVERRIDE = {'朴': 16, '玄': 5, '婳': 15}

# ── 81 数理吉凶分类（与 2026-08-17 会话口径一致）──
DAJI = {1, 3, 5, 6, 7, 11, 13, 15, 16, 18, 21, 23, 24, 25, 29, 31, 32,
        33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65, 67, 68, 81}
FENQI = {2, 9, 19, 20, 27, 28, 34, 36, 40, 44, 50, 54, 56, 58, 60, 62,
         64, 66, 69, 70, 72, 74, 76, 78}
XIONG = {10, 12, 14, 22, 26, 30, 42, 46, 49, 53, 55, 59, 71, 73, 75, 77, 79, 80}

# 数理名（仅收录有把握的，其余只显数字）
SHULI_NAME = {
    1: '大展鸿图', 2: '混沌未定', 3: '吉祥如意', 5: '种竹成林', 6: '安稳余庆',
    7: '精悍', 8: '坚刚', 9: '破舟入海', 10: '零暗', 11: '旱苗逢雨',
    12: '掘井无泉', 13: '春日牡丹', 14: '破兆', 15: '福寿', 16: '厚德载物',
    17: '刚强', 18: '铁镜重磨', 19: '多难', 20: '屋下藏金', 21: '明月中天',
    22: '秋草逢霜', 23: '旭日东升', 24: '掘藏得金', 25: '资性英敏', 26: '变怪',
    27: '欲望无止', 28: '阔水浮萍', 29: '智谋', 31: '春日花开', 32: '宝马金鞍',
    33: '旭日升天', 35: '高楼望月', 37: '猛虎出林', 39: '富贵荣华',
    41: '德高望重', 45: '顺风扬帆', 47: '点石成金', 48: '古松立鹤',
    63: '繁荣', 65: '巨流归海', 67: '通达', 68: '财路亨通', 81: '万物回春',
}

# 五行（尾数）
def wuxing_of(n):
    t = n % 10
    if t in (1, 2): return '木'
    if t in (3, 4): return '火'
    if t in (5, 6): return '土'
    if t in (7, 8): return '金'
    return '水'

ELEM = '木火土金水'
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
def ke(a, b):  # a 克 b?
    return (a, b) in [('木', '土'), ('土', '水'), ('水', '火'), ('火', '金'), ('金', '木')]

# 生僻字 / 多音字（音形义扣分用，口径与会话一致）
RARE = {'翕', '芩', '婳', '颀', '徽', '槿'}
DUOYIN = {'得', '和', '正'}

# 名字自带典故/出处/生肖彩蛋（音形义 +1，与网页 NAMES 的 eggs 对齐）
EGG_BONUS = {
    '王瑾翕', '王乔幽', '王鹿芩', '王安晓', '王月白', '王唯月', '王子鸢',
    '王安隐', '王安饶', '王栀一', '王芷凝', '王槿之', '王语清', '王浅月',
    '王妤晴', '王安之',
    '王齐一', '王惟一', '王若朴', '王虚白', '王抱朴', '王善渊', '王得一',
    '王守一', '王道一', '王中和', '王知白', '王和光', '王玄一', '王致一',
    '王培元', '王善元', '王元方', '王心一',
}

# 已定名/已评分的会话记录（保留原值，不做公式覆盖）
RECORDED = {
    '王斯卯': {'score': 96, 'brk': [30, 19, 14, 15, 9, 9], 'tier': '全绿'},
    '王元一': {'score': 84, 'brk': [30, 18, 15, 8, 4, 9], 'tier': '一⚠️'},
    '王元午': {'score': 87, 'brk': [30, 18, 14, 8, 9, 8], 'tier': '一⚠️'},
    '王聿午': {'score': 46, 'brk': [12, 8, 6, 5, 9, 6], 'tier': '慎用'},
    '王元壹': {'score': 88, 'tier': '一⚠️'},
    '王元正': {'score': 89, 'tier': '一⚠️'},
    '王太一': {'score': 84, 'tier': '一⚠️'},
    '王驰元': {'score': 96, 'tier': '全绿'},
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')


def get_stroke_kangxi(ch):
    # 多音字：lazy_pinyin 只给常用音，URL 可能对不上 → 枚举全部异读音
    candidates = [lazy_pinyin(ch)[0]]
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
            html = fetch(url)
        except Exception:
            continue
        m = re.search(r'康熙笔画[^0-9]{0,15}?(\d{1,2})', html)
        if m:
            return int(m.group(1))
    return None


def get_stroke_qianp(ch):
    """千篇国学: 康熙笔画（含部首按康熙计）。"""
    url = f'https://zidian.qianp.com/zi/{urllib.parse.quote(ch)}'
    try:
        html = fetch(url)
    except Exception:
        return None
    m = re.search(r'康熙[^0-9]{0,10}?(\d{1,2})\s*画', html)
    return int(m.group(1)) if m else None


def get_stroke(ch):
    if ch in OVERRIDE:
        return OVERRIDE[ch]
    a = get_stroke_kangxi(ch)
    b = get_stroke_qianp(ch)
    if a is not None and b is not None and a != b:
        print(f'⚠️ 双源不一致: {ch} kangxi={a} qianp={b} → 取 kangxi')
    return a if a is not None else b


def main():
    chars = sorted(set(''.join(NAMES)))
    strokes = {}
    print(f'共 {len(chars)} 个不重复字，开始抓取...')
    failed = []
    for i, ch in enumerate(chars):
        try:
            n = get_stroke(ch)
            strokes[ch] = n
            if n is None:
                failed.append(ch)
                print(f'  [{i+1}/{len(chars)}] {ch}: 页面未找到笔画')
            else:
                print(f'  [{i+1}/{len(chars)}] {ch}: {n}')
        except Exception as e:
            failed.append(ch)
            print(f'  [{i+1}/{len(chars)}] {ch}: ERROR {type(e).__name__}')
        time.sleep(0.35)

    # 验证已知笔画
    for ch, want in KNOWN_STROKES.items():
        got = strokes.get(ch)
        if got != want:
            print(f'⚠️ 笔画校验不符: {ch} 应 {want} 得 {got}')

    if failed:
        print('⚠️ 抓取失败:', failed)
        sys.exit(1)

    scores = {}
    for name in NAMES:
        a, b, c = name[0], name[1], name[2]
        sa, sb, sc = strokes[a], strokes[b], strokes[c]
        # 五格
        tian = sa + 1
        ren = sa + sb
        di = sb + sc
        wai = sc + 1
        zong = sa + sb + sc
        wuge = {'天': tian, '人': ren, '地': di, '外': wai, '总': zong}

        def cat(v):
            if v in DAJI: return '大吉'
            if v in FENQI: return '分歧⚠️'
            if v in XIONG: return '凶'
            return '吉'

        tags = {k: cat(v) for k, v in wuge.items()}

        # 三才
        we = {'天': wuxing_of(tian), '人': wuxing_of(ren), '地': wuxing_of(di)}
        rels = []
        for x, y in [('天', '人'), ('人', '地')]:
            ex, ey = we[x], we[y]
            if ex == ey or SHENG[ex] == ey or SHENG[ey] == ex:
                rels.append('吉')
            else:
                rels.append('克')
        if rels == ['吉', '吉']:
            sancai = f'{we["天"]}{we["人"]}{we["地"]} · 相生比和（吉配）'
            sc_sancai = 30
        elif '克' in rels:
            sancai = f'{we["天"]}{we["人"]}{we["地"]} · 有相克（⚠️）'
            sc_sancai = 12
        else:
            sancai = f'{we["天"]}{we["人"]}{we["地"]}'
            sc_sancai = 24

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

        # 音形义
        tones = [to_pinyin(ch, style=Style.TONE3)[0][0][-1] for ch in name]
        sc_yin = 8
        if len(set(tones)) == 3: sc_yin += 1
        elif len(set(tones)) == 1: sc_yin -= 1
        if any(ch in RARE for ch in name): sc_yin -= 1
        if any(ch in DUOYIN for ch in name): sc_yin -= 1
        if name in EGG_BONUS: sc_yin += 1
        sc_yin = max(6, min(10, sc_yin))

        score = sc_sancai + sc_ren + sc_di + sc_zong + sc_wai + sc_yin

        # 层档
        n_xiong = sum(1 for t in tags.values() if t == '凶')
        n_fenqi = sum(1 for t in tags.values() if t == '分歧⚠️')
        if n_xiong >= 3: tier = '慎用'
        elif n_xiong == 2: tier = '多⚠️'
        elif n_xiong == 1 or n_fenqi >= 1: tier = '一⚠️'
        else: tier = '全绿'

        # 五行
        char_wx = [wuxing_of(sa), wuxing_of(sb), wuxing_of(sc)]
        missing = [e for e in ELEM if e not in char_wx]
        wuge_wx = ''.join(wuxing_of(v) for k, v in wuge.items())

        rec = RECORDED.get(name)
        if rec:
            score = rec['score']
            tier = rec['tier']
            if 'brk' in rec:
                brk = rec['brk']
            else:
                # 公式重算，音形义补差对齐会话分数
                base = sc_sancai + sc_ren + sc_di + sc_zong + sc_wai
                yin = max(6, min(10, score - base))
                brk = [sc_sancai, sc_ren, sc_di, sc_zong, sc_wai, yin]
        else:
            brk = [sc_sancai, sc_ren, sc_di, sc_zong, sc_wai, sc_yin]

        wuge_out = {}
        for k in ('天', '人', '地', '外', '总'):
            v = wuge[k]
            nm = SHULI_NAME.get(v, '')
            wuge_out[k] = [f'{v} {nm}'.strip(), tags[k]]

        scores[name] = {
            'strokes': [sa, sb, sc],
            'score': score,
            'tier': tier,
            'sancai': sancai,
            'wuge': wuge_out,
            'brk': brk,
            'wuxing': {
                'chars': ''.join(char_wx),
                'missing': ''.join(missing) or '无',
                'wuge': wuge_wx,
            },
        }

    out = 'const SCORE_DATA = ' + json.dumps(scores, ensure_ascii=False, indent=1) + ';\n'
    (ROOT / 'score_data.js').write_text(out, encoding='utf-8')
    print(f'写入 score_data.js，共 {len(scores)} 个名字')

    # 控制台总表
    print('\n名字 | 笔画 | 五格(天/人/地/外/总) | 三字五行 | 评分 | 档')
    for name in NAMES:
        s = scores[name]
        print(f'{name} | {"".join(map(str, s["strokes"]))} | '
              f'{"/".join(s["wuge"][k][0].split()[0] for k in ("天","人","地","外","总"))} | '
              f'{s["wuxing"]["chars"]} | {s["score"]} | {s["tier"]}')


if __name__ == '__main__':
    main()
