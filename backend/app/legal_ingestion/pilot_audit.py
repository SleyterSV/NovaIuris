"""Repeat the documented V2 pilot offline from its existing source manifest."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import socket
from unittest.mock import patch

from .service import stage_file


def audit(existing_result: Path) -> dict:
    root = Path(__file__).resolve().parents[3]
    manifest = json.loads(existing_result.read_text(encoding="utf-8"))
    records = []
    with patch.object(socket.socket, "connect", side_effect=RuntimeError("pilot network disabled")), \
         patch.object(socket, "create_connection", side_effect=RuntimeError("pilot network disabled")):
        for prior in manifest["documents"]:
            source = (root / prior["path"]).resolve()
            if not source.is_relative_to(root) or not source.is_file():
                raise ValueError("Pilot source is outside the repository or missing")
            doc = stage_file(source)
            types = Counter(unit.unit_type for unit in doc.units)
            split = sum(unit.part_number is not None for unit in doc.units)
            records.append({"path": prior["path"], "document_hash": doc.document_hash,
                "status": doc.ingestion_status, "publishable": doc.ingestion_status == "staged",
                "ocr_required": doc.ocr_required, "extraction_quality": doc.extraction_quality,
                "metadata": {key: doc.metadata[key] for key in
                    ("number", "court", "chamber", "expediente", "resolution_type",
                     "resolution_date", "resolution_date_text", "ponente", "precedent_binding",
                     "excluded_postamble") if doc.metadata.get(key) is not None},
                "total_units": len(doc.units),
                "unit_types": dict(sorted(types.items())), "split_parts": split,
                "duplicate_extra": doc.metadata["duplicate_unit_hashes"],
                "editorial_concordances_collapsed": doc.metadata["editorial_concordances_collapsed"],
                "page_issues": [w for w in doc.warnings if "page_provenance" in w],
                "metadata_issues": [w for w in doc.warnings if "identity_missing" in w or "date_or_type_missing" in w],
                "warnings": doc.warnings})
    return {"scope": "10.4B-1.5 offline repeat of the same ten sources", "documents": records,
            "totals": {"documents": len(records), "publishable": sum(r["publishable"] for r in records),
                "review_required": sum(not r["publishable"] for r in records),
                "units": sum(r["total_units"] for r in records),
                "articles": sum(r["unit_types"].get("article", 0) for r in records),
                "fundaments": sum(r["unit_types"].get("foundation", 0) for r in records),
                "decisions": sum(r["unit_types"].get("decision", 0) for r in records),
                "duplicates": sum(r["duplicate_extra"] for r in records),
                "oversized_parts": sum(r["split_parts"] for r in records),
                "page_issues": sum(len(r["page_issues"]) for r in records),
                "metadata_issues": sum(len(r["metadata_issues"]) for r in records),
                "ocr_required": sum(r["ocr_required"] for r in records)}}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    result = audit(root / "docs" / "LEGAL_KNOWLEDGE_V2_PILOT_RESULT.json")
    output = root / "docs" / "LEGAL_KNOWLEDGE_V2_HARDENING_RESULT.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["totals"], ensure_ascii=False))
