"""Render a completed, server-owned NovaCase report as a restrained A4 PDF."""
from html import escape
import re

import fitz

from .case_report_content import report_blocks, report_content


def _inline(value):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escape(str(value or '')))


def render_case_pdf(result):
    content = report_content(result)
    parts = ['<header><small>NOVACASE · INFORME JURÍDICO</small>',
             f'<h1>{_inline(content["title"])}</h1>',
             '<p class="intro">Documento de análisis preparado para revisión profesional.</p>']
    if content['date']:
        parts.append(f'<p class="date">Generado: {_inline(content["date"])}</p>')
    parts.append('</header>')
    for section in content['sections']:
        parts.append(f'<section><h2>{_inline(section["title"])}</h2>')
        for kind, value in report_blocks(section['content'], section['title']):
            tag = {'heading': 'h3', 'list': 'p', 'paragraph': 'p'}[kind]
            css_class = ' class="item"' if kind == 'list' else ''
            prefix = '• ' if kind == 'list' else ''
            parts.append(f'<{tag}{css_class}>{prefix}{_inline(value)}</{tag}>')
        parts.append('</section>')
    if content['references']:
        parts.append('<section><h2>Fuentes utilizadas</h2>')
        for reference in content['references']:
            detail = f' · {_inline(reference["detail"])}' if reference['detail'] else ''
            parts.append(f'<p class="reference"><b>{_inline(reference["label"])}</b> '
                         f'{_inline(reference["title"])}{detail}</p>')
        parts.append('</section>')
    html = '<body>' + ''.join(parts) + '</body>'
    css = '''
      body { font-family: sans-serif; font-size: 10.5pt; color: #26384b; line-height: 1.55; }
      header { border-bottom: 1px solid #c9d4df; padding-bottom: 16pt; margin-bottom: 20pt; }
      small { color: #97774b; font-size: 8pt; font-weight: bold; letter-spacing: 1pt; }
      h1 { color: #142f4d; font-size: 22pt; margin: 9pt 0 4pt; }
      .intro { color: #5c6d7f; margin: 3pt 0; }
      .date { color: #6b7888; font-size: 8pt; margin: 9pt 0 0; }
      section { margin-bottom: 18pt; }
      h2 { color: #17375e; font-size: 13pt; margin: 0 0 8pt; border-bottom: 0.5pt solid #dce4eb; padding-bottom: 5pt; }
      h3 { color: #284563; font-size: 11pt; margin: 10pt 0 5pt; }
      p { margin: 0 0 8pt; } .item { margin-left: 12pt; }
      .reference { padding-bottom: 5pt; }
    '''
    page = fitz.paper_rect('a4')

    def rectfn(_number, _filled):
        return page, fitz.Rect(64, 64, page.width - 64, page.height - 68), None

    pdf = fitz.Story(html, user_css=css).write_with_links(rectfn)
    for number, sheet in enumerate(pdf, 1):
        sheet.draw_line((64, page.height - 45), (page.width - 64, page.height - 45),
                        color=(0.80, 0.84, 0.88))
        sheet.insert_text((64, page.height - 29), 'Generado por MYKE',
                          fontsize=8, fontname='helv', color=(0.43, 0.49, 0.56))
        sheet.insert_text((page.width - 85, page.height - 29), str(number),
                          fontsize=8, fontname='helv', color=(0.43, 0.49, 0.56))
    data = pdf.tobytes(garbage=3, deflate=True)
    pdf.close()
    return data
