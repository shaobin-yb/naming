# -*- coding: utf-8 -*-
"""批量查 liki qiming_char 字库(Top100+大师10名用字),带限流退避+断点续跑。"""
import json, os, socket, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")

# urllib 连接稳定性差(SSL 会话被针对),改用 curl 做请求端;JSON 经 stdin 传,绕开命令行中文编码
CURL = r"D:\Program Files\Git\mingw64\bin\curl.exe"

# 本机到 liki.hk 的 IPv6 路由不通,urllib 优先 IPv6 会 SSL 握手挂死 —— 强制 IPv4
_orig_gai = socket.getaddrinfo
def _gai_v4(host, port, family=0, *args, **kw):
    return _orig_gai(host, port, socket.AF_INET, *args, **kw)
socket.getaddrinfo = _gai_v4

BASE = "D:/cloude code/naming"
URL = "https://liki.hk/counsel/mcp/naming"
OUT = f"{BASE}/_liki_chars.json"

d = json.load(open(f"{BASE}/top100_data.json", encoding="utf-8"))
names = [it["name"] for it in d["list"]]
MASTER = ["王瞰云", "王御纬", "王撼岳", "王啸风", "王决云", "王挹江",
          "王枕风", "王浸阳", "王闻雨", "王鹤如"]
names += MASTER
chars = sorted({c for n in names for c in n[1:]})
print(f"总字数(去姓): {len(chars)}", flush=True)


def call(char, tries=3):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                          "params": {"name": "qiming_char", "arguments": {"char": char}}}).encode("utf-8")
    for _ in range(tries):
        try:
            p = subprocess.run([CURL, "-s", "--max-time", "25", "-X", "POST", URL,
                                "-H", "Content-Type: application/json",
                                "-H", "Accept: application/json, text/event-stream",
                                "-d", "@-"],
                               input=payload, capture_output=True, timeout=40)
            body = p.stdout.decode("utf-8", "replace")
            if not body.strip():
                print(f"  [{char}] empty -> backoff 25s", flush=True)
                time.sleep(25)
                continue
            j = json.loads(body)
            if "result" in j:
                return json.loads(j["result"]["content"][0]["text"])
            print(f"  [{char}] err: {json.dumps(j, ensure_ascii=False)[:120]}", flush=True)
            time.sleep(15)
        except Exception as e:
            print(f"  [{char}] exc: {e} -> backoff 15s", flush=True)
            time.sleep(15)
    return None


res = {}
if os.path.exists(OUT):
    res = json.load(open(OUT, encoding="utf-8"))
    print(f"断点续跑:已有 {len(res)} 字", flush=True)

for i, c in enumerate(chars):
    if c in res:
        continue
    r = call(c)
    if r is not None:
        res[c] = r if r else {"unlisted": True}  # 空响应体=字库未收录,与"未查询/失败"区分
    print(f"{i + 1}/{len(chars)} {c} -> {json.dumps(r, ensure_ascii=False)}", flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(6.5)

print(f"DONE {len(res)}/{len(chars)}", flush=True)
