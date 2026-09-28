# -*- coding: utf-8 -*-
import json, os, urllib.request
BASE = "http://127.0.0.1:8931/"
ROOT = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"

def code(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=15) as r:
            return r.status, len(r.read())
    except Exception as e:
        return "ERR", repr(e)[:60]

paths = ["index.html", "artist.html", "assets/css/style.css", "assets/js/app.js",
         "assets/js/detail.js", "data/db-index.js", "data/db-entries.js",
         "README.md", "docs/ENTRY_SCHEMA.md"]
print("--- 关键资源 ---")
for p in paths:
    s, n = code(p)
    print("  %-28s %-5s %s" % (p, s, n if isinstance(n, int) else n))

# 抽样检查图版文件是否真实存在且可达
idx = json.load(open(os.path.join(ROOT, "data", "index.json"), encoding="utf-8"))
arts = idx["artists"]
sample = [a for a in arts if a.get("thumb")][:8]
print("\n--- 图版抽样（来自 data/index.json 的 thumb 路径）---")
bad = 0
for a in sample:
    s, n = code(a["thumb"])
    flag = "OK" if s == 200 else "缺失"
    if s != 200: bad += 1
    print("  %-12s %-46s %s %s" % (a["zh"][:10], a["thumb"][:44], s, n if isinstance(n, int) else ""))
print("\n抽样不可达：%d / %d" % (bad, len(sample)))

# 统计磁盘上的图版
tot = 0; size = 0
for dp, _, fs in os.walk(os.path.join(ROOT, "assets", "img")):
    for f in fs:
        tot += 1; size += os.path.getsize(os.path.join(dp, f))
print("磁盘图版文件 %d 个，共 %.0f MB" % (tot, size / 1024 / 1024))
