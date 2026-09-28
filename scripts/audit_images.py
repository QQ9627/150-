# -*- coding: utf-8 -*-
"""审计图片匹配质量：列出可疑匹配（目标标题与命中标题差异大）与未配图作品。"""
import json, os, sys, difflib
ROOT = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
img = json.load(open(os.path.join(ROOT, "data", "images.json"), encoding="utf-8"))
arts = {a["id"]: a for a in json.load(open(os.path.join(ROOT, "data", "artists.json"),
                                            encoding="utf-8"))["artists"]}

susp, miss = [], []
for aid, rec in img.items():
    works = (arts.get(aid) or {}).get("works") or []
    for i, m in enumerate(rec.get("works") or []):
        if i >= len(works): continue
        tgt = works[i].get("titleEn") or works[i].get("title") or ""
        if not (m or {}).get("img"):
            miss.append((aid, arts[aid]["zh"], tgt)); continue
        hit = (m or {}).get("matchedTitle") or ""
        r = difflib.SequenceMatcher(None, tgt.lower(), hit.lower()).ratio()
        if r < 0.55:
            susp.append((round(r,2), arts[aid]["zh"], tgt, hit, m.get("src"), m.get("year") or works[i].get("year"), m.get("date") or ""))

mode = sys.argv[1] if len(sys.argv) > 1 else "susp"
if mode == "susp":
    susp.sort()
    print("可疑匹配（相似度<0.55）共 %d 条：\n" % len(susp))
    for r, zh, t, h, s, y1, y2 in susp[:80]:
        print("%.2f %-12s | %-42s => %-44s | %s %s/%s" % (r, zh[:11], t[:41], h[:43], s, y1, y2))
else:
    print("未配图作品共 %d 条：\n" % len(miss))
    cur = None
    for aid, zh, t in miss:
        if aid != cur: print("\n【%s】" % zh); cur = aid
        print("   -", t[:70])
