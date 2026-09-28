# -*- coding: utf-8 -*-
"""为人工校正的艺术家清空既有图版与记录，以便 fetch_images.py --only 重新匹配。"""
import json, os, shutil
ROOT = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
TARGETS = ["pablo-picasso","georges-seurat","ernst-ludwig-kirchner","el-lissitzky",
           "jean-francois-millet","rosa-bonheur","sonia-delaunay",
           "camille-pissarro","helen-frankenthaler","kathe-colwitz",
           "kathe-kollwitz","romare-bearden"]
p = os.path.join(ROOT, "data", "images.json")
d = json.load(open(p, encoding="utf-8"))
for t in TARGETS:
    if t in d:
        del d[t]
        print("移除记录:", t)
    dirp = os.path.join(ROOT, "assets", "img", t)
    if os.path.isdir(dirp):
        shutil.rmtree(dirp, ignore_errors=True)
        print("删除图版目录:", t)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("剩余记录:", len(d))
