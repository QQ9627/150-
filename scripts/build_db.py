# -*- coding: utf-8 -*-
"""把 data/*.json 打包成浏览器可直接 <script> 引用的 data/db-index.js / data/db-entries.js。
这样站点在 file:// 与 http:// 下都能工作（不依赖 fetch + CORS）。"""
import json, os, datetime

ROOT = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
D = os.path.join(ROOT, "data")

artists = json.load(open(os.path.join(D, "artists.json"), encoding="utf-8"))
taxonomy = artists["meta"]["taxonomy"]
entries = artists["artists"]

imgp = os.path.join(D, "images.json")
images = json.load(open(imgp, encoding="utf-8")) if os.path.exists(imgp) else {}

# ---- 合并图片进词条 ----
for e in entries:
    rec = images.get(e["id"]) or {}
    e["portrait"] = rec.get("portrait")
    e["portraitSrc"] = rec.get("portraitSrc")
    imgs = rec.get("works") or []
    for i, w in enumerate(e.get("works") or []):
        m = imgs[i] if i < len(imgs) else {}
        w["image"] = (m or {}).get("img")
        w["museum"] = (m or {}).get("museum")
        w["credit"] = (m or {}).get("credit")
        w["accession"] = (m or {}).get("acc")
        w["sourceLink"] = (m or {}).get("link")
        w["hiRes"] = (m or {}).get("hi")
        w["imageSrc"] = (m or {}).get("src")
        w["matchedTitle"] = (m or {}).get("matchedTitle")

# ---- 索引 ----
index = []
for e in entries:
    thumb = e.get("portrait")
    if not thumb:
        for w in (e.get("works") or []):
            if w.get("image"): thumb = w["image"]; break
    index.append({
        "id": e["id"], "name": e["name"], "zh": e["zh"],
        "birth": e.get("birth"), "death": e.get("death"), "datesZh": e.get("datesZh"),
        "country": e.get("country"), "region": e.get("region"), "period": e.get("period"),
        "movement": e.get("movement"), "movementTags": e.get("movementTags") or [],
        "mediums": e.get("mediums") or [], "tagline": e.get("tagline"),
        "thumb": thumb, "works": [w.get("title", "") for w in (e.get("works") or [])],
        "imgCount": sum(1 for w in (e.get("works") or []) if w.get("image")),
        "workCount": len(e.get("works") or []),
    })

# 流派筛选词表：只用受控的 movement 主值；自由标签 movementTags 仅参与全文检索与展示
movements = sorted({e.get("movement") for e in entries if e.get("movement")},
                   key=lambda k: 0)

def entry_chars(e):
    n = sum(len(x or "") for x in (e.get("life") or []))
    n += sum(len(x or "") for x in (e.get("style") or []))
    n += sum(len(x or "") for x in (e.get("legacy") or []))
    n += sum(len(x or "") for x in (e.get("controversy") or []))
    n += len(e.get("statement") or "") + len(e.get("motifs") or "") + len(e.get("tagline") or "")
    ev = e.get("evolution") or {}
    n += sum(len(ev.get(k) or "") for k in ("early", "middle", "late"))
    for w in (e.get("works") or []):
        n += sum(len(w.get(f) or "") for f in
                 ("title", "titleEn", "collection", "background", "scene", "innovation", "significance"))
    return n

WORDS = sum(entry_chars(e) for e in entries)

WORDS = 0
for e in entries:
    n = sum(len(x) for x in (e.get("life") or []))
    n += sum(len(x) for x in (e.get("style") or []))
    n += sum(len(x) for x in (e.get("legacy") or []))
    n += sum(len(x) for x in (e.get("controversy") or []))
    n += len(e.get("statement") or "") + len(e.get("motifs") or "")
    n += sum(len((e.get("evolution") or {}).get(k) or "") for k in ("early", "middle", "late"))
    for w in (e.get("works") or []):
        n += sum(len(w.get(f) or "") for f in ("background", "scene", "innovation", "significance"))
        n += len(w.get("title") or "")
    WORDS += n

meta = {
    "title": "对艺术史产生重大影响的 150 位艺术家",
    "count": len(entries),
    "builtAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "words": WORDS,
    "avgWords": WORDS // max(1, len(entries)),
    "words": WORDS,
    "avgWords": WORDS // max(1, len(entries)),
    "imgStats": {
        "portraits": sum(1 for e in entries if e.get("portrait")),
        "works": sum(1 for e in entries for w in (e.get("works") or []) if w.get("image")),
        "worksTotal": sum(len(e.get("works") or []) for e in entries),
    },
}

with open(os.path.join(D, "db-index.js"), "w", encoding="utf-8") as f:
    f.write("/* 由 scripts/build_db.py 生成，请勿手改。数据源：data/*.json */\n")
    f.write("window.ARTDB = window.ARTDB || {};\n")
    f.write("window.ARTDB.taxonomy = %s;\n" % json.dumps(taxonomy, ensure_ascii=False))
    f.write("window.ARTDB.movements = %s;\n" % json.dumps(movements, ensure_ascii=False))
    f.write("window.ARTDB.meta = %s;\n" % json.dumps(meta, ensure_ascii=False))
    f.write("window.ARTDB.index = %s;\n" % json.dumps(index, ensure_ascii=False))

with open(os.path.join(D, "db-entries.js"), "w", encoding="utf-8") as f:
    f.write("/* 由 scripts/build_db.py 生成，请勿手改。数据源：data/artists.json + data/images.json */\n")
    f.write("window.ARTDB = window.ARTDB || {};\n")
    f.write("window.ARTDB.entries = {")
    f.write(",".join('%s:%s' % (json.dumps(e["id"]), json.dumps(e, ensure_ascii=False)) for e in entries))
    f.write("};\n")

# 同步一份 taxonomy.json 便于外部使用
json.dump({"taxonomy": taxonomy, "movements": movements, "meta": meta},
          open(os.path.join(D, "taxonomy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 同步 index.json（含图版缩略图路径，供外部程序 / 检索脚本直接使用）
json.dump({"taxonomy": taxonomy, "movements": movements, "meta": meta, "artists": index},
          open(os.path.join(D, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

sz1 = os.path.getsize(os.path.join(D, "db-index.js")) / 1024.0
sz2 = os.path.getsize(os.path.join(D, "db-entries.js")) / 1024.0
print("db-index.js   %.0f KB  (%d 位)" % (sz1, len(index)))
print("db-entries.js %.0f KB" % sz2)
print("图片：肖像 %d/%d，作品 %d/%d" % (meta["imgStats"]["portraits"], len(entries),
                                        meta["imgStats"]["works"], meta["imgStats"]["worksTotal"]))
print("流派词表 %d 个" % len(movements))
