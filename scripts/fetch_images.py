# -*- coding: utf-8 -*-
"""
为 150 位艺术家的代表作抓取并核验图片。

来源优先级：
  1) The Met Open Access API         —— 权威元数据 + 高清原图
  2) Cleveland Museum of Art Open Access —— 权威元数据 + 高清原图
  3) WikiArt                          —— 覆盖率保底（含现代/当代、非西方）

产出：
  assets/img/<artistId>/portrait.jpg
  assets/img/<artistId>/w1.jpg … w5.jpg
  data/images.json
  data/_cache/*.json （原始检索缓存，可重复运行、断点续抓）
"""
import json, os, re, sys, time, unicodedata, hashlib, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from PIL import Image
import io

ROOT = r"C:\Users\JNPYY\WorkBuddy\2026-09-27-19-27-34\artists-db"
IMGDIR = os.path.join(ROOT, "assets", "img")
CACHE = os.path.join(ROOT, "data", "_cache")
os.makedirs(IMGDIR, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

MAX_SIDE = 1100
QUALITY = 82
LIMIT = None
ONLY = None
for a in sys.argv[1:]:
    if a.startswith("--limit="):
        LIMIT = int(a.split("=")[1])
    if a.startswith("--only="):
        ONLY = set(x for x in a.split("=", 1)[1].split(",") if x)

# 人工校正表：key = "<艺术家id>||<作品英文名>"
# ALIAS：优先在候选里寻找标题包含这些关键词的作品（修正同人异作误配）
ALIAS = {
    "pablo-picasso||Les Demoiselles d'Avignon": ["les demoiselles d avignon"],
    "georges-seurat||A Sunday Afternoon on the Island of La Grande Jatte":
        ["a sunday afternoon on the island of la grande jatte", "sunday afternoon on the island"],
    "ernst-ludwig-kirchner||Street, Berlin": ["street berlin", "berliner strasse", "street in berlin"],
    "el-lissitzky||Proun Room": ["proun room"],
    "jean-francois-millet||The Shepherdess": ["shepherdess"],
    "rosa-bonheur||The Sheep Market": ["sheep market", "market"],
    "sonia-delaunay||Simultaneous Blanket": ["blanket", "simultaneous"],
}
# REJECT：确认误配且无法可靠修正的，宁缺毋滥（改用版式化题名图版）
REJECT = {
    ("camille-pissarro", "Hoar Frost, the Effect of Snow"),
    ("helen-frankenthaler", "Blue Territory"),
    ("kathe-kollwitz", "War"),
    ("romare-bearden", "The Prevalence of Ritual: Tidings"),
    # WikiArt 未收录该作正图（版权/授权原因），或仅有习作稿：宁缺毋滥
    ("pablo-picasso", "Les Demoiselles d'Avignon"),
    ("georges-seurat", "A Sunday Afternoon on the Island of La Grande Jatte"),
}

lock = threading.Lock()
log_lines = []
def log(msg):
    with lock:
        log_lines.append(msg)
        print(msg, flush=True)

def get_json(url, timeout=25, tries=2):
    for i in range(tries):
        try:
            r = S.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.json()
        except Exception:
            time.sleep(0.6)
    return None

def get_text(url, timeout=30, tries=2):
    for i in range(tries):
        try:
            r = S.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.text
        except Exception:
            time.sleep(0.6)
    return None

# ---------------- 文本匹配 ----------------
def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

STOP = {"the","a","an","of","and","in","on","at","with","from","no","la","le","les","el","de","del","il","der","die","das","study","portrait","series"}

# 常见异名归一（艺术史术语的英文同义/异拼）
SYN = {
    "descent":"deposition","deposition":"descent","entombment":"deposition",
    "madonna":"virgin","virgin":"madonna",
    "judgement":"judgment","judgment":"judgement",
    "colour":"color","color":"colour",
    "grey":"gray","gray":"grey",
    "magi":"magi","adoration":"adoration",
    "arnolfini":"arnolfini",
    "selfportrait":"self","self":"selfportrait",
    "portrait":"portrait","portraits":"portrait",
    "annunciation":"annunciation","annunciate":"annunciation",
    "landscape":"landscape","view":"landscape","vue":"landscape",
    "peasant":"peasant","peasants":"peasant",
    "woman":"woman","women":"woman","lady":"woman",
    "man":"man","men":"man","gentleman":"man",
    "child":"child","children":"child",
    "still":"still","life":"live","lives":"live",
    "flowers":"flower","flower":"flowers","floral":"flower",
    "trees":"tree","tree":"trees",
    "houses":"house","house":"houses",
    "fishing":"fish","boats":"boat","boat":"boats",
    "river":"river","seine":"seine",
    "garden":"garden","eden":"paradise","paradise":"eden",
    "expulsion":"expulsion","banishment":"expulsion",
    "ghent":"ghent","altarpiece":"altar","altarpiece":"altarpiece",
    "resurrection":"resurrection","crucifixion":"crucifixion",
    "christ":"christ","jesus":"christ",
    "holy":"holy","sacred":"holy",
}

def toks(s, canon=True):
    out = set()
    for t in norm(s).split():
        if not t or t in STOP or len(t) <= 1: continue
        out.add(SYN.get(t, t) if canon else t)
    return out

def similarity(a, b):
    ta, tb = toks(a), toks(b)
    if not ta or not tb: return 0.0
    j = len(ta & tb) / len(ta | tb)
    na, nb = norm(a), norm(b)
    contain = 0.0
    if na and nb and (na in nb or nb in na) and min(len(na), len(nb)) > 6:
        contain = 0.92
    return max(j, contain)

def year_of(x):
    if x is None: return None
    m = re.search(r"(1[2-9]\d\d|20[0-2]\d)", str(x))
    return int(m.group(1)) if m else None

def score(target_title, target_year, cand_title, cand_year):
    """同一位艺术家名下的候选中评分：标题相似度 + 年代一致性加权。"""
    s = similarity(target_title, cand_title)
    ty, cy = year_of(target_year), year_of(cand_year)
    if ty and cy:
        d = abs(ty - cy)
        if d <= 2:   s += 0.20
        elif d <= 5: s += 0.10
        elif d <= 10: s += 0.02
        elif d > 30: s -= 0.20
    return s

def noise(title):
    t = norm(title)
    return any(k in t for k in ("after ", "copy of", "free copy", "reproduction", "from l artiste", "pictorum", "engraved by"))

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

# ---------------- WikiArt ----------------
WIKI_OVERRIDE = {
    "katsushika-hokusai": ["hokusai", "katsushika-hokusai"],
    "kitagawa-utamaro": ["kitagawa-utamaro", "utamaro"],
    "rembrandt-van-rijn": ["rembrandt", "rembrandt-van-rijn"],
    "el-greco": ["el-greco", "dom-nikos-theotokopoulos"],
    "francis-bacon": ["francis-bacon"],
    "josef-albers": ["josef-albers"],
    "man-ray": ["man-ray"],
    "claude-lorrain": ["claude-lorrain", "claude-gellee"],
    "titian": ["titian", "tiziano-vecelli"],
    "raphael": ["raphael", "raffaello-santi"],
    "michelangelo": ["michelangelo", "michelangelo-buonarroti"],
    "caravaggio": ["caravaggio", "michelangelo-merisi-da-caravaggio"],
    "yayoi-kusama": ["yayoi-kusama"],
    "leonardo-da-vinci": ["leonardo-da-vinci"],
    "diego-velazquez": ["diego-velazquez"],
    "camille-pissarro": ["camille-pissarro"],
    "willem-de-kooning": ["willem-de-kooning"],
    "georgia-okeeffe": ["georgia-okeeffe"],
    "edward-hopper": ["edward-hopper"],
    "zhu-da": ["bada-shanren", "zhu-da"],
    "qi-baishi": ["qi-baishi"],
    "xu-beihong": ["xu-beihong"],
    "gu-kaizhi": ["gu-kaizhi"],
    "fan-kuan": ["fan-kuan"],
    "ni-zan": ["ni-zan"],
    "el-anatsui": ["el-anatsui"],
    "tarsila-do-amaral": ["tarsila-do-amaral"],
    "amrita-sher-gil": ["amrita-sher-gil"],
    "william-kentridge": ["william-kentridge"],
    "shirin-neshat": ["shirin-neshat"],
}

def wiki_artist(meta):
    aid = meta["id"]
    cf = os.path.join(CACHE, "wiki_%s.json" % aid)
    if os.path.exists(cf):
        d = json.load(open(cf, encoding="utf-8"))
        return d
    cands = list(WIKI_OVERRIDE.get(aid, []))
    for src in (meta.get("name"), meta.get("wikiTitle")):
        if src:
            s = slugify(src)
            if s and s not in cands: cands.append(s)
            parts = slugify(src).split("-")
            if len(parts) > 1:
                s2 = "-".join(parts[-2:])
                if s2 not in cands: cands.append(s2)
    name_toks = toks(meta.get("name",""))
    result = {"slug": None, "portrait": None, "works": []}
    for slug in cands:
        if not slug: continue
        arr = get_json("https://www.wikiart.org/en/App/Painting/PaintingsByArtist?artistUrl=%s&json=2" % slug)
        if not isinstance(arr, list) or not arr: continue
        an = ""
        for it in arr:
            if isinstance(it, dict) and it.get("artistName"):
                an = it["artistName"]; break
        at = toks(an)
        if at and name_toks and not (at & name_toks):
            continue
        works = []
        for it in arr:
            if not isinstance(it, dict): continue
            u = it.get("image") or it.get("imageUrl") or ""
            t = it.get("title") or ""
            y = it.get("completitionYear") or it.get("year") or ""
            if u and t:
                works.append({"title": t, "url": u.split("!")[0], "year": str(y)})
        if not works: continue
        result["slug"] = slug
        result["works"] = works
        break
    if result["slug"]:
        j = get_json("https://www.wikiart.org/en/%s?json=2" % result["slug"])
        if isinstance(j, dict):
            p = j.get("image") or j.get("imageUrl")
            if p: result["portrait"] = p.split("!")[0]
    json.dump(result, open(cf, "w", encoding="utf-8"), ensure_ascii=False)
    return result

# ---------------- The Met ----------------
def met_artist(meta):
    aid = meta["id"]
    cf = os.path.join(CACHE, "met_%s.json" % aid)
    if os.path.exists(cf):
        return json.load(open(cf, encoding="utf-8"))
    out = []
    d = get_json("https://collectionapi.metmuseum.org/public/collection/v1/search"
                 "?hasImages=true&artistOrCulture=true&q=%s" % requests.utils.quote(meta["name"]))
    ids = (d or {}).get("objectIDs") or []
    ids = ids[:18]
    def one(oid):
        return get_json("https://collectionapi.metmuseum.org/public/collection/v1/objects/%d" % oid)
    if ids:
        with ThreadPoolExecutor(max_workers=4) as ex:
            for o in ex.map(one, ids):
                if not o: continue
                if not o.get("primaryImage"): continue
                out.append({"title": o.get("title") or "", "date": o.get("objectDate") or "",
                            "img": o.get("primaryImage"), "thumb": o.get("primaryImageSmall") or o.get("primaryImage"),
                            "credit": o.get("creditLine") or "", "acc": o.get("accessionNumber") or "",
                            "museum": "The Metropolitan Museum of Art",
                            "link": o.get("objectURL") or "", "artist": o.get("artistDisplayName") or ""})
    json.dump(out, open(cf, "w", encoding="utf-8"), ensure_ascii=False)
    return out

# ---------------- Cleveland ----------------
def cle_artist(meta):
    aid = meta["id"]
    cf = os.path.join(CACHE, "cle_%s.json" % aid)
    if os.path.exists(cf):
        return json.load(open(cf, encoding="utf-8"))
    out = []
    d = get_json("https://openaccess-api.clevelandart.org/api/artworks/?q=%s&has_image=1&limit=40"
                 % requests.utils.quote(meta["name"]))
    surn = toks(meta["name"])
    for it in (d or {}).get("data", []):
        imgs = it.get("images") or {}
        web = (imgs.get("web") or {}).get("url")
        pr = (imgs.get("print") or {}).get("url")
        if not web: continue
        creators = " ".join([str((c or {}).get("description","")) for c in (it.get("creators") or [])])
        if surn and toks(creators) and not (surn & toks(creators)):
            continue
        out.append({"title": it.get("title") or "", "date": it.get("creation_date") or "",
                    "img": web, "thumb": web, "hi": pr,
                    "credit": it.get("creditline") or "", "acc": it.get("accession_number") or "",
                    "museum": "克利夫兰艺术博物馆 (Cleveland Museum of Art)",
                    "link": it.get("url") or "", "artist": creators})
    json.dump(out, open(cf, "w", encoding="utf-8"), ensure_ascii=False)
    return out

# ---------------- 下载与压缩 ----------------
dl_lock = threading.Lock()
downloaded = {}

def fetch_image(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 2000:
        return True
    try:
        r = S.get(url, timeout=45)
        if r.status_code != 200 or len(r.content) < 3000:
            return False
        im = Image.open(io.BytesIO(r.content))
        if im.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            im = im.convert("RGBA")
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        w, h = im.size
        if max(w, h) > MAX_SIDE:
            k = MAX_SIDE / float(max(w, h))
            im = im.resize((max(1,int(w*k)), max(1,int(h*k))), Image.LANCZOS)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        return True
    except Exception:
        return False

# ---------------- 主流程 ----------------
db = json.load(open(os.path.join(ROOT, "data", "artists.json"), encoding="utf-8"))
artists = db["artists"]
if ONLY:
    artists = [a for a in artists if a["id"] in ONLY]
elif LIMIT:
    artists = artists[:LIMIT]

result = {}
if os.path.exists(os.path.join(ROOT, "data", "images.json")):
    try:
        result = json.load(open(os.path.join(ROOT, "data", "images.json"), encoding="utf-8"))
    except Exception:
        result = {}

stat = {"portrait": 0, "works_total": 0, "works_img": 0, "met": 0, "cle": 0, "wiki": 0, "none": 0}

def process(meta):
    aid = meta["id"]
    works = meta.get("works") or []
    if not works: return
    wiki = wiki_artist(meta)
    met = met_artist(meta)
    cle = cle_artist(meta)
    rec = result.get(aid, {})
    rec.setdefault("id", aid)
    rec.setdefault("name", meta.get("zh") or meta.get("name"))
    rec["works"] = rec.get("works") or [{} for _ in works]
    while len(rec["works"]) < len(works):
        rec["works"].append({})

    # 肖像
    pdest = os.path.join(IMGDIR, aid, "portrait.jpg")
    if not os.path.exists(pdest) or os.path.getsize(pdest) < 2000:
        purl = wiki.get("portrait")
        if purl and fetch_image(purl, pdest):
            rec["portrait"] = "assets/img/%s/portrait.jpg" % aid
            rec["portraitSrc"] = "WikiArt"
        else:
            for m in (met + cle):
                if "self-portrait" in norm(m["title"]):
                    if fetch_image(m.get("thumb") or m["img"], pdest):
                        rec["portrait"] = "assets/img/%s/portrait.jpg" % aid
                        rec["portraitSrc"] = m["museum"]
                        break

    for i, w in enumerate(works):
        te = w.get("titleEn") or w.get("title") or ""
        tc = w.get("title") or ""
        slot = rec["works"][i] or {}
        slot.setdefault("title", tc)
        slot.setdefault("titleEn", te)
        slot.setdefault("year", w.get("year"))
        dest = os.path.join(IMGDIR, aid, "w%d.jpg" % (i+1))
        rel = "assets/img/%s/w%d.jpg" % (aid, i+1)
        if (aid, te) in REJECT:
            if os.path.exists(dest):
                try: os.remove(dest)
                except Exception: pass
            slot["img"] = None
            slot["rejected"] = True
            rec["works"][i] = slot
            with lock: stat["none"] += 1
            continue
        if os.path.exists(dest) and os.path.getsize(dest) > 2000:
            slot["img"] = rel
            rec["works"][i] = slot
            continue
        best = None; best_score = 0.0; src = None
        for m in met:
            if noise(m["title"]): continue
            s = score(te, slot.get("year"), m["title"], m.get("date"))
            if s > best_score: best_score, best, src = s, m, "met"
        for c in cle:
            if noise(c["title"]): continue
            s = score(te, slot.get("year"), c["title"], c.get("date")) * 1.02
            if s > best_score: best_score, best, src = s, c, "cle"
        if best and best_score >= 0.62:
            if fetch_image(best.get("thumb") or best["img"], dest):
                slot.update({"img": rel, "museum": best["museum"], "credit": best.get("credit"),
                             "acc": best.get("acc"), "link": best.get("link"),
                             "date": best.get("date"), "matchedTitle": best["title"],
                             "src": "Met" if src == "met" else "Cleveland",
                             "hi": best.get("hi") or best.get("img")})
                rec["works"][i] = slot
                with lock:
                    stat["met" if src == "met" else "cle"] += 1
                    stat["works_img"] += 1
                continue
        # WikiArt 兜底（同一艺术家名下匹配，阈值可放宽）
        bw = None; bs = 0.0
        aliases = ALIAS.get("%s||%s" % (aid, te))
        if aliases:
            for m in wiki.get("works", []):
                nt = norm(m["title"])
                for al in aliases:
                    if al and al in nt:
                        bw, bs = m, 9.0
                        break
                if bs > 8:
                    break
        if bw is None:
            for m in wiki.get("works", []):
                s = score(te, slot.get("year"), m["title"], m.get("year"))
                if s > bs: bs, bw = s, m
        if bw and bs >= 0.48:
            if fetch_image(bw["url"], dest):
                slot.update({"img": rel, "museum": "WikiArt 图像资料库", "src": "WikiArt",
                             "link": "https://www.wikiart.org/en/%s" % (wiki.get("slug") or ""),
                             "matchedTitle": bw["title"], "hi": bw["url"]})
                rec["works"][i] = slot
                with lock:
                    stat["wiki"] += 1
                    stat["works_img"] += 1
                continue
        slot["img"] = None
        rec["works"][i] = slot
        with lock:
            stat["none"] += 1

    result[aid] = rec
    with lock:
        stat["works_total"] += len(works)
        if rec.get("portrait"): stat["portrait"] += 1

t0 = time.time()
with ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(process, m): m["id"] for m in artists}
    done = 0
    for f in as_completed(futs):
        done += 1
        try:
            f.result()
        except Exception as e:
            log("!! %s 失败: %r" % (futs[f], e))
        if done % 10 == 0:
            log("进度 %d/%d  用时 %.0fs  已配图作品 %d" % (done, len(artists), time.time()-t0, stat["works_img"]))
            json.dump(result, open(os.path.join(ROOT, "data", "images.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)

json.dump(result, open(os.path.join(ROOT, "data", "images.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
log("\n=== 完成 ===")
log("肖像 %d/%d" % (stat["portrait"], len(artists)))
log("作品配图 %d / %d (%.0f%%)" % (stat["works_img"], stat["works_total"],
                                   100.0*stat["works_img"]/max(1,stat["works_total"])))
log("来源分布: Met=%d  Cleveland=%d  WikiArt=%d  未配=%d" %
    (stat["met"], stat["cle"], stat["wiki"], stat["none"]))
log("总用时 %.0f 秒" % (time.time()-t0))
open(os.path.join(CACHE, "fetch_log.txt"), "w", encoding="utf-8").write("\n".join(log_lines))
