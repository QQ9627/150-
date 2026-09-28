# -*- coding: utf-8 -*-
"""校验词条 JSON 文件是否符合 ENTRY_SCHEMA。
用法: python check_part.py <file.json> [more.json ...]
也接受 {'entries': [...]} 或 {'artists': [...]} 包裹形式，或裸数组。"""
import json, os, sys

REQ_STR = ["id","name","zh","country","region","period","movement","tagline","statement","motifs"]
REQ_INT = ["birth"]
WORK_FIELDS = ["title","titleEn","year","collection","background","scene","innovation","significance"]
MIN = {"life":6,"style":6,"works":3,"legacy":5,"controversy":4}
MAX = {"life":9,"style":8,"works":5,"legacy":7,"controversy":6}
EQUAL = ["early","middle","late"]

def load(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, dict):
        for k in ("entries","artists","data"):
            if k in d and isinstance(d[k], list):
                return d[k]
        return [d]
    return d

def check(e, errs, warns):
    aid = e.get("id","<no-id>")
    def E(m): errs.append("%s: %s" % (aid, m))
    def W(m): warns.append("%s: %s" % (aid, m))
    for k in REQ_STR:
        if not isinstance(e.get(k), str) or not e[k].strip(): E("缺少字符串字段 %s" % k)
    for k in REQ_INT:
        if not isinstance(e.get(k), int): E("字段 %s 应为整数年份" % k)
    if e.get("death") is not None and not isinstance(e.get("death"), int):
        E("death 应为整数或 null")
    for k, lo in MIN.items():
        if k == "works":
            v = e.get(k)
            if not isinstance(v, list): E("works 应为数组"); continue
            if not (lo <= len(v) <= MAX[k]): E("works 应有 %d–%d 件，现有 %d" % (lo, MAX[k], len(v)))
            for i, w in enumerate(v):
                if not isinstance(w, dict): E("works[%d] 不是对象" % i); continue
                for f in WORK_FIELDS:
                    if not isinstance(w.get(f), str) or not w[f].strip():
                        E("works[%d] 缺少 %s" % (i, f))
                if w.get("titleEn","").strip() == w.get("title","").strip():
                    W("works[%d] titleEn 应与中文 title 不同" % i)
        else:
            v = e.get(k)
            if not isinstance(v, list): E("%s 应为数组" % k); continue
            if not (lo <= len(v) <= MAX[k]): E("%s 应有 %d–%d 条，现有 %d" % (k, lo, MAX[k], len(v)))
            for i, s in enumerate(v):
                if not isinstance(s, str) or not s.strip(): E("%s[%d] 为空" % (k, i))
                elif len(s) < 30: W("%s[%d] 过短（%d 字）" % (k, i, len(s)))
    ev = e.get("evolution")
    if not isinstance(ev, dict): E("evolution 缺失或非对象")
    else:
        for k in EQUAL:
            s = ev.get(k)
            if not isinstance(s, str) or not s.strip(): E("evolution.%s 缺失" % k)
            elif len(s) < 100: W("evolution.%s 偏短（%d 字）" % (k, len(s)))
    if isinstance(e.get("movementTags"), list) is False: W("movementTags 建议为数组")
    if isinstance(e.get("mediums"), list) is False: W("mediums 建议为数组")
    total = 0
    for k in ("life","style","legacy","controversy"): total += len(e.get(k) or [])
    total += len(e.get("statement") or "") + len(e.get("motifs") or "")
    for k in EQUAL: total += len((e.get("evolution") or {}).get(k) or "")
    for w in (e.get("works") or []):
        total += sum(len(w.get(f) or "") for f in WORK_FIELDS[:1]+WORK_FIELDS[4:])
    if total < 1400: W("整条总字数偏少（约 %d 字），目标 1800 字以上" % total)
    return total

def main():
    all_err, all_warn, n, tots = [], [], 0, []
    for p in sys.argv[1:]:
        if not os.path.exists(p): all_err.append("%s: 文件不存在" % p); continue
        try:
            entries = load(p)
        except Exception as ex:
            all_err.append("%s: JSON 解析失败 -> %r" % (p, ex)); continue
        for e in entries:
            if not isinstance(e, dict): all_err.append("%s: 条目非对象" % p); continue
            n += 1; tots.append(check(e, all_err, all_warn))
    print("检查条目数: %d" % n)
    if tots: print("平均每条约 %d 字" % (sum(tots)//len(tots)))
    if all_warn:
        print("\n[WARN] %d 项" % len(all_warn))
        for w in all_warn[:40]: print("  - " + w)
    if all_err:
        print("\n[ERROR] %d 项" % len(all_err))
        for e in all_err[:60]: print("  - " + e)
        sys.exit(1)
    print("\nOK: 结构校验通过")

if __name__ == "__main__":
    main()
