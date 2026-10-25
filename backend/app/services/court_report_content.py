"""Presentation adapter over NovaCourt's persisted, server-owned report."""
from datetime import datetime
import re
import unicodedata

from .case_report_content import clean_text, HEADING


def court_report_content(result):
    if not isinstance(result, dict) or result.get('success') is not True:
        raise ValueError('Completed Court result required')
    document = result.get('court_report_document')
    simulation = result.get('simulation')
    if (not isinstance(document, dict) or document.get('document_type') != 'court_simulation'
            or document.get('case_id') != result.get('case_id')
            or not isinstance(document.get('sections'), list)
            or not isinstance(simulation, dict) or simulation.get('status') != 'ready'):
        raise ValueError('Completed Court report required')

    sections = []
    for item in document['sections']:
        if not isinstance(item, dict):
            continue
        title, text = clean_text(item.get('title')), clean_text(item.get('content'))
        if title and text:
            sections.append({'title': title, 'content': text})
    if not sections:
        raise ValueError('Court report has no content')

    sources = document.get('sources') if isinstance(document.get('sources'), list) else []
    citations = document.get('citations') if isinstance(document.get('citations'), list) else []
    by_id = {source.get('source_id'): source for source in sources
             if isinstance(source, dict) and isinstance(source.get('source_id'), str)}
    references, seen = [], set()
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        label = citation.get('label')
        source_id = citation.get('source_id')
        if not isinstance(label, str) or not re.fullmatch(r'\[\d+\]', label) or source_id in seen:
            continue
        source = by_id.get(source_id)
        if not source:
            continue
        seen.add(source_id)
        metadata = source.get('metadata') if isinstance(source.get('metadata'), dict) else {}
        unit_type = source.get('unit_type') or metadata.get('unit_type')
        unit_number = source.get('unit_number') or metadata.get('unit_number')
        unit_label = {'foundation': 'Fundamento', 'article': 'Artículo', 'decision': 'Decisión',
                      'separate_opinion': 'Voto separado'}.get(unit_type)
        locator = source.get('locator') or (f'{unit_label} {unit_number}' if unit_label and unit_number else '')
        pages = ''
        if source.get('page_start'):
            pages = f"pág. {source['page_start']}"
            if source.get('page_end') and source['page_end'] != source['page_start']:
                pages += f"–{source['page_end']}"
        is_private = source.get('source_scope') in {'case', 'private_case'}
        detail = ' · '.join(clean_text(value) for value in (
            'Documento aportado' if is_private else source.get('court') or source.get('issuer') or 'Fuente jurídica',
            locator, pages) if value)
        references.append({'label': label,
            'title': clean_text(source.get('display_title') or source.get('title') or 'Fuente utilizada'),
            'detail': detail, 'group': 'DOCUMENTOS DEL CASO' if is_private else 'FUENTES JURÍDICAS'})

    meta = result.get('metadata') if isinstance(result.get('metadata'), dict) else {}
    case_title = clean_text(document.get('case_title') or result.get('case_title') or meta.get('case_title'))
    return {'title': 'INFORME DE SIMULACIÓN JURÍDICA', 'case_title': case_title,
            'date': datetime.now().astimezone().strftime('%d/%m/%Y'),
            'sections': sections, 'references': references}


def court_filename(result, extension):
    if extension not in {'pdf', 'docx'}:
        raise ValueError('Unsupported Court export format')
    document = result.get('court_report_document') if isinstance(result, dict) else {}
    metadata = result.get('metadata') if isinstance(result, dict) and isinstance(result.get('metadata'), dict) else {}
    title = clean_text((document or {}).get('case_title') or result.get('case_title') or metadata.get('case_title'))
    slug = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^A-Za-z0-9]+', '_', slug).strip('_')[:60].strip('_')
    suffix = slug or 'Informe_Simulacion_Juridica'
    return f'MYKE_NovaCourt_{suffix}.{extension}'


def court_report_blocks(content):
    blocks = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        heading = HEADING.match(line)
        if heading:
            blocks.append(('heading', clean_text(heading.group(1))))
        elif re.match(r'^\d+[.)]\s+', line):
            blocks.append(('numbered', clean_text(re.sub(r'^\d+[.)]\s+', '', line))))
        elif line.startswith(('- ', '* ')):
            blocks.append(('list', clean_text(line[2:])))
        else:
            blocks.append(('paragraph', clean_text(line)))
    return blocks
