import json, os
ROOT = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
C = os.path.join(ROOT, "data", "_cache")
for f in sorted(os.listdir(C)):
    if f.startswith(("met_","cle_","wiki_")):
        d = json.load(open(os.path.join(C,f), encoding="utf-8"))
        n = len(d) if isinstance(d, list) else len(d.get("works",[]))
        print("%-34s n=%d" % (f, n))
        if f.startswith("wiki_") and isinstance(d, dict):
            print("    slug=%s portrait=%s" % (d.get("slug"), bool(d.get("portrait"))))
            for w in d.get("works",[])[:6]: print("      -", w["title"][:50], "|", w["year"])
        if f.startswith(("met_","cle_")) and isinstance(d, list):
            for w in d[:6]: print("      -", w["title"][:50], "|", w.get("date"))
print("\n--- images.json ---")
im = json.load(open(os.path.join(ROOT,"data","images.json"), encoding="utf-8"))
for k, v in im.items():
    print(k, "portrait=", v.get("portrait"))
    for w in v.get("works", []):
        print("   ", (w.get("titleEn") or "")[:34], "->", w.get("img"), "|", w.get("matchedTitle","")[:40], "|", w.get("src"))
