# -*- coding: utf-8 -*-
import json, os, collections
root = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
p = os.path.join(root, "data", "roster.json")
d = json.load(open(p, encoding="utf-8"))

# 1) 统一时期词表：去掉 1914–1945，归入 1925–1945 / 1900–1925
d["taxonomy"]["period"] = ["14世纪及以前","15世纪","16世纪","17世纪","18世纪",
                           "19世纪前期","19世纪后期","1900–1925","1925–1945","1945–1970","1970年以后"]
early = {"marcel-duchamp"}
for a in d["artists"]:
    if a["period"] == "1914–1945":
        a["period"] = "1900–1925" if a["id"] in early else "1925–1945"

# 2) 精简 5 位（风格/流派与同列表内其他条目高度重叠），保证 150 位整
cut = {"andre-derain","francis-picabia","theo-van-doesburg","canaletto","georges-de-la-tour"}
before = len(d["artists"])
d["artists"] = [a for a in d["artists"] if a["id"] not in cut]

# 3) 补入全球视野条目
add = [
 {"id":"tarsila-do-amaral","name":"Tarsila do Amaral","zh":"塔西拉·杜·阿马拉尔","birth":1886,"death":1973,
  "country":"巴西","region":"拉丁美洲","period":"1925–1945","movement":"现代主义","mediums":["油画","素描·手稿"],"wikiTitle":"Tarsila do Amaral"},
 {"id":"el-anatsui","name":"El Anatsui","zh":"埃尔·阿纳楚","birth":1944,"death":None,
  "country":"加纳／尼日利亚","region":"非洲","period":"1970年以后","movement":"当代艺术","mediums":["雕塑","装置"],"wikiTitle":"El Anatsui"},
]
d["artists"].extend(add)
d["meta"]["count"] = len(d["artists"])

json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

a = d["artists"]
print("before=%d after=%d" % (before, len(a)))
print("periods:", dict(collections.Counter(x["period"] for x in a)))
print("regions:", dict(collections.Counter(x["region"] for x in a)))
print("bad period:", [x["id"] for x in a if x["period"] not in d["taxonomy"]["period"]])
print("dup:", [k for k,v in collections.Counter(x["id"] for x in a).items() if v>1])
