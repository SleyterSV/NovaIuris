"""Presentation-only projection of a persisted NovaCase report for file exports."""
from datetime import datetime
import re


TECHNICAL_ID = re.compile(r'\b(?:FACT|ISSUE|SRC)-[0-9a-f-]{8,}\b|\b[0-9a-f]{8}-[0-9a-f-]{27,}\b', re.I)
HEADING = re.compile(r'^#{1,3}\s+(.+?)\s*$')
SOURCE_HEADING = re.compile(r'^fuentes(?: utilizadas)?$', re.I)
NARRATIVE_SECTION = re.compile(
    r'^(?:Objeto y alcance|Marco normativo y jurisprudencial|Análisis jurídico(?: por cuestión)?|'
    r'Argumentos jurídicos centrales|Contraargumentos previsibles y réplicas)$', re.I)


def clean_text(value):
    return TECHNICAL_ID.sub('', str(value or '')).strip()


def report_content(result):
    """Return the same authorized text and citations for PDF and DOCX."""
    if not isinstance(result, dict) or result.get('success') is not True:
        raise ValueError('Completed result required')
    report = result.get('report')
    if not isinstance(report, str) or not report.strip():
        raise ValueError('Report unavailable')
    document = result.get('report_document') or {}
    if not isinstance(document, dict) or (document and document.get('case_id') != result.get('case_id')):
        raise ValueError('Report case mismatch')
    sections = document.get('sections') if isinstance(document.get('sections'), list) else []
    if not sections:
        sections = []
        title = None
        lines = []
        for raw in report.splitlines():
            heading = HEADING.match(raw.strip())
            if heading:
                if title and any(line.strip() for line in lines):
                    sections.append({'title': title, 'content': '\n'.join(lines).strip()})
                title, lines = heading.group(1), []
            else:
                lines.append(raw)
        if title and any(line.strip() for line in lines):
            sections.append({'title': title, 'content': '\n'.join(lines).strip()})
        if not sections:
            sections = [{'title': 'Informe', 'content': report}]
    sections = [{'title': clean_text(item.get('title') or 'Sección'),
                 'content': clean_text(item.get('content'))}
                for item in sections if isinstance(item, dict) and isinstance(item.get('content'), str)
                and item['content'].strip() and not SOURCE_HEADING.fullmatch(str(item.get('title') or '').strip())]
    sources = document.get('sources') if isinstance(document.get('sources'), list) else []
    citations = document.get('citations') if isinstance(document.get('citations'), list) else []
    by_id = {item.get('source_id'): item for item in sources if isinstance(item, dict)}
    references, used = [], set()
    for citation in citations:
        if not isinstance(citation, dict) or not re.fullmatch(r'\[\d+\]', str(citation.get('label') or '')):
            continue
        source_id = citation.get('source_id')
        source = by_id.get(source_id)
        if not source or source_id in used:
            continue
        used.add(source_id)
        metadata = source.get('metadata') if isinstance(source.get('metadata'), dict) else {}
        unit_type = source.get('unit_type') or metadata.get('unit_type')
        unit_number = source.get('unit_number') or metadata.get('unit_number')
        unit_label = {'foundation': 'Fundamento', 'article': 'Artículo',
                      'decision': 'Decisión', 'separate_opinion': 'Voto separado'}.get(unit_type)
        canonical_unit = f'{unit_label} {unit_number}' if unit_label and unit_number else None
        locator = source.get('locator') or canonical_unit or source.get('article') or source.get('legal_basis')
        metadata = [source.get('court') or source.get('issuer') or
                    ('Documento del caso' if source.get('source_scope') in ('case', 'private_case') else None), locator,
                    f"pág. {source['page_start']}" if source.get('page_start') else None]
        references.append({'label': citation['label'],
                           'title': clean_text(source.get('display_title') or source.get('title') or 'Fuente utilizada'),
                           'detail': ' · '.join(clean_text(value) for value in metadata if value)})
    generated = document.get('generated_at')
    date_label = ''
    if isinstance(generated, str):
        try:
            date_label = datetime.fromisoformat(generated.replace('Z', '+00:00')).strftime('%d/%m/%Y')
        except ValueError:
            pass
    return {'title': clean_text(document.get('title') or 'Informe jurídico'),
            'date': date_label, 'sections': sections, 'references': references}


def report_blocks(content, section_title=''):
    """Keep legal wording intact while identifying headings, prose and real lists."""
    blocks = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        heading = HEADING.match(line)
        if heading:
            blocks.append(('heading', clean_text(heading.group(1))))
        elif line.startswith(('- ', '* ')):
            kind = 'paragraph' if NARRATIVE_SECTION.fullmatch(section_title.strip()) else 'list'
            blocks.append((kind, clean_text(line[2:])))
        else:
            blocks.append(('paragraph', clean_text(line)))
    return blocks
