"""A4 PDF renderer using the existing NovaCase/PyMuPDF Story export engine."""
import fitz

from .case_pdf import _inline
from .court_report_content import court_report_blocks, court_report_content


def render_court_pdf(result):
    content = court_report_content(result)
    parts = ['<header><small>MYKE · LEGAL INTELLIGENCE</small>',
             f'<h1>{_inline(content["title"])}</h1>',
             '<p class="product">NovaCourt</p>']
    if content['case_title']:
        parts.append(f'<h2 class="case-title">{_inline(content["case_title"])}</h2>')
    parts += ['<p class="disclaimer">Simulación jurídica. No constituye una resolución judicial real ni sustituye la evaluación profesional.</p>',
              f'<p class="date">Generado: {_inline(content["date"])}</p></header>']
    for section in content['sections']:
        parts.append(f'<section><h2>{_inline(section["title"])}</h2>')
        for kind, value in court_report_blocks(section['content']):
            if kind == 'heading':
                parts.append(f'<h3>{_inline(value)}</h3>')
            elif kind in {'list', 'numbered'}:
                prefix = '• ' if kind == 'list' else ''
                parts.append(f'<p class="item">{prefix}{_inline(value)}</p>')
            else:
                parts.append(f'<p>{_inline(value)}</p>')
        parts.append('</section>')
    if content['references']:
        parts.append('<section class="references"><h2>Fuentes utilizadas</h2>')
        for group in ('DOCUMENTOS DEL CASO', 'FUENTES JURÍDICAS'):
            refs = [ref for ref in content['references'] if ref['group'] == group]
            if not refs:
                continue
            parts.append(f'<h3>{_inline(group)}</h3>')
            for ref in refs:
                detail = f' · {_inline(ref["detail"])}' if ref['detail'] else ''
                parts.append(f'<p class="reference"><b>{_inline(ref["label"])}</b> '
                             f'{_inline(ref["title"])}{detail}</p>')
        parts.append('</section>')
    html = '<body>' + ''.join(parts) + '</body>'
    css = '''
      body { font-family: sans-serif; font-size: 10.5pt; color: #26384b; line-height: 1.55; }
      header { border-bottom: 1px solid #c9d4df; padding-bottom: 16pt; margin-bottom: 20pt; }
      small { color: #97774b; font-size: 8pt; font-weight: bold; letter-spacing: 1pt; }
      h1 { color: #142f4d; font-size: 21pt; margin: 9pt 0 4pt; }
      .product { color: #97774b; font-size: 10pt; margin: 0 0 8pt; }
      .case-title { color: #284563; font-size: 13pt; margin: 10pt 0; }
      .disclaimer { color: #65758a; font-size: 8.5pt; margin: 10pt 0 4pt; }
      .date { color: #6b7888; font-size: 8pt; margin: 7pt 0 0; }
      section { margin-bottom: 18pt; } h2 { color: #17375e; font-size: 13pt; margin: 0 0 8pt; border-bottom: .5pt solid #dce4eb; padding-bottom: 5pt; }
      h3 { color: #284563; font-size: 10pt; margin: 10pt 0 5pt; }
      p { margin: 0 0 8pt; } .item { margin-left: 15pt; }
      .reference { padding-bottom: 5pt; } .references { break-before: auto; }
    '''
    page = fitz.paper_rect('a4')
    def rectfn(_number, _filled):
        return page, fitz.Rect(64, 62, page.width - 64, page.height - 68), None
    pdf = fitz.Story(html, user_css=css).write_with_links(rectfn)
    for number, sheet in enumerate(pdf, 1):
        sheet.draw_line((64, page.height - 45), (page.width - 64, page.height - 45), color=(.80, .84, .88))
        sheet.insert_text((64, page.height - 29), 'Generado por MYKE · NovaCourt', fontsize=8,
                          fontname='helv', color=(.43, .49, .56))
        sheet.insert_text((page.width - 85, page.height - 29), str(number), fontsize=8,
                          fontname='helv', color=(.43, .49, .56))
    data = pdf.tobytes(garbage=3, deflate=True)
    pdf.close()
    return data
