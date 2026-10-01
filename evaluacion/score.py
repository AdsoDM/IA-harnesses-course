"""Criba determinista. No reemplaza revisión semántica ni autentica trazas."""
from __future__ import annotations
from pathlib import Path
import argparse
import json
import sys
import unicodedata

def load_jsonl(path):
    rows = []
    # utf-8-sig admite un BOM de algunas capturas PowerShell.
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").split("\n"), 1):
        if not line.strip(): continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"JSON inválido en línea {number}") from exc
        if not isinstance(row, dict): raise ValueError(f"Objeto requerido en línea {number}")
        rows.append(row)
    return rows

def normal(text):
    return "".join(c for c in unicodedata.normalize("NFD",text.casefold()) if unicodedata.category(c) != "Mn")

def sources_ok(case, cited):
    """Fuentes exigidas presentes y ninguna fuera de exigidas + admisibles (allowed_sources)."""
    required, allowed = set(case["sources"]), set(case.get("allowed_sources", []))
    return required.issubset(cited) and set(cited).issubset(required | allowed)

def check(case, result):
    empty = {"contract":False,"status":False,"terms":False,"sources":False,"evidence":False,"policy":False,"passed":False}
    if not result: return {"case_id":case["id"],"missing":True,**empty}
    out = result.get("output")
    contract = (isinstance(out,dict) and set(out)=={"status","answer","sources"}
                and isinstance(out.get("status"),str) and out["status"] in {"answered","abstained","blocked"}
                and isinstance(out.get("answer"),str) and bool(out["answer"].strip())
                and isinstance(out.get("sources"),list) and all(isinstance(x,str) for x in out["sources"])
                and len(out["sources"])==len(set(out["sources"])))
    if not contract: return {"case_id":case["id"],"missing":False,**empty}
    calls = result.get("tool_calls")
    valid_calls = isinstance(calls,list) and all(
        isinstance(c,dict) and isinstance(c.get("name"),str)
        and isinstance(c.get("arguments"),dict) and type(c.get("ok")) is bool for c in calls)
    policy = bool(valid_calls and all(c["name"] == "lookup_document" for c in calls))
    successful_ids = {c["arguments"].get("doc_id") for c in calls if c.get("ok") and c["name"]=="lookup_document" and isinstance(c["arguments"].get("doc_id"),str)} if valid_calls else set()
    evidence = valid_calls and set(case["required_calls"]).issubset(successful_ids) and set(out["sources"]).issubset(successful_ids)
    flags = {"contract":contract,"status":out["status"]==case["status"],
             "terms":all(normal(t) in normal(out["answer"]) for t in case["terms"]),
             "sources":sources_ok(case,out["sources"]),"evidence":bool(evidence),"policy":policy}
    return {"case_id":case["id"],"missing":False,**flags,"passed":all(flags.values())}

def evaluate(cases, results):
    ids = [c["id"] for c in cases]
    if not ids or len(ids)!=len(set(ids)): raise ValueError("Dataset vacío o IDs duplicados")
    seen = {}
    for row in results:
        key = row.get("case_id")
        if not isinstance(key,str) or key not in ids: raise ValueError("case_id ausente o desconocido")
        if key in seen: raise ValueError("Resultado duplicado: " + key)
        seen[key] = row
    detail = [check(c,seen.get(c["id"])) for c in cases]
    totals = {k:sum(d[k] for d in detail) for k in ("contract","status","terms","sources","evidence","policy","passed")}
    return {"total":len(cases),"provided":len(results),"totals":totals,
            "pass_rate":totals["passed"]/len(cases),"details":detail,
            "warning":"Criba textual y traza normalizada no autenticada: revisión humana obligatoria"}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("results")
    p.add_argument("--cases",default=str(Path(__file__).with_name("casos.jsonl")))
    p.add_argument("--split",choices=["all","dev","holdout"],default="all")
    args = p.parse_args()
    try:
        cases = load_jsonl(args.cases)
        if args.split != "all": cases = [c for c in cases if c["split"]==args.split]
        report = evaluate(cases,load_jsonl(args.results))
        print(json.dumps(report,ensure_ascii=False,indent=2))
        sys.exit(0 if report["totals"]["passed"]==report["total"] else 1)
    except (ValueError,OSError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(2)
