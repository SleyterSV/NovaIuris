"""Render a completed, server-owned NovaCase report as a restrained A4 PDF."""
from datetime import datetime
from html import escape
import re

import fitz


_TECHNICAL_REFERENCE = re.compile(r'\b(?:FACT|SRC)-[0-9a-f-]{8,}\b', re.IGNORECASE)


def _inline(value):
    text = _TECHNICAL_REFERENCE.sub('', str(value or ''))
    text = escape(text.strip())
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)


def _body_html(value):
    blocks = []
    for raw in str(value or '').splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(('### ', '## ')):
            blocks.append(f'<h3>{_inline(line.lstrip("# "))}</h3>')
        elif line.startswith(('- ', '* ')):
            blocks.append(f'<p class="item">• {_inline(line[2:])}</p>')
        else:
            blocks.append(f'<p>{_inline(line)}</p>')
    return ''.join(blocks)


def render_case_pdf(result):
    """Use only the persisted report; never accept browser-supplied prose."""
    if not isinstance(result, dict) or result.get('success') is not True:
        raise ValueError('Completed result required')
    report = result.get('report')
    if not isinstance(report, str) or not report.strip():
        raise ValueError('Report unavailable')
    document = result.get('report_document') or {}
    if document and document.get('case_id') != result.get('case_id'):
        raise ValueError('Report case mismatch')
    sections = document.get('sections') if isinstance(document.get('sections'), list) else []
    if not sections:
        sections = [{'title': 'Informe jurídico', 'content': report}]
    title = _inline(document.get('title') or 'Informe jurídico')
    generated = document.get('generated_at')
    date_label = ''
    if generated:
        try:
            date_label = datetime.fromisoformat(generated.replace('Z', '+00:00')).strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            pass
    parts = ['<header><small>NOVACASE · INFORME JURÍDICO</small>',
             f'<h1>{title}</h1>',
             '<p class="intro">Documento preparado para revisión profesional.</p>']
    if date_label:
        parts.append(f'<p class="date">Fecha de generación: {date_label}</p>')
    parts.append('</header><aside>Esta síntesis requiere revisión integral de los hechos, documentos y fuentes originales antes de su uso profesional.</aside>')
    for section in sections:
        if not isinstance(section, dict) or not isinstance(section.get('content'), str) or not section['content'].strip():
            continue
        parts.append(f'<section><h2>{_inline(section.get("title") or "Sección")}</h2>'
                     f'{_body_html(section["content"])}</section>')
    citations = document.get('citations') if isinstance(document.get('citations'), list) else []
    sources = document.get('sources') if isinstance(document.get('sources'), list) else []
    source_by_id = {source.get('source_id'): source for source in sources if isinstance(source, dict)}
    references = []
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        source = source_by_id.get(citation.get('source_id'))
        if not source:
            continue
        label = _inline(citation.get('label') or '')
        title_text = _inline(source.get('display_title') or source.get('title') or 'Fuente utilizada')
        locator = source.get('locator') or source.get('article') or source.get('legal_basis')
        page_number = source.get('page_start')
        details = []
        if locator:
            details.append(_inline(locator))
        if page_number:
            details.append(f'pág. {_inline(page_number)}')
        suffix = ' · '.join(details)
        references.append(f'<p>{label} {title_text}{" — " + suffix if suffix else ""}</p>')
    if references:
        parts.append('<section><h2>Fuentes utilizadas</h2>' + ''.join(references) + '</section>')
    html = '<body>' + ''.join(parts) + '</body>'
    css = '''
      body { font-family: sans-serif; font-size: 10.5pt; color: #26384b; line-height: 1.5; }
      header { border-bottom: 1px solid #c9d4df; padding-bottom: 16pt; margin-bottom: 18pt; }
      small { color: #97774b; font-size: 8pt; font-weight: bold; letter-spacing: 1pt; }
      h1 { color: #142f4d; font-size: 22pt; margin: 9pt 0 4pt; }
      .intro { color: #5c6d7f; margin: 3pt 0; }
      .date { color: #6b7888; font-size: 8pt; margin: 9pt 0 0; }
      aside { background: #f7f3ea; border-left: 2pt solid #b69a6a; padding: 9pt 12pt; font-size: 8.5pt; color: #594f40; margin-bottom: 19pt; }
      section { margin-bottom: 17pt; }
      h2 { color: #17375e; font-size: 13pt; margin: 0 0 7pt; border-bottom: 0.5pt solid #dce4eb; padding-bottom: 5pt; }
      h3 { color: #284563; font-size: 11pt; margin: 10pt 0 4pt; }
      p { margin: 0 0 7pt; } .item { margin-left: 12pt; }
    '''
    page = fitz.paper_rect('a4')
    def rectfn(_number, _filled):
        return page, fitz.Rect(54, 54, page.width - 54, page.height - 62), None
    pdf = fitz.Story(html, user_css=css).write_with_links(rectfn)
    for sheet in pdf:
        sheet.draw_line((54, page.height - 44), (page.width - 54, page.height - 44), color=(0.80, 0.84, 0.88))
        sheet.insert_text((page.width - 142, page.height - 29), 'Generado por MYKE',
                          fontsize=8, fontname='helv', color=(0.43, 0.49, 0.56))
    data = pdf.tobytes(garbage=3, deflate=True)
    pdf.close()
    return data
