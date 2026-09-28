# -*- coding: utf-8 -*-
"""把 roster.json 切成 N 个写作批次，便于并行撰写与后续补全。"""
import json, os, math, sys

root = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10   # 批次数
roster = json.load(open(os.path.join(root, "data", "roster.json"), encoding="utf-8"))
arts = roster["artists"]
size = math.ceil(len(arts) / N)
outdir = os.path.join(root, "data", "batches")
os.makedirs(outdir, exist_ok=True)
manifest = []
for i in range(N):
    chunk = arts[i*size:(i+1)*size]
    if not chunk:
        continue
    bid = "%02d" % (i+1)
    payload = {"batchId": bid, "slots": [[o, o+size] for o in [i*size]][0] if False else None,
               "artists": chunk}
    payload.pop("slots", None)
    json.dump(payload, open(os.path.join(outdir, "batch-%s.json" % bid), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    manifest.append({"batchId": bid, "count": len(chunk),
                     "ids": [x["id"] for x in chunk],
                     "first": chunk[0]["zh"], "last": chunk[-1]["zh"]})
json.dump(manifest, open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for m in manifest:
    print("batch-%s  %2d 位  %s … %s" % (m["batchId"], m["count"], m["first"], m["last"]))
print("total:", sum(m["count"] for m in manifest))
