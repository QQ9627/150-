# -*- coding: utf-8 -*-
import json, os, re, unicodedata, sys
sys.path.insert(0, os.path.join(r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db","scripts"))
ROOT = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
import importlib.util
spec = importlib.util.spec_from_file_location("fi", os.path.join(ROOT,"scripts","fetch_images.py"))
# 只取匹配函数：直接复制核心逻辑，避免执行主流程
def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+"," ",s)
    return re.sub(r"\s+"," ",s).strip()
STOP = {"the","a","an","of","and","in","on","at","with","from","no","la","le","les","el","de","del","il","der","die","das","study","portrait","series"}
SYN = {"descent":"deposition","deposition":"descent","entombment":"deposition","madonna":"virgin","virgin":"madonna",
"judgement":"judgment","judgment":"judgement","colour":"color","color":"colour","grey":"gray","gray":"grey",
"selfportrait":"self","self":"selfportrait","portraits":"portrait","landscape":"landscape","view":"landscape","vue":"landscape",
"peasants":"peasant","women":"woman","lady":"woman","men":"man","gentleman":"man","children":"child",
"life":"live","lives":"live","flowers":"flower","flower":"flowers","floral":"flower","trees":"tree","tree":"trees",
"houses":"house","house":"houses","fishing":"fish","boats":"boat","boat":"boats","eden":"paradise","paradise":"eden",
"banishment":"expulsion","altarpiece":"altar","jesus":"christ","sacred":"holy"}
def toks(s):
    return {SYN.get(t,t) for t in norm(s).split() if t and t not in STOP and len(t)>1}
def sim(a,b):
    ta,tb=toks(a),toks(b)
    if not ta or not tb: return 0.0
    j=len(ta&tb)/len(ta|tb)
    na,nb=norm(a),norm(b)
    c=0.92 if (na and nb and (na in nb or nb in na) and min(len(na),len(nb))>6) else 0.0
    return max(j,c)

arts = {a["id"]: a for a in json.load(open(os.path.join(ROOT,"data","artists.json"),encoding="utf-8"))["artists"]}
img = json.load(open(os.path.join(ROOT,"data","images.json"),encoding="utf-8"))
buckets = {}
rows=[]
for aid, rec in img.items():
    works = (arts.get(aid) or {}).get("works") or []
    for i,m in enumerate(rec.get("works") or []):
        if i>=len(works) or not (m or {}).get("img"): continue
        tgt = works[i].get("titleEn") or ""
        hit = m.get("matchedTitle") or ""
        s = sim(tgt,hit)
        rows.append((s, aid, arts[aid]["zh"], tgt, hit, m.get("src")))
        b = round(s,1)
        buckets[b]=buckets.get(b,0)+1
print("相似度分布（已配图 %d 条）："%len(rows))
for b in sorted(buckets): print("   %.1f : %d" % (b,buckets[b]))
for th in (0.4,0.45,0.5,0.55,0.6,0.65,0.7):
    keep=sum(1 for r in rows if r[0]>=th)
    print("阈值 %.2f → 保留 %d 条 (%.0f%%), 放弃 %d 条" % (th,keep,100*keep/len(rows),len(rows)-keep))
print("\n低于 0.55 的明细（这些是需要人工判断的）：")
for s,aid,zh,t,h,src in sorted(rows):
    if s < 0.55:
        print("  %.2f %-12s %-40s => %s" % (s, zh[:11], t[:39], h[:52]))
