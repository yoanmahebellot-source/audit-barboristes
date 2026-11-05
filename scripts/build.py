#!/usr/bin/env python3
"""Génère docs/index.html (version client) à partir de data/scans/*.json.

  python3 scripts/build.py build            régénère la page
  python3 scripts/build.py add <doc.json>   ajoute/remplace un relevé complet
                                            (ne garde que les champs destinés au client)
                                            puis régénère la page
"""
import json, sys, glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_NOTE = ("Une note 2 sur ChatGPT et Gemini suppose un lien visible vers lesbarboristes.fr : "
                "les sources repliées peuvent faire sous-estimer les résultats. Les cases hachurées n'ont pas été mesurées.")

def clean(doc):
    """Champs client uniquement : jamais de concurrents, de notes internes ni d'incohérences."""
    out = {k: doc[k] for k in ("month", "label", "date", "kind") if k in doc}
    if doc.get("best"):
        out["best"] = doc["best"]
    out["footnote"] = doc.get("client_footnote") or DEFAULT_NOTE
    out["actions"] = [[str(a[0]), str(a[1])] for a in doc.get("actions", [])][:5]
    out["rows"] = [{"n": int(r["n"]), "s": r["s"]} for r in doc.get("rows", [])]
    return out

def build():
    scans = []
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "scans", "*.json"))):
        scans.append(json.load(open(p, encoding="utf-8")))
    queries = json.load(open(os.path.join(ROOT, "data", "queries.json"), encoding="utf-8"))
    tpl = open(os.path.join(ROOT, "scripts", "template.html"), encoding="utf-8").read()
    html = tpl.replace("__QUERIES__", json.dumps(queries, ensure_ascii=False)) \
              .replace("__SCANS__", json.dumps(scans, ensure_ascii=False).replace("</", "<\\/"))
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8").write(html)
    print("docs/index.html régénéré :", len(scans), "relevé(s)")

def add(path):
    doc = json.load(open(path, encoding="utf-8"))
    m = re.match(r"(\d{4})-(\d{2})-\d{2}$", doc.get("date", ""))
    if not m:
        sys.exit("date manquante ou invalide (AAAA-MM-JJ)")
    dest = os.path.join(ROOT, "data", "scans", f"{m.group(1)}-{m.group(2)}.json")
    json.dump(clean(doc), open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit", os.path.relpath(dest, ROOT))
    build()

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build()
    elif len(sys.argv) == 3 and sys.argv[1] == "add":
        add(sys.argv[2])
    else:
        sys.exit(__doc__)
