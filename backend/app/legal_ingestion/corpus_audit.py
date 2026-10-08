"""Requalify the fixed original-source inventory without providers or database access."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import socket

from .extractors import is_html_document
from .service import stage_file


ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "docs/LEGAL_KNOWLEDGE_V2_CORPUS_QUALIFICATION.json"
REVIEWS = ROOT / "docs/LEGAL_KNOWLEDGE_V2_CORPUS_RECOVERY_REVIEW.json"
OUTPUT = ROOT / "docs/LEGAL_KNOWLEDGE_V2_CORPUS_RECOVERY.json"


def _offline(*args, **kwargs):
    raise RuntimeError("Corpus audit forbids network access")


def audit(root: Path, baseline: dict, reviews: dict) -> dict:
    """The baseline supplies only source paths/hashes, never legal text or units."""
    root = root.resolve()
    rows = baseline["records"]
    if len(rows) != baseline["physical_originals"]:
        raise ValueError("Baseline original count disagrees with its inventory")
    approved = {entry["source_file_hash"]: entry for entry in reviews.get("approved", [])}
    published_sources = {row["source_file_hash"] for row in rows if row["already_published"]}
    exact_groups = defaultdict(list)
    for row in rows:
        exact_groups[row["source_file_hash"]].append(row["source_path"])
    canonical = {digest: sorted(paths)[0] for digest, paths in exact_groups.items()}
    shared_cases = {path for group in baseline["duplicates"]["same_identity_different_source"]
                    for path in group["source_paths"]}
    output = []
    for index, prior in enumerate(rows):
        relative = Path(prior["source_path"])
        source = (root / relative).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError(f"Missing or out-of-scope source at record {index}")
        data = source.read_bytes()
        source_hash = hashlib.sha256(data).hexdigest()
        if source_hash != prior["source_file_hash"]:
            raise ValueError(f"Original source changed at record {index}")
        row = {"source_path": prior["source_path"], "filename": prior["filename"],
               "format": prior["format"], "size_bytes": len(data),
               "source_file_hash": source_hash, "probable_type": prior["probable_type"],
               "before_category": prior["category"], "before_gate_status": prior.get("gate_status")}
        if source_hash in published_sources:
            row.update(category="ALREADY_PUBLISHED", reason="PILOT_SOURCE_ALREADY_PUBLISHED",
                       manual_review_status="EXCLUDED", eligible_for_10_6B=False)
        elif relative.suffix.lower() == ".pdf" and is_html_document(data):
            row.update(category="INVALID_SOURCE", reason="HTML_EDITORIAL_PAGE_WITH_PDF_EXTENSION",
                       source_format="html", manual_review_status="SOURCE_REVIEW_REQUIRED",
                       eligible_for_10_6B=False)
        else:
            document = stage_file(source)
            counts = dict(sorted(Counter(unit.unit_type for unit in document.units).items()))
            row.update(document_hash=document.document_hash, parser_version=document.parser_version,
                       document_type=document.document_type, source_format=document.source_format,
                       source_quality=document.extraction_quality, gate_status=document.ingestion_status,
                       ocr_required=document.ocr_required,
                       metadata={key: value for key, value in document.metadata.items() if key in
                                 {"court", "chamber", "expediente", "resolution_type",
                                  "resolution_date", "number", "precedent_binding", "ponente",
                                  "materia", "instancia"} and value is not None},
                       total_units=len(document.units), unit_types=counts,
                       warnings=document.warnings,
                       duplicate_unit_hashes=document.metadata.get("duplicate_unit_hashes", 0),
                       oversized_parts=sum(bool(unit.part_number) for unit in document.units),
                       page_issue_count=sum(unit.page_start is None or unit.page_end is None
                                            for unit in document.units if document.source_format == "pdf"),
                       pages=[min((unit.page_start for unit in document.units if unit.page_start is not None), default=None),
                              max((unit.page_end for unit in document.units if unit.page_end is not None), default=None)],
                       search_text_chars=sum(len(unit.search_text) for unit in document.units),
                       token_count=sum(unit.token_count or 0 for unit in document.units))
            if document.ocr_required:
                row.update(category="OCR_REQUIRED", reason="PDF_TEXT_NOT_EXTRACTABLE",
                           manual_review_status="OCR_PENDING", eligible_for_10_6B=False)
            elif canonical[source_hash] != prior["source_path"]:
                row.update(category="REVIEW_REQUIRED", reason="EXACT_SOURCE_DUPLICATE",
                           canonical_source=canonical[source_hash],
                           manual_review_status="EXCLUDED_DUPLICATE", eligible_for_10_6B=False)
            elif prior["source_path"] in shared_cases:
                row.update(category="REVIEW_REQUIRED", reason="SAME_CASE_DIFFERENT_SOURCE_NOT_RECONCILED",
                           manual_review_status="SOURCE_COMPARISON_PENDING", eligible_for_10_6B=False)
            elif document.ingestion_status != "staged":
                row.update(category="REVIEW_REQUIRED", reason="QUALITY_GATE_BLOCKERS",
                           manual_review_status="AUTOMATED_GATE_BLOCKED", eligible_for_10_6B=False)
            else:
                review = approved.get(source_hash)
                if (review and review["source_path"] == prior["source_path"]
                        and review["document_hash"] == document.document_hash
                        and review["parser_version"] == document.parser_version
                        and review["expected_unit_count"] == len(document.units)):
                    row.update(category="PUBLISHABLE", reason="GATE_AND_MANUAL_REVIEW_PASS",
                               manual_review_status="PASS", eligible_for_10_6B=True)
                else:
                    row.update(category="REVIEW_REQUIRED", reason="MANUAL_REVIEW_PENDING",
                               manual_review_status="PENDING", eligible_for_10_6B=False)
        output.append(row)
    classifications = Counter(row["category"] for row in output)
    gross_units = Counter(key for row in output for key, value in row.get("unit_types", {}).items()
                          for _ in range(value))
    publishable = [row for row in output if row["category"] == "PUBLISHABLE"]
    return {"scope": "10.6A.1 offline corpus recovery", "physical_originals": len(output),
            "parser_version": publishable[0]["parser_version"] if publishable else None,
            "records": output,
            "summary": {"classification": dict(sorted(classifications.items())),
                        "gross_units": sum(gross_units.values()),
                        "unit_types": dict(sorted(gross_units.items())),
                        "publishable_by_type": dict(sorted(Counter(row["document_type"] for row in publishable).items())),
                        "publishable_units": sum(row["total_units"] for row in publishable),
                        "new_embeddings_required": sum(row["total_units"] for row in publishable),
                        "new_embedding_text_chars": sum(row["search_text_chars"] for row in publishable),
                        "exact_source_groups": sum(len(paths) > 1 for paths in exact_groups.values()),
                        "exact_source_extra_files": sum(len(paths) - 1 for paths in exact_groups.values()),
                        "same_case_different_source_groups": len(baseline["duplicates"]["same_identity_different_source"])}}


def main() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    reviews = json.loads(REVIEWS.read_text(encoding="utf-8"))
    with patch.object(socket.socket, "connect", _offline), patch.object(socket, "create_connection", _offline):
        report = audit(ROOT, baseline, reviews)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
