"""
文件解析工具
支持PDF、Markdown、TXT、DOCX文件的文本提取
"""

import os
from pathlib import Path
from typing import List, Optional
import re
import logging
import json
import docx  # Añadido para soporte de Word

logger = logging.getLogger(__name__)

def _read_text_with_fallback(file_path: str) -> str:
    """
    读取文本文件，UTF-8失败时自动探测编码。
    """
    data = Path(file_path).read_bytes()
    
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    encoding = None
    try:
        from charset_normalizer import from_bytes
        best = from_bytes(data).best()
        if best and best.encoding:
            encoding = best.encoding
    except Exception:
        pass
    
    if not encoding:
        try:
            import chardet
            result = chardet.detect(data)
            encoding = result.get('encoding') if result else None
        except Exception:
            pass
    
    if not encoding:
        encoding = 'utf-8'
    
    return data.decode(encoding, errors='replace')


class FileParser:
    """文件解析器"""
    SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.markdown', '.txt', '.docx'}
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        suffix = path.suffix.lower()
        if suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {suffix}")
        
        if suffix == '.pdf':
            return cls._extract_from_pdf(file_path)
        elif suffix in {'.md', '.markdown'}:
            return cls._extract_from_md(file_path)
        elif suffix == '.txt':
            return cls._extract_from_txt(file_path)
        elif suffix == '.docx':
            return cls._extract_from_docx(file_path)
        raise ValueError(f"无法处理的文件格式: {suffix}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        try:
            import fitz 
        except ImportError:
            raise ImportError("需要安装PyMuPDF: pip install PyMuPDF")
        text_parts = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
        return "\n\n".join(text_parts)

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return '\n'.join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
    
    @staticmethod
    def _extract_from_md(file_path: str) -> str:
        return _read_text_with_fallback(file_path)
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        return _read_text_with_fallback(file_path)

def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """将文本分割成小块"""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            for sep in ['。', '！', '？', '.\n', '!\n', '?\n', '\n\n', '. ', '! ', '? ']:
                last_sep = text[start:end].rfind(sep)
                if last_sep != -1 and last_sep > chunk_size * 0.3:
                    end = start + last_sep + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end < len(text) else len(text)
    return chunks

# ====================================================================
# NUEVA LÓGICA ATÓMICA (ESPECIALIZADA EN FORMATO SPIJ PERUANO)
# ====================================================================
class LegalParser:
    def __init__(self, document_path: str, rama: str, fuente: str):
        self.document_path = Path(document_path)
        self.rama = rama
        self.fuente = fuente
        self.parsed_data = {}

    def extract_text(self) -> str:
        try:
            if self.document_path.suffix.lower() == '.docx':
                doc = docx.Document(self.document_path)
                full_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
                return '\n'.join(full_text)
            
            with open(self.document_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error leyendo el archivo {self.document_path}: {e}")
            return ""

    def parse_articles(self) -> list:
        raw_text = self.extract_text()
        if not raw_text:
            return []
        
        paragraphs = raw_text.split('\n')
        current_article_key = None
        current_buffer = []
        
        # Regex ULTRA estricto: Busca "Artículo", espacio, un número (con posibles letras/guiones como 124-B), 
        # y que termine con un punto, guion o grado (.-°). Ignora menciones a mitad de oración.
        article_start_pattern = re.compile(r'^(?:Artículo|Articulo|ARTÍCULO|ARTICULO)\s+(\d+[A-Z\-]*)(?:[.-°]|\s|$)', re.IGNORECASE)

        for line in paragraphs:
            clean_line = line.strip()
            if not clean_line:
                continue

            # IGNORAR artículos históricos que el SPIJ pone entre comillas (ej: '"Artículo 108.- ...')
            if clean_line.startswith('"') or clean_line.startswith('”'):
                if current_article_key:
                    current_buffer.append(clean_line)
                continue

            match = article_start_pattern.match(clean_line)
            if match:
                # 1. ESTANDARIZAR: Forzamos a que la llave sea siempre "ARTÍCULO X" en mayúsculas
                numero_articulo = match.group(1).upper()
                nueva_llave = f"ARTÍCULO {numero_articulo}"

                # 2. GUARDAR EL ANTERIOR (Solo si es la primera vez que lo vemos)
                if current_article_key:
                    # REGLA SPIJ: La versión vigente siempre es la primera. Ignoramos las repetidas abajo.
                    if current_article_key not in self.parsed_data:
                        self.parsed_data[current_article_key] = self._build_node(current_article_key, current_buffer)
                
                # 3. EMPEZAR EL NUEVO
                current_article_key = nueva_llave
                current_buffer = [clean_line]
            else:
                # Acumular el texto del cuerpo del artículo
                if current_article_key:
                    current_buffer.append(clean_line)

        # Guardar el último artículo del documento
        if current_article_key and current_article_key not in self.parsed_data:
            self.parsed_data[current_article_key] = self._build_node(current_article_key, current_buffer)
                
        logger.info(f"✅ Se consolidaron {len(self.parsed_data)} artículos ÚNICOS Y VIGENTES de {self.fuente}.")
        return list(self.parsed_data.values())

    def _build_node(self, key: str, lines: List[str]) -> dict:
        full_text = " ".join(lines)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        return {
            "rama": self.rama,
            "fuente": self.fuente,
            "articulo": key,
            "texto": full_text,
            "vigencia": "Vigente"
        }

    def get_parsed_data(self) -> list:
        return list(self.parsed_data.values())

# ==========================================
# BLOQUE DE EJECUCIÓN 
# ==========================================
if __name__ == "__main__":
    
    documentos_a_procesar = [
        # --- DOMINIO PENAL ---
        {"path": "raw_docs/CODIGO PENAL.docx", "rama": "Derecho Penal", "fuente": "Código Penal Peruano"},
        {"path": "raw_docs/NUEVO CODIGO PROCESAL PENAL (D.L 957).docx", "rama": "Derecho Procesal Penal", "fuente": "Nuevo Código Procesal Penal"},
        {"path": "raw_docs/CODIGO DE EJECUCION PENAL.docx", "rama": "Derecho Penal", "fuente": "Código de Ejecución Penal"},
        
        # --- DOMINIO CIVIL Y FAMILIA ---
        {"path": "raw_docs/CODIGO CIVIL.docx", "rama": "Derecho Civil", "fuente": "Código Civil Peruano"},
        {"path": "raw_docs/(TUO) CODIGO PROCESAL CIVIL.docx", "rama": "Derecho Procesal Civil", "fuente": "Texto Único Ordenado del Código Procesal Civil"},
        {"path": "raw_docs/CODIGO DE LOS NIÑOS Y ADOLESCENTES.docx", "rama": "Derecho de Familia", "fuente": "Código de los Niños y Adolescentes"},
        
        # --- DOMINIO CONSTITUCIONAL ---
        {"path": "raw_docs/CONSTITUCION POLITICA.docx", "rama": "Derecho Constitucional", "fuente": "Constitución Política del Perú"},
        {"path": "raw_docs/NUEVO CODIGO PROCESAL CONSTITUCIONAL.docx", "rama": "Derecho Constitucional", "fuente": "Nuevo Código Procesal Constitucional"},
        
        # --- DOMINIO CORPORATIVO, ESTATAL Y SOCIAL (LOS NUEVOS TITANES) ---
        {"path": "raw_docs/LEY GENERAL DE SOCIEDADES.docx", "rama": "Derecho Corporativo", "fuente": "Ley General de Sociedades"},
        {"path": "raw_docs/LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL.docx", "rama": "Derecho Administrativo", "fuente": "TUO Ley del Procedimiento Administrativo General"},
        {"path": "raw_docs/NUEVA LEY PROCESAL DEL TRABAJO.docx", "rama": "Derecho Laboral", "fuente": "Nueva Ley Procesal del Trabajo"},
        {"path": "raw_docs/TEXTO UNICO ORDENADO DEL CODIGO TRIBUTARIO.docx", "rama": "Derecho Tributario", "fuente": "TUO Código Tributario"},
        {"path": "raw_docs/CODIGO DE PROTECCION Y DEFENSA DEL CONSUMIDOR.docx", "rama": "Derecho del Consumidor", "fuente": "Código de Protección y Defensa del Consumidor"}
    ]

    output_dir = Path("processed_docs")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n🚀 Iniciando el procesamiento ATÓMICO de los archivos Word...\n")
    
    for doc in documentos_a_procesar:
        file_path = Path(doc["path"])
        if not file_path.exists():
            print(f"⚠️ Archivo no encontrado, saltando: {file_path}")
            continue
            
        print(f"Procesando: {doc['fuente']}...")
        parser = LegalParser(document_path=str(file_path), rama=doc["rama"], fuente=doc["fuente"])
        parser.parse_articles()
        
        nombre_limpio = file_path.stem.lower().replace(" ", "_").replace("(", "").replace(")", "")
        json_output_path = output_dir / f"{nombre_limpio}_estructurado.json"
        
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(parser.get_parsed_data(), f, ensure_ascii=False, indent=4)
            
        print(f"📁 Guardado exitosamente en -> {json_output_path}\n")
        
    print("✅ ¡Procesamiento completado! Revisa tu nueva carpeta 'processed_docs'.")