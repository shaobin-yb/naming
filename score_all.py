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

# 2026-10-13 踩坑（与 board_score.py 同源）：本机到 kangxizidian.org 的 IPv6 路由不通，
# urllib 默认优先解析 IPv6，导致整批抓取挂死——强制 IPv4 后恢复正常。
import socket
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_getaddrinfo

ROOT = Path(__file__).resolve().parent

# ── 87 个名字（全部王姓三字名）──
NAMES = [
    # 已定名 / 讨论候选（34 + 新增 2026-09-15 牧简之悠融合系列）
    '王斯卯', '王元一', '王驰元', '王元午', '王元壹', '王元正', '王太一',
    '王齐一', '王惟一', '王若朴', '王虚白', '王抱朴', '王善渊', '王得一',
    '王守一', '王道一', '王中和', '王知白', '王和光', '王玄一', '王致一',
    '王天一', '王心一', '王培元', '王善元', '王得元', '王斯元', '王元本',
    '王元玄', '王元方', '王川元', '王抱元', '王春元', '王聿午',
    '王牧之', '王简一', '王牧一', '王悠之', '王简之', '王牧悠', '王简悠',
    # 传承向 2026-09-24（承老大「王斯卯」一西一东 + 生肖嵌字结构，老二取丙午马年「午」）
    '王斯午', '王恒午', '王亘午', '王宙午', '王玄午', '王周午', '王常午',
    '王永午', '王仲午', '王双午', '王乙午', '王又午',
    '王午恒', '王午玄', '王午斯',
    # 五劫向 2026-09-24（道教五劫说：卯=上皇住劫 / 午=开皇住劫，俱为住劫）
    # A 开皇本劫（老二本劫）：劫名「开」+ 五气「元阳之气」
    '王午开', '王开午', '王午阳', '王阳午', '王午元',
    # B 上皇本劫（老大本劫）：五气「中灵之气」
    '王午中', '王午灵',
    # C 住劫之性 + 劫名本字
    '王午住', '王午皇', '王午上',
    # D 延康本劫（爸妈本劫，酉）：劫名「延」「康」—— 2026-09-24 老板补充：夫妻同属酉鸡
    '王午康', '王康午', '王延午', '王午延',
    # E 其余劫名：龙汉「龙」「汉」/ 赤明「赤」「明」
    '王午龙', '王龙午', '王午汉', '王汉午', '王午明', '王明午', '王午赤', '王赤午',
    # 中药名向 2026-09-28（药典2020版83种毒性中药已全部筛除；β=灰名单另标）
    # 清雅型
    '王白芷', '王青黛', '王白薇', '王紫萱', '王桔梗', '王玉竹',
    '王合欢', '王连翘', '王辛夷', '王石斛', '王雪见',
    # 端方型
    '王苁蓉', '王厚朴', '王茯苓', '王灵芝', '王紫苏', '王景天', '王长卿',
    # 生肖忌用字根，保留待权衡
    '王忍冬', '王远志',
    # ── 兄弟对仗向 2026-09-28（三个接点：木字桥 / 午火意象 / 元一呼应）──
    # 接点 B「木字桥」：卯的五行=木，草药名天然属木（艹/木字旁）
    '王木香', '王苏木',
    # 接点 C「五行相生」：卯(木)生午(火)，取火/日/明意象
    '王决明', '王丹参', '王赤芝',
    # 呼应「王元一」的元 / 数字对仗
    '王元参', '王百合',
    # 生肖马字旁（承「王驰元」偏旁藏生肖手法）
    '王马兰',
    # 老板提名 2026-10-12（经典出处向：中庸 / 庄子·则阳+周易·讼 / 离骚+幼学琼林 / 抱朴子·广譬）
    '王斯昭', '王饮和', '王云启', '王谷安',
    # 老板提名 2026-10-13（代办「寒假作业」10 名：豪放派 5 + 清幽派 5，引文已逐条网络核验）
    '王瞰云', '王御纬', '王撼岳', '王啸风', '王决云',
    '王挹江', '王枕风', '王浸阳', '王闻雨', '王鹤如',
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
    # 2026-09-15 新增（kangxizidian.org 双源验证）
    '牧': 8, '简': 18, '之': 4, '悠': 11,
    # 2026-09-24 传承向新增（双源验证，双/乙 见 OVERRIDE）
    '恒': 10, '亘': 6, '宙': 8, '周': 8, '常': 11, '永': 5,
    '仲': 6, '又': 2, '双': 18, '乙': 1,
    # 2026-09-24 五劫向新增（kangxi 源；阳 经 WebSearch 多源印证 = 陽 17画）
    '开': 12, '阳': 17, '皇': 9, '住': 7, '灵': 24, '上': 3, '中': 4,
    # 2026-09-24 延康/龙汉/赤明劫名（延/汉 经 WebSearch 多源印证：延=康熙7画、汉=繁体漢15画）
    '康': 11, '延': 7, '龙': 16, '汉': 15, '赤': 7, '明': 8,
    # 2026-09-28 中药名向（kangxizidian.org + zidian.qianp.com 双源抓取实测）
    # 注：黛 实测 17 画（非直觉的 16）——黑12+代5，以抓取为准
    '青': 8, '黛': 17, '芷': 10, '薇': 19, '紫': 11, '萱': 15,
    '桔': 10, '梗': 11, '玉': 5, '竹': 6, '合': 6, '欢': 22,
    '连': 14, '翘': 18, '辛': 7, '夷': 6, '石': 5, '斛': 11,
    '雪': 11, '见': 7, '苁': 17, '蓉': 16, '厚': 9, '茯': 12,
    '苓': 11, '芝': 10, '苏': 22, '景': 12, '长': 8, '卿': 11,
    '忍': 7, '冬': 5, '远': 17, '志': 7,
    # 2026-09-28 兄弟对仗向（kangxizidian.org 实测；千篇源当日限流未返回）
    # 兰 23 = 繁体蘭（同「汉15=漢」口径）；马 10 = 繁体馬；参 11 = 參
    '木': 4, '香': 9, '决': 8, '丹': 4, '参': 11, '百': 6, '兰': 23, '马': 10,
    # 2026-10-12 老板提名四名（实测：云 12 = 繁体雲、启 11 = 繁体啟，同「汉15=漢」口径）
    # 饮 13 = 康熙字典【戌集下】【食】飮·康熙筆画13·部外筆画4（食部按完整 9 画计；
    #   kangxizidian.org 与多个姓名学源印证一致，12 画为少数派字形计法）
    '昭': 9, '饮': 13, '云': 12, '启': 11, '谷': 7, '安': 6,
    # 2026-10-13 老板提名「寒假作业」10 名用字（kangxizidian.org 专业版实测，浏览器直取）
    #   啸 16：康熙页眉计 15（部外12）vs 条目正文「嘯字十六畫」——姓名学通行口径为
    #   口3+部外13=16（与「肃=繁体13」算术自洽），取名用字按姓名学口径取 16
    '瞰': 17, '撼': 17, '啸': 16, '挹': 11, '枕': 8, '浸': 11, '岳': 8, '雨': 8, '江': 7,
    # 以下取自十二典轮已验证缓存（classics/strokes_cache.json，同康熙口径）：
    '御': 11, '纬': 15, '鹤': 21, '如': 6, '风': 9, '闻': 14,
}

# 姓名学约定笔画覆盖（均经 WebSearch 双源查证，2026-08-24）：
# 朴: 起名语境义为「质朴」(樸) → 按繁体 樸 16 画（本字 朴 = 6 画）
# 玄: 康熙字典玄部 5 画（qianp 抓取 9 画为误）
# 婳: 按繁体 嫿 计 15 画（女3+畫12；简体 婳 11 画）
# 双: 三才五格以康熙为准 → 按繁体 雙 18 画（简体 双 = 4 画；2026-09-24 WebSearch 双源查证）
# 乙: 康熙乙部 1 画（kangxizidian 页面无笔画字段，qianp = 1 采信）
OVERRIDE = {'朴': 16, '玄': 5, '婳': 15, '双': 18, '乙': 1}

# ── 81 数理吉凶分类（与 2026-08-17 会话口径一致）──
# 2026-09-24 修复：4 与 43 原先不在任何集合，落到 else 分支被默认判「吉」——
# 权威 81 数理表两者皆为凶（4=凶变/短命之数，与 9/19/20/34/44 同组；43=散财破产），
# 且「王午上」外格 4 因此虚高。按本表「各家有出入→分歧」的既有口径，二者归入 FENQI。
# JI 为「吉」档（非大吉）：8、17 等落在这一档是该口径的原意，不可并入 DAJI。
DAJI = {1, 3, 5, 6, 7, 11, 13, 15, 16, 18, 21, 23, 24, 25, 29, 31, 32,
        33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65, 67, 68, 81}
JI = {8, 17}
# 2026-09-28 新增 38：中药名向「王灵芝」总格 38 触发未分类报错（该报错正是 09-24 修复的预期行为）。
# 38 =「磨铁成针」半吉——各家标注有出入（熊崎式定半吉 / 有流派标「凶带吉」「吉中带凶」），
# 按本表「各家有出入→分歧」的既有口径归入 FENQI，不并入 DAJI。
FENQI = {2, 4, 9, 19, 20, 27, 28, 34, 36, 38, 40, 43, 44, 50, 54, 56, 58, 60, 62,
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
# 2026-09-28 增补：苁/斛 生僻；桔(jié/jú)、翘(qiáo/qiào)、长(cháng/zhǎng) 多音
# 2026-10-12 增补：饮（yǐn 喝水 / yìn 使饮——「饮和」词典口径作 yìn，点名场景两读皆现，属需纠正的读音）
# 2026-10-13 增补：瞰、挹（老板提名「寒假作业」名字中的冷字，日常认读书写成本高）
RARE = {'翕', '芩', '婳', '颀', '徽', '槿', '苁', '斛', '瞰', '挹'}
DUOYIN = {'得', '和', '正', '桔', '翘', '长', '饮'}

# 名字自带典故/出处/生肖彩蛋（音形义 +1，与网页 NAMES 的 eggs 对齐）
EGG_BONUS = {
    '王瑾翕', '王乔幽', '王鹿芩', '王安晓', '王月白', '王唯月', '王子鸢',
    '王安隐', '王安饶', '王栀一', '王芷凝', '王槿之', '王语清', '王浅月',
    '王妤晴', '王安之',
    '王齐一', '王惟一', '王若朴', '王虚白', '王抱朴', '王善渊', '王得一',
    '王守一', '王道一', '王中和', '王知白', '王和光', '王玄一', '王致一',
    '王培元', '王善元', '王元方', '王心一',
    # 2026-09-15 牧简之悠系列（典故彩蛋 +1）
    '王牧之', '王简一', '王简之', '王悠之',
    # 2026-09-24 传承向（生肖嵌字 / 典故 / 兄弟对仗，+1）
    '王斯午', '王恒午', '王亘午', '王周午', '王常午',
    '王午恒', '王午玄', '王午斯',
    # 2026-09-24 五劫向（道教五劫：卯=上皇 / 午=开皇，俱为住劫，典故 +1）
    '王午开', '王开午', '王午阳', '王阳午', '王午元',
    '王午中', '王午灵', '王午住', '王午皇', '王午上',
    '王午康', '王康午', '王延午', '王午延',
    '王午龙', '王龙午', '王午汉', '王汉午', '王午明', '王明午',
    # 2026-09-28 中药名向（每个都有可考的命名由来/典故，+1）
    '王白芷', '王青黛', '王白薇', '王紫萱', '王桔梗', '王玉竹',
    '王合欢', '王连翘', '王辛夷', '王石斛', '王雪见',
    '王苁蓉', '王厚朴', '王茯苓', '王灵芝', '王紫苏', '王景天', '王长卿',
    '王忍冬', '王远志',
    # 2026-09-28 兄弟对仗向（典故彩蛋 +1）
    '王木香', '王苏木', '王决明', '王丹参', '王赤芝',
    '王元参', '王百合', '王马兰',
    # 2026-10-12 老板提名四名（经典出处逐字可考，+1）
    '王斯昭', '王饮和', '王云启', '王谷安',
    # 2026-10-13 老板提名「寒假作业」10 名（引文经维基文库四库本等逐条核验，+1）
    '王瞰云', '王御纬', '王撼岳', '王啸风', '王决云',
    '王挹江', '王枕风', '王浸阳', '王闻雨', '王鹤如',
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


def fetch(url, retries=3):
    # 抓取源偶发抽风（返回错误页/超时），重试避免整个批次因单字中断
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/120.0 Safari/537.36'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            last = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise last


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


def load_stroke_cache():
    """从已有 score_data.js 复用笔画，避免每次全量重抓（源会限流）。"""
    path = ROOT / 'score_data.js'
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding='utf-8')
        data = json.loads(text[text.index('{'):text.rindex('}') + 1])
    except Exception:
        return {}
    cache = {}
    for name, v in data.items():
        st = v.get('strokes') or []
        for ch, n in zip(name, st):
            if isinstance(n, int):
                cache[ch] = n
    return cache


def main():
    chars = sorted(set(''.join(NAMES)))
    strokes = {}
    cache = load_stroke_cache()
    # 2026-10-13：已验证笔画（KNOWN_STROKES/OVERRIDE）直接采用、不再重复抓取
    #（慢网络日抓取会长时间卡死；如与抓取值有出入，由下方一致性检查兜底报警）
    todo = [ch for ch in chars if ch not in cache
            and ch not in KNOWN_STROKES and ch not in OVERRIDE]
    print(f'共 {len(chars)} 个不重复字：缓存+已验证 {len(chars) - len(todo)}，需抓取 {len(todo)}')
    strokes.update({ch: cache[ch] for ch in chars if ch in cache})
    strokes.update({ch: KNOWN_STROKES[ch] for ch in chars if ch in KNOWN_STROKES})
    strokes.update({ch: OVERRIDE[ch] for ch in chars if ch in OVERRIDE})
    failed = []
    for i, ch in enumerate(todo):
        n = None
        # 抓取源偶发返回错误页（200 但无笔画字段），重试整字查询
        for attempt in range(3):
            try:
                n = get_stroke(ch)
            except Exception:
                n = None
            if n is not None:
                break
            if attempt < 2:
                time.sleep(2.0 * (attempt + 1))
        strokes[ch] = n
        if n is None:
            failed.append(ch)
            print(f'  [{i+1}/{len(todo)}] {ch}: 页面未找到笔画（重试 3 次仍失败）')
        else:
            print(f'  [{i+1}/{len(todo)}] {ch}: {n}')
        time.sleep(0.35)

    # 已验证笔画作兜底：抓取失败/不一致时用权威值，不让网络抽风中断整批
    for ch, want in {**KNOWN_STROKES, **OVERRIDE}.items():
        got = strokes.get(ch)
        if got != want:
            note = '补用已验证值' if ch in failed or got is None else '以已知值为准'
            print(f'⚠️ 笔画不一致: {ch} 抓取={got} 已知={want} → {note}')
            strokes[ch] = want
            if ch in failed:
                failed.remove(ch)

    if failed:
        print('⚠️ 抓取失败（无已验证值兜底）:', failed)
        sys.exit(1)

    UNCLASSIFIED = set()
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
            if v in JI: return '吉'
            if v in FENQI: return '分歧⚠️'
            if v in XIONG: return '凶'
            # 数理表未覆盖绝对不能默认判吉——2026-09-24 的「4/43 静默判吉」bug 即源于此
            UNCLASSIFIED.add(v)
            return '未分类'

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
            if t == '未分类':
                raise SystemExit(f'❌ 数理 {v}（{name} {k}格）未归入吉凶表——'
                                 f'请先在 DAJI/FENQI/XIONG 中定义，不可默认判吉')
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

    # index.html 用 <script src> 引 score_data.js，浏览器会缓存旧版 → 数据改了页面不更新。
    # 打内容指纹：内容变才换版本号，避免无谓的 diff 噪音。
    import hashlib
    digest = hashlib.md5(out.encode('utf-8')).hexdigest()[:8]
    html_path = ROOT / 'index.html'
    html = html_path.read_text(encoding='utf-8')
    new_html = re.sub(r'<script src="score_data\.js(?:\?v=[0-9a-f]+)?"></script>',
                      f'<script src="score_data.js?v={digest}"></script>', html)
    if new_html != html:
        html_path.write_text(new_html, encoding='utf-8', newline='')
        print(f'index.html 版本指纹 → {digest}')

    # 控制台总表
    print('\n名字 | 笔画 | 五格(天/人/地/外/总) | 三字五行 | 评分 | 档')
    for name in NAMES:
        s = scores[name]
        print(f'{name} | {"".join(map(str, s["strokes"]))} | '
              f'{"/".join(s["wuge"][k][0].split()[0] for k in ("天","人","地","外","总"))} | '
              f'{s["wuxing"]["chars"]} | {s["score"]} | {s["tier"]}')


if __name__ == '__main__':
    main()
