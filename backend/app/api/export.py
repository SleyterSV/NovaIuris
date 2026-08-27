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
@export_bp.route('/pdf', methods=['POST'])
def generar_pdf():
    doc_data = request.get_json()
    
    if not doc_data:
        return jsonify({"success": False, "error": "No se enviaron datos"}), 400
        
    tipo = doc_data.get('tipo', '')
    datos = doc_data.get('datos', {})
    
    if tipo not in ['NovaCase', 'NovaCourt']:
        return jsonify({"success": False, "error": "Tipo de documento no válido"}), 400

    latex_content = armar_latex(tipo, datos)
    temp_dir = tempfile.mkdtemp()
    
    try:
        tex_path = os.path.join(temp_dir, "documento.tex")
        pdf_path = os.path.join(temp_dir, "documento.pdf")
        
        # Inyección del logotipo (Asegúrate de que NovaIuris.png esté en la carpeta static del backend)
        logo_src = os.path.join(os.getcwd(), "static", "NovaIuris.png") 
        if os.path.exists(logo_src):
            shutil.copy(logo_src, os.path.join(temp_dir, "NovaIuris.png"))
        
        # Escribir el código LaTeX en el archivo
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_content)
            
        # Compilación doble para resolver referencias y márgenes
        try:
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "documento.tex"], cwd=temp_dir, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "documento.tex"], cwd=temp_dir, check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return jsonify({"success": False, "error": "Error compilando LaTeX. Verifica la instalación de pdflatex."}), 500

        if not os.path.exists(pdf_path):
            return jsonify({"success": False, "error": "No se pudo generar el PDF final."}), 500

        # Cargar el PDF compilado a la memoria RAM
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
    finally:
        # Limpieza de servidor obligatoria
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Retornar el archivo directamente desde la memoria
    return send_file(
        io.BytesIO(pdf_bytes), 
        mimetype="application/pdf", 
        as_attachment=True, 
        download_name=f"NovaIuris_{tipo}_Oficial.pdf"
    )