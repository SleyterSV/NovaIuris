"""Normalization and deterministic document/unit identity."""
import hashlib
import json
import re
import unicodedata
from uuid import uuid5, NAMESPACE_URL


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", str(text or "")).replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")).strip()


def search_normalize(text: str) -> str:
    return re.sub(r"\s+", " ", normalize_text(text)).strip()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def document_hash(blocks) -> str:
    return sha256("\n".join(search_normalize(block.text) for block in blocks if search_normalize(block.text)))


def content_hash(unit_type: str, number: str | None, heading: str | None, text: str,
                 part_number: int | None = None, hierarchy: dict | None = None) -> str:
    identity = [unit_type, search_normalize(number or "").casefold(),
                search_normalize(heading or "").casefold(), search_normalize(text), part_number,
                {key: search_normalize(value or "").casefold() for key, value in sorted((hierarchy or {}).items())}]
    return sha256(json.dumps(identity, ensure_ascii=False, separators=(",", ":")))


def stable_document_id(hash_value: str, parser_version: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"legal-document:{hash_value}:{parser_version}"))


def stable_unit_id(document_id: str, unit_hash: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"legal-unit:{document_id}:{unit_hash}"))
