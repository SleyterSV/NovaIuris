"""Deterministic offline staging; publishing requires a separate future adapter."""
from collections import Counter
from pathlib import Path
from . import PARSER_VERSION
from .cleaners import remove_repeated_page_furniture
from .extractors import extract
from .identity import document_hash, stable_document_id
from .models import StagedDocument
from .parsers import JurisprudenceParser, NormativeParser, case_law_metadata
from .quality import extraction_quality, validate_staged
from .units import OversizedUnitError, contextual_search_text, split_oversized_unit


def _family(filename, blocks, requested):
    if requested != "auto":
        if requested not in {"normative", "jurisprudence"}:
            raise ValueError("Unsupported legal document family")
        return requested
    title = Path(filename).stem.casefold()
    if any(word in title for word in ("sentencia", "casación", "casacion", "precedente", "auto", "tc_")):
        return "jurisprudence"
    if any(word in title for word in ("constituci", "código", "codigo", "ley", "tributario")):
        return "normative"
    first = " ".join(block.text for block in blocks[:12]).casefold()
    return "jurisprudence" if any(word in first for word in ("tribunal constitucional", "corte suprema", "casación n")) else "normative"


def _document_type(filename, family):
    name = Path(filename).stem.casefold()
    if family == "jurisprudence":
        return "cassation" if "casaci" in name else "order" if "auto" in name else "judgment"
    if "constituci" in name:
        return "constitution"
    if "código" in name or "codigo" in name:
        return "code"
    if "ley" in name:
        return "law"
    return "regulation"


def stage_file(path, *, family="auto", max_unit_tokens=800) -> StagedDocument:
    extracted = extract(path)
    blocks, removed = remove_repeated_page_furniture(extracted.blocks)
    chosen = _family(extracted.filename, blocks, family)
    parser = JurisprudenceParser() if chosen == "jurisprudence" else NormativeParser()
    parsed = parser.parse(blocks)
    quality = extraction_quality(blocks, extracted.ocr_required)
    warnings = list(extracted.warnings)
    if removed:
        warnings.append(f"page_furniture_removed:{removed}")
    # Repeated PDF headers may carry the only case number; read identity before removing them.
    metadata = case_law_metadata(extracted.blocks, extracted.filename) if chosen == "jurisprudence" else {}
    if chosen == "jurisprudence" and not any(unit.unit_type == "decision" for unit in parsed):
        warnings.append("decision_not_detected")
    units = []
    for unit in parsed:
        try:
            units.extend(split_oversized_unit(unit, max_unit_tokens))
        except OversizedUnitError:
            warnings.append(f"oversized_unit_review:{unit.sequence}")
            # Keep the complete source unit for manual review; publication stays gated.
            units.append(unit)
    seen_hashes = set()
    duplicates_detected = 0
    for unit in units:
        if unit.content_hash in seen_hashes:
            duplicates_detected += 1
        seen_hashes.add(unit.content_hash)
    if duplicates_detected:
        warnings.append(f"duplicate_unit_hashes:{duplicates_detected}")
    for index, unit in enumerate(units, 1):
        unit.sequence = index
    title = Path(extracted.filename).stem.replace("_", " ").strip()
    staged = StagedDocument(title=title, document_type=_document_type(extracted.filename, chosen),
        document_hash=document_hash(blocks), source_file_name=extracted.filename,
        source_format=extracted.source_format, parser_version=PARSER_VERSION,
        extraction_quality=quality, ingestion_status="staged", ocr_required=extracted.ocr_required,
        metadata={**metadata, "family": chosen, "parser_name": parser.name,
                  "source_file_hash": extracted.source_file_hash, "removed_page_furniture": removed,
                  "duplicate_unit_hashes": duplicates_detected},
        units=units, warnings=warnings)
    staged.document_id = stable_document_id(staged.document_hash, PARSER_VERSION)
    for unit in units:
        unit.search_text = contextual_search_text(staged, unit)
    problems = validate_staged(staged)
    staged.warnings.extend(problems)
    if chosen == "jurisprudence" and "decision_not_detected" in warnings:
        problems.append("decision_not_detected")
    if any(warning.startswith("oversized_unit_review:") for warning in warnings):
        problems.append("oversized_unit_review")
    staged.ingestion_status = "review_required" if problems else "staged"
    return staged


def dry_run(paths, *, family="auto", max_unit_tokens=800):
    seen = set()
    summaries = []
    for path in paths:
        document = stage_file(path, family=family, max_unit_tokens=max_unit_tokens)
        identity = (document.document_hash, document.parser_version)
        duplicate = identity in seen
        seen.add(identity)
        counts = dict(sorted(Counter(unit.unit_type for unit in document.units).items()))
        summaries.append({"document": document.title, "detected": document.metadata["family"],
                          "document_hash": document.document_hash,
                          "metadata": {key: document.metadata.get(key) for key in
                                       ("court", "expediente", "resolution_type", "precedent_binding", "sumilla")
                                       if document.metadata.get(key) is not None},
                          "units": counts, "status": document.ingestion_status,
                          "extraction_quality": document.extraction_quality,
                          "duplicate_skipped": duplicate, "warnings": document.warnings})
    return summaries
