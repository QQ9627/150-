import json, os, collections
root = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
d = json.load(open(os.path.join(root,"data","roster.json"), encoding="utf-8"))
a = d["artists"]
print("count:", len(a))
ids = [x["id"] for x in a]
dup = [k for k,v in collections.Counter(ids).items() if v>1]
print("dup ids:", dup)
print("periods:", collections.Counter(x["period"] for x in a))
print("regions:", collections.Counter(x["region"] for x in a))
print("movements:", len(set(x["movement"] for x in a)))
med = collections.Counter()
for x in a:
    for m in x["mediums"]: med[m]+=1
print("mediums:", dict(med))
# check taxonomy coverage
tax = d["taxonomy"]
bad_p = [x["id"] for x in a if x["period"] not in tax["period"]]
bad_r = [x["id"] for x in a if x["region"] not in tax["region"]]
bad_m = sorted({m for x in a for m in x["mediums"] if m not in tax["medium"]})
print("bad period:", bad_p)
print("bad region:", bad_r)
print("bad medium:", bad_m)
