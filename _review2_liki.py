# -*- coding: utf-8 -*-
"""627 全量池的余字批量查询(347字),合并存入 _liki_chars.json。"""
import json, os, socket, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")
CURL = r"D:\Program Files\Git\mingw64\bin\curl.exe"
BASE = "D:/cloude code/naming"
URL = "https://liki.hk/counsel/mcp/naming"
OUT = f"{BASE}/_liki_chars.json"

pool = json.load(open(f"{BASE}/_review2_pool.json", encoding="utf-8"))
res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
chars = [c for c in pool["todo"] if c not in res]
print(f"待查(去重后): {len(chars)}", flush=True)


def call(char, tries=4):
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
                print(f"  [{char}] empty -> backoff 20s", flush=True)
                time.sleep(20)
                continue
            j = json.loads(body)
            if "result" in j:
                return json.loads(j["result"]["content"][0]["text"])
            print(f"  [{char}] err: {json.dumps(j, ensure_ascii=False)[:100]}", flush=True)
            time.sleep(12)
        except Exception as e:
            print(f"  [{char}] exc: {e} -> backoff 12s", flush=True)
            time.sleep(12)
    return None


for i, c in enumerate(chars):
    r = call(c)
    if r is not None:
        res[c] = r if r else {"unlisted": True}
    print(f"{i + 1}/{len(chars)} {c}", flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(3)

print(f"DONE total={len(res)}", flush=True)
