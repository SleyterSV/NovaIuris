import os
import subprocess
import tempfile
import shutil
import io
from flask import Blueprint, request, send_file, jsonify

# ==========================================
# 1. DEFINICIÓN DEL BLUEPRINT (RUTAS)
# ==========================================
export_bp = Blueprint('export', __name__)

# ==========================================
# 2. LÓGICA DE GENERACIÓN LATEX
# ==========================================
def armar_latex(tipo: str, datos: dict) -> str:
    contenido_dinamico = ""
    
    if tipo == 'NovaCase':
        resumen = datos.get("resumenHechos", "Sin hechos registrados.")
        estrategia = datos.get("estrategiaSugerida", "Sin estrategia sugerida.")
        
        fundamentos_lista = datos.get("fundamentacionLegal", [])
        fundamentos = "\n".join([f"\\item {ley}" for ley in fundamentos_lista]) if fundamentos_lista else "\\item Sin fundamentos legales."
            
        jurisprudencia_lista = datos.get("jurisprudenciaClave", [])
        jurisprudencia = "\n".join([f"\\textbf{{{jur['titulo']}}} \\\\ {jur['extracto']} \\vspace{{0.5cm}}" for jur in jurisprudencia_lista]) if jurisprudencia_lista else "Sin jurisprudencia aplicable."
        
        contenido_dinamico = f"""
\\section{{Introducción y Hechos del Caso}}
{resumen}

\\section{{Fundamentación Legal}}
\\begin{{itemize}}
{fundamentos}
\\end{{itemize}}

\\section{{Jurisprudencia Clave}}
{jurisprudencia}

\\section{{Estrategia Sugerida}}
{estrategia}
"""
    elif tipo == 'NovaCourt':
        acciones = datos.get("allActions", [])
        transcripcion = "\n".join([f"\\textbf{{{linea.get('agent_name', 'Agente')}}}: \\\\ {linea.get('action_args', {}).get('content', '')} \\vspace{{0.3cm}}" for linea in acciones])
        contenido_dinamico = f"\\section{{Transcripción Oficial de la Audiencia}}\n{transcripcion}"

    return f"""\\documentclass[12pt, a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{graphicx}}
\\usepackage{{fancyhdr}}
\\usepackage[top=3cm, bottom=3cm, left=2.5cm, right=2.5cm, headheight=1.5cm]{{geometry}}
\\usepackage{{mathptmx}}
\\usepackage{{setspace}}
\\usepackage{{microtype}}
\\onehalfspacing

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\large\\textbf{{Nova Iuris}}}}
\\fancyhead[R]{{\\includegraphics[height=1.2cm]{{NovaIuris.png}}}} 
\\fancyfoot[C]{{- \\thepage\\ -}}
\\renewcommand{{\\headrulewidth}}{{0.8pt}} 

\\begin{{document}}
\\begin{{titlepage}}
    \\centering
    \\vspace*{{1cm}} 
    \\includegraphics[width=8cm]{{NovaIuris.png}}\\par
    \\vspace{{1.5cm}}
    \\rule{{0.8\\textwidth}}{{0.5pt}}\\par
    \\vspace{{0.8cm}}
    {{\\large \\textsc{{Documento Generado por {tipo}}}}}\\par
    \\vspace{{0.8cm}}
    \\rule{{0.8\\textwidth}}{{0.5pt}}\\par
    \\vspace{{2.5cm}}
    {{\\Huge \\textbf{{NOVA IURIS}}}}\\par
    \\vspace{{0.5cm}}
    {{\\Large \\textit{{Reporte de Análisis Legal Oficial}}}}\\par
    \\vfill
    \\begin{{flushright}}
        \\rule{{5cm}}{{0.5pt}}\\\\
        \\vspace{{0.2cm}}
        {{\\large \\textbf{{Fecha de emisión:}}}}\\\\
        {{\\large \\today\\par}}
    \\end{{flushright}}
    \\vspace{{1cm}}
\\end{{titlepage}}
\\newpage
{contenido_dinamico}
\\end{{document}}"""

# ==========================================
# 3. ENDPOINT DE COMPILACIÓN
# ==========================================
# Legacy LaTeX formatter above is retained, but external compilation is disabled.
from flask import g
from ..utils.api_response import api_error
from ..services.document_output import prepare_document

@export_bp.route('/prepare', methods=['POST'])
def prepare_export():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error('INVALID_EXPORT', 'Debe enviar un objeto JSON válido.', g.request_id, 400)
    try:
        document = prepare_document(data.get('case_id'), data.get('result'), data.get('tool'))
    except (ValueError, TypeError):
        return api_error('INVALID_EXPORT', 'El resultado debe corresponder al case_id indicado.', g.request_id, 400)
    return jsonify(success=True, document=document)

@export_bp.route('/pdf', methods=['POST'])
def generar_pdf():
    return api_error('DOCUMENT_OUTPUT_PENDING', 'La exportación PDF está pendiente del bloque Document Output.', g.request_id, 501)
