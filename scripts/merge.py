# -*- coding: utf-8 -*-
"""合并 10 批 × 3 片词条，用 roster.json 作为元数据唯一真源，输出 artists.json / index.json。"""
import json, os, glob, collections

root = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
roster = json.load(open(os.path.join(root, "data", "roster.json"), encoding="utf-8"))
arts = roster["artists"]
order = [a["id"] for a in arts]
meta = {a["id"]: a for a in arts}

META_KEYS = ["id","name","zh","birth","death","country","region","period","movement","mediums"]

files = sorted(glob.glob(os.path.join(root, "data", "artists", "part-*.json")))
print("发现分片文件 %d 个" % len(files))
entries = {}
problems = []
drift = []
for f in files:
    try:
        arr = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        problems.append("%s JSON 解析失败: %r" % (os.path.basename(f), e)); continue
    if not isinstance(arr, list):
        problems.append("%s 不是数组" % os.path.basename(f)); continue
    for e in arr:
        eid = e.get("id")
        if eid not in meta:
            problems.append("%s 含未知 id: %s" % (os.path.basename(f), eid)); continue
        if eid in entries:
            problems.append("重复 id: %s (%s)" % (eid, os.path.basename(f)))
        # 记录元数据漂移并被真源覆盖
        for k in META_KEYS:
            if k in e and e[k] != meta[eid].get(k):
                drift.append("%s.%s: 写作=%r → 真源=%r" % (eid, k, e[k], meta[eid].get(k)))
        for k in META_KEYS:
            e[k] = meta[eid].get(k)
        entries[eid] = e

missing = [i for i in order if i not in entries]
print("合并条目 %d / %d；缺失 %d" % (len(entries), len(order), len(missing)))
if missing: print("缺失 id:", missing[:40])
if drift:
    print("\n元数据漂移已修正 %d 处（示例前 12）:" % len(drift))
    for d in drift[:12]: print("  - " + d)
if problems:
    print("\n问题:")
    for p in problems[:40]: print("  - " + p)

merged = [entries[i] for i in order if i in entries]
out = {
    "meta": {"title": roster["meta"]["title"], "count": len(merged),
             "taxonomy": roster["taxonomy"]},
    "artists": merged,
}
json.dump(out, open(os.path.join(root, "data", "artists.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 轻量索引（列表页 / 筛选用）
index = []
for e in merged:
    index.append({
        "id": e["id"], "name": e["name"], "zh": e["zh"],
        "birth": e.get("birth"), "death": e.get("death"), "datesZh": e.get("datesZh"),
        "country": e.get("country"), "region": e.get("region"), "period": e.get("period"),
        "movement": e.get("movement"), "movementTags": e.get("movementTags") or [],
        "mediums": e.get("mediums") or [], "tagline": e.get("tagline"),
        "works": [w.get("title","") for w in (e.get("works") or [])],
        "workTitlesEn": [w.get("titleEn","") for w in (e.get("works") or [])],
        "thumb": (e.get("images") or {}).get("thumb"),
    })
json.dump({"taxonomy": roster["taxonomy"], "artists": index},
          open(os.path.join(root, "data", "index.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 统计
tot = 0
for e in merged:
    n = sum(len(e.get(k) or []) for k in ("life","style","legacy","controversy"))
    n += len(e.get("statement") or "") + len(e.get("motifs") or "")
    n += sum(len((e.get("evolution") or {}).get(k) or "") for k in ("early","middle","late"))
    for w in (e.get("works") or []):
        n += sum(len(w.get(f) or "") for f in ("title","collection","background","scene","innovation","significance"))
    tot += n
print("\n总字数约 %d 字，平均每条约 %d 字" % (tot, tot//max(1,len(merged))))
print("输出: data/artists.json, data/index.json")
