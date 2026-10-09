"""Structure-first normative and case-law parsers for staged public knowledge."""
from __future__ import annotations

import re
from datetime import date
from .identity import normalize_text, search_normalize, content_hash
from .models import Block, LegalUnit


ARTICLE = re.compile(r"^art[íi]culo\s+([0-9]+(?:[-–][A-Za-z0-9]+)?|[IVX]{1,4}|[úu]nico)(?=\s|[.°º:–-]|$)\s*(?:[.°º]?[–-]|[.:])?\s*(.*)$", re.I)
HIERARCHY = re.compile(r"^(libro|secci[oó]n|t[íi]tulo|cap[íi]tulo)\s+([IVXLCDM\d]+(?:\s*[-–].*)?)$", re.I)
PRELIMINARY_TITLE = re.compile(r"^t[íi]tulo\s+preliminar$", re.I)
AMENDMENT = re.compile(r"^(?:art[íi]culo\s+\d+\s+)?(?:modificado|incorporado|sustituido|derogado)\s+por\b|^\(?art[íi]culo\s+modificado\b", re.I)
CONCORDANCE = re.compile(r"^concordancias?\s*[:.]", re.I)
PROVISIONS = re.compile(r"^disposici[oó]n(?:es)?\s+(?:(?:complementarias?|finales?|transitorias?|modificatorias?|derogatorias?)\s*(?:y\s+)?){1,4}$", re.I)
ORDINAL_PROVISION = re.compile(r"^([úu]nica|primera|segunda|tercera|cuarta|quinta|sexta|s[eé]tima|octava|novena|d[eé]cima(?:\s+primera)?|[a-z]+[ée]sima)\s*[.\-–]", re.I)
SECTION = re.compile(r"^(sumilla|materia|antecedentes?|autos\s+y\s+vistos?|vistos?|fundamentos?(?:\s+de\s+derecho)?|considerandos?|atendiendo\s+a\s+que|an[áa]lisis(?:\s+de\s+la\s+controversia|\s+del\s+caso\s+concreto)?|decisi[oó]n|parte\s+resolutiva|resuelve|ha\s+resuelto|por\s+estos\s+fundamentos|fallo|(?:fundamento\s+de\s+)?voto\s+(?:singular|en\s+discordia|separado|concurrente)(?:\s+del?\s+magistrad[oa])?|fundamento\s+de\s+voto\s+del?\s+magistrad[oa])(?:\s*[:.]\s*(.*))?\s*$", re.I)
VOTE_HEADING = re.compile(r"^(?:fundamento\s+de\s+voto|voto(?:\s+(?:singular|en\s+discordia|separado|concurrente))?)(?:\s+(?:del?|de\s+la)\s+(?:magistrad[oa]|juez)(?:\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s.]{2,80})?)?$", re.I)
ROMAN_SECTION = re.compile(r"^[IVXLCDM]+[.)]\s*(.+?)\s*[:.]?\s*$", re.I)
FOUNDATION_V2_1_0 = re.compile(r"^(?:fundamento\s+)?(\d{1,3}|(?:primero|segundo|tercero|cuarto|quinto|sexto|s[ée]timo|octavo|noveno|d[ée]cimo(?:primero|segundo|tercero|cuarto|quinto|sexto|s[ée]timo|octavo|noveno)?|und[ée]cimo|duod[ée]cimo|vig[ée]simo|trig[ée]simo)(?:\s+(?:primero|segundo|tercero|cuarto|quinto|sexto|s[ée]timo|octavo|noveno))?)\s*[.°º)-]+-?\s+(.+)$", re.I)
FOUNDATION = re.compile(FOUNDATION_V2_1_0.pattern.replace("s[ée]timo", "s[ée]ptimo"), re.I)
EXPEDIENTE = re.compile(r"(?:exp(?:ediente)?\.?\s*(?:n[.°ºo]*\s*)?|casaci[oó]n\s*(?:n[.°ºo]*\s*)?)(\d{1,8}[-/–]\d{2,4}(?:[-/–][A-Za-z0-9]+)*)", re.I)
DAY_WORDS = {"uno": 1, "primero": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
             "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
             "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
             "dieciséis": 16, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18,
             "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidós": 22,
             "veintidos": 22, "veintitrés": 23, "veintitres": 23,
             "veinticuatro": 24, "veinticinco": 25, "veintiséis": 26,
             "veintiseis": 26, "veintisiete": 27, "veintiocho": 28,
             "veintinueve": 29, "treinta": 30, "treinta y uno": 31}
WORD_DATE = re.compile(r"\b(?:en\s+)?lima\s*,\s*(?P<day>treinta y uno|[a-záéíóú]+)\s+de\s+"
                       r"(?P<month>enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|octubre|noviembre|diciembre)\s+de\s+"
                       r"(?P<year>dos mil(?:\s+[a-záéíóú]+)?)\b", re.I)


def _unit(kind: str, sequence: int, blocks: list[Block], *, number=None, heading=None,
          hierarchy=None, parent_sequence=None) -> LegalUnit:
    text = normalize_text("\n".join(block.text for block in blocks))
    pages = [block.page for block in blocks if block.page is not None]
    normalized = search_normalize(text)
    context = hierarchy or {}
    unit = LegalUnit(kind, sequence, text, normalized,
                     content_hash(kind, number, heading, normalized, hierarchy=context),
                     unit_number=number, heading=heading,
                     page_start=min(pages) if pages else None,
                     page_end=max(pages) if pages else None,
                     parent_sequence=parent_sequence, excerpt=normalized[:240],
                     token_count=len(normalized.split()), **context)
    unit.metadata["source_block_indexes"] = [block.index for block in blocks]
    if pages:
        unit.metadata["source_line_pages"] = [block.page for block in blocks for line in normalize_text(block.text).splitlines() if line]
    return unit


class NormativeParser:
    name = "normative"

    def parse(self, blocks: list[Block]) -> list[LegalUnit]:
        self.postamble_start_index = None
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
        provision_blocks: list[Block] = []
        provision_number = None
        provision_heading = None
        in_provisions = False

        def flush_article():
            nonlocal article_blocks
            if article_blocks:
                units.append(_unit("article", len(units) + 1, article_blocks,
                                   number=article_number, heading=article_heading, hierarchy=hierarchy.copy()))
                article_blocks = []

        def flush_provision():
            nonlocal provision_blocks
            if provision_blocks:
                unit = _unit("disposition", len(units) + 1, provision_blocks,
                             number=provision_number, hierarchy=hierarchy.copy())
                unit.metadata["provision_heading"] = provision_heading
                unit.content_hash = content_hash(unit.unit_type, unit.unit_number, unit.heading,
                                                 unit.normalized_text, provision_heading,
                                                 hierarchy=hierarchy.copy())
                units.append(unit)
                provision_blocks = []

        for block in expanded:
            line = search_normalize(block.text)
            if in_provisions and re.match(r"^comun[ií]quese\s+al\s+señor\s+presidente\b", line, re.I):
                flush_article()
                flush_provision()
                self.postamble_start_index = block.index
                break
            if PROVISIONS.match(line):
                flush_article()
                flush_provision()
                provision_heading = line
                in_provisions = True
                continue
            provision = ORDINAL_PROVISION.match(line) if in_provisions else None
            if provision:
                flush_article()
                flush_provision()
                provision_number = provision.group(1).upper()
                provision_blocks = [block]
                continue
            if PRELIMINARY_TITLE.match(line):
                flush_article()
                flush_provision()
                in_provisions = False
                hierarchy = {"book": None, "section": None, "title": "PRELIMINAR", "chapter": None}
                continue
            if in_provisions and provision_blocks:
                if AMENDMENT.match(line):
                    units.append(_unit("amendment_note", len(units) + 1, [block],
                                       number=provision_number, hierarchy=hierarchy.copy()))
                    continue
                if CONCORDANCE.match(line):
                    units.append(_unit("concordance", len(units) + 1, [block],
                                       number=provision_number, hierarchy=hierarchy.copy()))
                    continue
                provision_blocks.append(block)
                continue
            level = HIERARCHY.match(line)
            if level:
                flush_article()
                flush_provision()
                in_provisions = False
                key = {"libro": "book", "sección": "section", "seccion": "section",
                       "título": "title", "titulo": "title", "capítulo": "chapter", "capitulo": "chapter"}[level.group(1).lower()]
                hierarchy[key] = level.group(2)
                for child in ("section", "title", "chapter")[("book", "section", "title", "chapter").index(key):]:
                    hierarchy[child] = None
                continue
            article = ARTICLE.match(line)
            if article:
                flush_article()
                flush_provision()
                in_provisions = False
                article_number = article.group(1).upper()
                candidate_heading = article.group(2).strip()
                article_heading = (candidate_heading if len(block.text.splitlines()) == 1
                                   and 0 < len(candidate_heading.split()) <= 18
                                   and not re.search(r"[.;:!?]$", candidate_heading)
                                   else None)
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
        flush_provision()
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
    compact_original = re.sub(r"\s+", " ", header)
    compact_header = compact_original.casefold()
    primary_header = re.sub(r"\s+", " ", " ".join(block.text for block in blocks[:12])).casefold()
    court_hits = [(match.start(), name) for phrase, name in
                  ((r"tribunal\s+constitucional", "Tribunal Constitucional"),
                   (r"corte\s+suprema", "Corte Suprema"),
                   (r"corte\s+superior", "Corte Superior"))
                  for match in re.finditer(phrase, primary_header)]
    court = min(court_hits)[1] if court_hits else None
    opening = " ".join(block.text for block in blocks[:16]).casefold()
    resolution_type = ("casación" if re.search(r"\bcasaci[oó]n\s+n[.°ºo]*\s*\d", opening) else
                       "auto" if "auto del tribunal" in opening else
                       "sentencia" if "sentencia" in opening else None)
    # Binding force requires an explicit declaration in the document, not a headline.
    precedent_binding = True if re.search(r"(?:se\s+establece|constituye|tiene\s+car[aá]cter\s+de)\s+(?:un\s+)?precedente\s+vinculante", header, re.I) else None
    def labeled(label):
        match = re.search(rf"(?im)^\s*{label}\s*[:.]\s*([^\n]+)", header)
        return match.group(1).strip() if match else None
    chamber_match = re.search(r"\b(?:sala\s+(?:primera|segunda|tercera|cuarta|penal\s+(?:permanente|transitoria))|(?:primera|segunda|tercera|cuarta)\s+sala(?:\s+constitucional)?)\b", primary_header, re.I)
    chamber = chamber_match.group(0).title() if chamber_match else None
    ponente = labeled(r"(?:magistrado\s+)?ponente")
    if ponente is None:
        for block in reversed(blocks[-30:]):
            signature = re.match(r"^\s*(?:MAGISTRADO\s+)?PONENTE\s*[:.]?\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s.]+)\s*$",
                                 block.text, re.I)
            if signature:
                ponente = signature.group(1).strip()
                break
    materia = labeled("materia")
    instancia = labeled("instancia")
    date_match = re.search(r"\b(?:en\s+)?lima\s*,\s*(?:a\s+los\s+|al\s+d[ií]a\s+)?(\d{1,2})(?:\s+d[ií]as?\s+del\s+mes|\s+del\s+mes)?\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})\b", compact_header, re.I)
    months = {name: index for index, name in enumerate(("enero","febrero","marzo","abril","mayo","junio","julio","agosto","setiembre","octubre","noviembre","diciembre"), 1)}
    months["septiembre"] = 9
    resolution_date = None
    if date_match:
        try:
            resolution_date = date(int(date_match.group(3)), months[date_match.group(2).lower()], int(date_match.group(1))).isoformat()
        except ValueError:
            pass
    resolution_date_text = None
    if resolution_date is None:
        written = WORD_DATE.search(compact_original)
        if written:
            day = DAY_WORDS.get(written.group("day").casefold())
            year_words = written.group("year").casefold().split()
            year = 2000 + (DAY_WORDS.get(year_words[2], 0) if len(year_words) == 3 else 0)
            if day and (len(year_words) == 2 or year > 2000):
                try:
                    resolution_date = date(year, months[written.group("month").casefold()], day).isoformat()
                    resolution_date_text = written.group(0)
                except ValueError:
                    pass
    return {"court": court, "expediente": expediente.group(1) if expediente else None,
            "resolution_type": resolution_type, "sumilla": sumilla,
            "precedent_binding": precedent_binding, "issuer": court, "chamber": chamber,
            "ponente": ponente, "materia": materia, "instancia": instancia,
            "resolution_date": resolution_date, "resolution_date_text": resolution_date_text}


class JurisprudenceParser:
    name = "jurisprudence"

    def __init__(self, *, legacy=False):
        self.legacy = legacy

    def parse(self, blocks: list[Block]) -> list[LegalUnit]:
        units: list[LegalUnit] = []
        kind = None
        buffer: list[Block] = []
        number = None
        unit_heading = None

        def flush():
            nonlocal buffer, unit_heading
            if buffer and kind:
                units.append(_unit(kind, len(units) + 1, buffer, number=number,
                                   heading=unit_heading))
            buffer = []
            unit_heading = None

        for block_index, block in enumerate(blocks):
            line = search_normalize(block.text)
            heading = SECTION.match(line)
            roman = ROMAN_SECTION.match(line)
            if VOTE_HEADING.fullmatch(line):
                flush()
                kind, number, buffer = "separate_opinion", None, [block]
                continue
            if kind == "separate_opinion":
                buffer.append(block)
                continue
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
                kind = ("separate_opinion" if VOTE_HEADING.match(label) else
                        "sumilla" if label == "sumilla" else "matter" if label == "materia" else
                        "antecedent" if label.startswith(("antecedente", "visto", "auto")) else
                        "foundation" if label.startswith(("fundamento", "considerando", "atendiendo", "análisis", "analisis")) else
                        "decision")
                number = None
                buffer = [block]
                continue
            numbered = (FOUNDATION_V2_1_0 if self.legacy else FOUNDATION).match(line)
            if numbered and (kind == "foundation" or (kind is not None and not numbered.group(1).isdigit())):
                # A wrapped case reference such as "Auto 5 - 00004-2024-PCC/TC"
                # can begin at the left margin like a numbered foundation.
                if (numbered.group(1).isdigit() and
                        re.match(r"\d{2,}-\d{4}(?:[-/][A-Za-z0-9]+)*", numbered.group(2))):
                    buffer.append(block)
                    continue
                # A remote judgment's numbered paragraph quoted after an
                # explicit citation remains inside the citing foundation.
                cited_intro = " ".join(item.text for item in blocks[max(0, block_index - 12):block_index]).casefold()
                cited_tail = " ".join(item.text for item in blocks[max(0, block_index - 2):block_index]).casefold()
                if (kind == "foundation" and numbered.group(1).isdigit()
                        and number and number.isdigit()
                        and int(numbered.group(1)) != int(number) + 1
                        and re.search(r"(?:sentencia|resoluci[oó]n|parte resolutiva)", cited_intro)
                        and re.search(r"(?:señala|establece|dispone)[^:]{0,100}lo siguiente\s*:\s*$", cited_tail)):
                    buffer.append(block)
                    continue
                if kind != "foundation":
                    flush()
                    kind, number, buffer = "foundation", None, []
                if number == numbered.group(1) and buffer:
                    buffer.append(block)
                    continue
                header_only = (not self.legacy and number is None and 1 <= len(buffer) <= 3
                               and SECTION.match(search_normalize(buffer[0].text))
                               and all(len(item.text.split()) <= 5 and
                                       not re.search(r"[.!?;:]|\d", item.text)
                                       for item in buffer[1:]))
                if header_only:
                    unit_heading = buffer[-1].text.strip() if len(buffer) > 1 else None
                    buffer = []
                elif number is None and len(buffer) == 1 and (SECTION.match(search_normalize(buffer[0].text)) or ROMAN_SECTION.match(search_normalize(buffer[0].text))):
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
