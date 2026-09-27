"""Ejecute con credenciales: python scripts/benchmark_novacourt.py casos.json."""
import json, sys, time
from app.services.court_simulation import LegalDebateSimulator
def main(path):
    cases=json.load(open(path, encoding="utf-8")); rows=[]
    for case in cases:
        started=time.perf_counter(); result=LegalDebateSimulator.simulate_case(case["case"])
        rows.append({"id":case.get("id"),"duration_ms":round((time.perf_counter()-started)*1000),**result.get("performance",{})})
    print(json.dumps(rows, ensure_ascii=False, indent=2))
if __name__=="__main__": main(sys.argv[1])
