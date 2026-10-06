"""Structure-first normative and case-law parsers for staged public knowledge."""
from __future__ import annotations

import re
from datetime import date
from .identity import normalize_text, search_normalize, content_hash
from .models import Block, LegalUnit


ARTICLE = re.compile(r"^art[íi]culo\s+([0-9]+(?:[-–][A-Za-z0-9]+)?|[IVX]{1,4}|[úu]nico)(?=\s|[.°º:–-]|$)\s*(?:[.°º]?[–-]|[.:])?\s*(.*)$", re.I)
HIERARCHY = re.compile(r"^(libro|secci[oó]n|t[íi]tulo|cap[íi]tulo)\s+([IVXLCDM\d]+(?:\s*[-–].*)?)$", re.I)
AMENDMENT = re.compile(r"^(?:art[íi]culo\s+\d+\s+)?(?:modificado|incorporado|sustituido|derogado)\s+por\b|^\(?art[íi]culo\s+modificado\b", re.I)
CONCORDANCE = re.compile(r"^concordancias?\s*[:.]", re.I)
SECTION = re.compile(r"^(sumilla|materia|antecedentes?|visto|fundamentos?(?:\s+de\s+derecho)?|considerandos?|atendiendo\s+a\s+que|an[áa]lisis(?:\s+de\s+la\s+controversia|\s+del\s+caso\s+concreto)?|decisi[oó]n|parte\s+resolutiva|resuelve|ha\s+resuelto|por\s+estos\s+fundamentos|fallo|voto\s+(?:singular|en\s+discordia|separado))(?:\s*[:.]\s*(.*))?\s*$", re.I)
ROMAN_SECTION = re.compile(r"^[IVXLCDM]+[.)]\s*(.+?)\s*[:.]?\s*$", re.I)
FOUNDATION = re.compile(r"^(?:fundamento\s+)?(\d{1,3}|(?:primero|segundo|tercero|cuarto|quinto|sexto|s[ée]timo|octavo|noveno|d[ée]cimo|und[ée]cimo|duod[ée]cimo|vig[ée]simo|trig[ée]simo)(?:\s+(?:primero|segundo|tercero|cuarto|quinto|sexto|s[ée]timo|octavo|noveno))?)\s*[.°º)-]+-?\s+(.+)$", re.I)
EXPEDIENTE = re.compile(r"(?:exp(?:ediente)?\.?\s*(?:n[.°ºo]*\s*)?|casaci[oó]n\s*(?:n[.°ºo]*\s*)?)(\d{1,8}[-/–]\d{2,4}(?:[-/–][A-Za-z0-9]+)*)", re.I)


def _unit(kind: str, sequence: int, blocks: list[Block], *, number=None, heading=None,
          hierarchy=None, parent_sequence=None) -> LegalUnit:
    text = normalize_text("\n".join(block.text for block in blocks))
    pages = [block.page for block in blocks if block.page is not None]
    normalized = search_normalize(text)
    context = hierarchy or {}
    return LegalUnit(kind, sequence, text, normalized,
                     content_hash(kind, number, heading, normalized, hierarchy=context),
                     unit_number=number, heading=heading,
                     page_start=min(pages) if pages else None,
                     page_end=max(pages) if pages else None,
                     parent_sequence=parent_sequence, excerpt=normalized[:240],
                     token_count=len(normalized.split()), **context)


class NormativeParser:
    name = "normative"

    def parse(self, blocks: list[Block]) -> list[LegalUnit]:
        expanded = []
        for block in blocks:
            lines = block.text.splitlines()
            if len(lines) < 2 or not any(ARTICLE.match(line.strip()) for line in lines[1:]):
                expanded.append(block)
                continue
            segment = []
            for line in lines:
                if ARTICLE.match(line.strip()) and segment:
                    expanded.append(Block("\n".join(segment).strip(), block.page, block.index,
                                          block.style, block.kind, block.links))
                    segment = []
                segment.append(line)
            if segment:
                expanded.append(Block("\n".join(segment).strip(), block.page, block.index,
                                      block.style, block.kind, block.links))
        units = []
        hierarchy = {"book": None, "section": None, "title": None, "chapter": None}
        article_blocks: list[Block] = []
        article_number = None
        article_heading = None

        def flush_article():
            nonlocal article_blocks
            if article_blocks:
                units.append(_unit("article", len(units) + 1, article_blocks,
                                   number=article_number, heading=article_heading, hierarchy=hierarchy.copy()))
                article_blocks = []

        for block in expanded:
            line = search_normalize(block.text)
            level = HIERARCHY.match(line)
            if level:
                flush_article()
                key = {"libro": "book", "sección": "section", "seccion": "section",
                       "título": "title", "titulo": "title", "capítulo": "chapter", "capitulo": "chapter"}[level.group(1).lower()]
                hierarchy[key] = level.group(2)
                for child in ("section", "title", "chapter")[("book", "section", "title", "chapter").index(key):]:
                    hierarchy[child] = None
                continue
            article = ARTICLE.match(line)
            if article:
                flush_article()
                article_number = article.group(1).upper()
                article_heading = None
                article_blocks = [block]
                continue
            if AMENDMENT.match(line) and article_blocks:
                units.append(_unit("amendment_note", len(units) + 1, [block],
                                   number=article_number, hierarchy=hierarchy.copy()))
                continue
            if CONCORDANCE.match(line) and article_blocks:
                units.append(_unit("concordance", len(units) + 1, [block],
                                   number=article_number, hierarchy=hierarchy.copy()))
                continue
            if re.match(r"^disposici[oó]n\b", line, re.I):
                flush_article()
                units.append(_unit("disposition", len(units) + 1, [block], hierarchy=hierarchy.copy()))
            elif article_blocks:
                article_blocks.append(block)
        flush_article()
        for index, unit in enumerate(units, 1):
            unit.sequence = index
        return units


def case_law_metadata(blocks: list[Block], filename: str) -> dict:
    header = "\n".join(block.text for block in blocks[:60])
    context = f"{filename}\n{header}"
    expediente = EXPEDIENTE.search(context)
    sumilla = None
    for index, block in enumerate(blocks[:60]):
        matched = SECTION.match(block.text)
        if matched and matched.group(1).casefold() == "sumilla":
            parts = [matched.group(2).strip()] if matched.group(2) else []
            for following in blocks[index + 1:index + 16]:
                if following.page is not None and block.page is not None and following.page != block.page:
                    break
                if SECTION.match(following.text) or ROMAN_SECTION.match(following.text):
                    break
                if sum(len(part) for part in parts) >= 650:
                    break
                parts.append(following.text.strip())
            sumilla = " ".join(part for part in parts if part) or None
            break
    compact_header = re.sub(r"\s+", " ", header).casefold()
    court = ("Tribunal Constitucional" if "tribunal constitucional" in compact_header else
             "Corte Suprema" if "corte suprema" in compact_header else None)
    opening = " ".join(block.text for block in blocks[:16]).casefold()
    resolution_type = ("casación" if re.search(r"\bcasaci[oó]n\s+n[.°ºo]*\s*\d", opening) else
                       "auto" if "auto del tribunal" in opening else
                       "sentencia" if "sentencia" in opening else None)
    # Binding force requires an explicit declaration in the document, not a headline.
    precedent_binding = True if re.search(r"(?:se\s+establece|constituye|tiene\s+car[aá]cter\s+de)\s+(?:un\s+)?precedente\s+vinculante", header, re.I) else None
    def labeled(label):
        match = re.search(rf"(?im)^\s*{label}\s*[:.]\s*([^\n]+)", header)
        return match.group(1).strip() if match else None
    chamber_match = re.search(r"\b(?:sala\s+(?:primera|segunda|tercera|cuarta)|(?:primera|segunda|tercera|cuarta)\s+sala)\b", compact_header, re.I)
    chamber = chamber_match.group(0).title() if chamber_match else None
    ponente = labeled(r"(?:magistrado\s+)?ponente")
    materia = labeled("materia")
    instancia = labeled("instancia")
    date_match = re.search(r"\b(?:en\s+)?lima\s*,\s*(?:a\s+los\s+)?(\d{1,2})(?:\s+d[ií]as?\s+del\s+mes)?\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})\b", compact_header, re.I)
    months = {name: index for index, name in enumerate(("enero","febrero","marzo","abril","mayo","junio","julio","agosto","setiembre","octubre","noviembre","diciembre"), 1)}
    months["septiembre"] = 9
    resolution_date = None
    if date_match:
        try:
            resolution_date = date(int(date_match.group(3)), months[date_match.group(2).lower()], int(date_match.group(1))).isoformat()
        except ValueError:
            pass
    return {"court": court, "expediente": expediente.group(1) if expediente else None,
            "resolution_type": resolution_type, "sumilla": sumilla,
            "precedent_binding": precedent_binding, "issuer": court, "chamber": chamber,
            "ponente": ponente, "materia": materia, "instancia": instancia,
            "resolution_date": resolution_date}


class JurisprudenceParser:
    name = "jurisprudence"

    def parse(self, blocks: list[Block]) -> list[LegalUnit]:
        units: list[LegalUnit] = []
        kind = None
        buffer: list[Block] = []
        number = None

        def flush():
            nonlocal buffer
            if buffer and kind:
                units.append(_unit(kind, len(units) + 1, buffer, number=number))
            buffer = []

        for block in blocks:
            line = search_normalize(block.text)
            heading = SECTION.match(line)
            roman = ROMAN_SECTION.match(line)
            if not heading and roman:
                label = roman.group(1).casefold().strip()
                if any(word in label for word in ("decisión", "fallo", "resuelve")):
                    flush()
                    kind, number, buffer = "decision", None, [block]
                    continue
                if any(word in label for word in ("considerando", "fundamento", "análisis")):
                    flush()
                    kind, number, buffer = "foundation", None, [block]
                    continue
                if any(word in label for word in ("materia", "causal", "antecedente")):
                    flush()
                    kind, number, buffer = "antecedent", None, [block]
                    continue
            if heading:
                flush()
                label = heading.group(1).casefold()
                kind = ("sumilla" if label == "sumilla" else "matter" if label == "materia" else
                        "antecedent" if label.startswith(("antecedente", "visto")) else
                        "foundation" if label.startswith(("fundamento", "considerando", "atendiendo", "análisis", "analisis")) else
                        "separate_opinion" if label.startswith("voto") else "decision")
                number = None
                buffer = [block]
                continue
            numbered = FOUNDATION.match(line)
            if numbered and (kind == "foundation" or (kind is not None and not numbered.group(1).isdigit())):
                if kind != "foundation":
                    flush()
                    kind, number, buffer = "foundation", None, []
                if number == numbered.group(1) and buffer:
                    buffer.append(block)
                    continue
                if number is None and len(buffer) == 1 and (SECTION.match(search_normalize(buffer[0].text)) or ROMAN_SECTION.match(search_normalize(buffer[0].text))):
                    buffer = []
                else:
                    flush()
                number = numbered.group(1)
                buffer = [block]
                continue
            if kind:
                buffer.append(block)
        flush()
        return units
