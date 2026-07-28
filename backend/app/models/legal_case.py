"""

Gestión de Contexto de Casos Legales

Se utiliza para persistir el estado del caso en el servidor, evitando pasar grandes cantidades de datos entre interfaces.

"""



import os

import json

import uuid

import shutil

from datetime import datetime

from typing import Dict, Any, List, Optional

from enum import Enum

from dataclasses import dataclass, field, asdict

from ..config import Config





class CaseStatus(str, Enum):

    """Estado del caso legal"""

    CREATED = "created"              # Recién creado, archivos subidos

    INVESTIGATING = "investigating"  # Agentes investigadores buscando en la base vectorial y armando el dossier

    DEBATING = "debating"            # Fase de simulación activa: Fiscales vs Defensa

    COMPLETED = "completed"          # Simulación completada y veredicto emitido

    FAILED = "failed"                # Fallo en la simulación





@dataclass

class LegalCase:

    """Modelo de datos del caso legal"""

    case_id: str

    name: str

    status: CaseStatus

    created_at: str

    updated_at: str

   

    # Información de archivos (Pruebas/Documentos del caso)

    files: List[Dict[str, str]] = field(default_factory=list)  # [{filename, path, size}]

    total_text_length: int = 0

   

    # Detalles del caso (Ingresados por el usuario)

    jurisdiction: Optional[str] = None  # Ej: "Penal", "Civil", "Laboral"

    case_description: Optional[str] = None  # Resumen de los hechos ingresados

   

    # Base de conocimiento y resultados (Llenados por los agentes)

    dossier: Optional[Dict[str, Any]] = None  # Base armada por los investigadores

    debate_history: List[Dict[str, Any]] = field(default_factory=list) # Transcripción del debate

    verdict_summary: Optional[str] = None  # Análisis final del Agente Juez

   

    # Configuración de vectorización (RAG)

    chunk_size: int = 500

    chunk_overlap: int = 50

   

    # Información de errores

    error: Optional[str] = None

   

    def to_dict(self) -> Dict[str, Any]:

        """Convierte la instancia a un diccionario"""

        return {

            "case_id": self.case_id,

            "name": self.name,

            "status": self.status.value if isinstance(self.status, CaseStatus) else self.status,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "files": self.files,

            "total_text_length": self.total_text_length,

            "jurisdiction": self.jurisdiction,

            "case_description": self.case_description,

            "dossier": self.dossier,

            "debate_history": self.debate_history,

            "verdict_summary": self.verdict_summary,

            "chunk_size": self.chunk_size,

            "chunk_overlap": self.chunk_overlap,

            "error": self.error

        }

   

    @classmethod

    def from_dict(cls, data: Dict[str, Any]) -> 'LegalCase':

        """Crea una instancia desde un diccionario"""

        status = data.get('status', 'created')

        if isinstance(status, str):

            status = CaseStatus(status)

       

        return cls(

            case_id=data['case_id'],

            name=data.get('name', 'Caso Sin Nombre'),

            status=status,

            created_at=data.get('created_at', ''),

            updated_at=data.get('updated_at', ''),

            files=data.get('files', []),

            total_text_length=data.get('total_text_length', 0),

            jurisdiction=data.get('jurisdiction'),

            case_description=data.get('case_description'),

            dossier=data.get('dossier'),

            debate_history=data.get('debate_history', []),

            verdict_summary=data.get('verdict_summary'),

            chunk_size=data.get('chunk_size', 500),

            chunk_overlap=data.get('chunk_overlap', 50),

            error=data.get('error')

        )





class CaseManager:

    """Gestor de Casos - Responsable del almacenamiento y recuperación de casos"""

   

    # Directorio raíz para el almacenamiento de casos

    CASES_DIR = os.path.join(Config.UPLOAD_FOLDER, 'cases')

   

    @classmethod

    def _ensure_cases_dir(cls):

        """Asegura que el directorio de casos exista"""

        os.makedirs(cls.CASES_DIR, exist_ok=True)

   

    @classmethod

    def _get_case_dir(cls, case_id: str) -> str:

        """Obtiene la ruta del directorio del caso"""

        return os.path.join(cls.CASES_DIR, case_id)

   

    @classmethod

    def _get_case_meta_path(cls, case_id: str) -> str:

        """Obtiene la ruta del archivo de metadatos del caso"""

        return os.path.join(cls._get_case_dir(case_id), 'case.json')

   

    @classmethod

    def _get_case_files_dir(cls, case_id: str) -> str:

        """Obtiene el directorio de almacenamiento de archivos del caso"""

        return os.path.join(cls._get_case_dir(case_id), 'files')

   

    @classmethod

    def _get_case_text_path(cls, case_id: str) -> str:

        """Obtiene la ruta de almacenamiento del texto extraído del caso"""

        return os.path.join(cls._get_case_dir(case_id), 'extracted_text.txt')

   

    @classmethod

    def create_case(cls, name: str = "Caso Sin Nombre") -> LegalCase:

        """

        Crea un nuevo caso legal

       

        Args:

            name: Nombre del caso

           

        Returns:

            El nuevo objeto LegalCase creado

        """

        cls._ensure_cases_dir()

       

        case_id = f"case_{uuid.uuid4().hex[:12]}"

        now = datetime.now().isoformat()

       

        legal_case = LegalCase(

            case_id=case_id,

            name=name,

            status=CaseStatus.CREATED,

            created_at=now,

            updated_at=now

        )

       

        # Crear estructura de directorios del caso

        case_dir = cls._get_case_dir(case_id)

        files_dir = cls._get_case_files_dir(case_id)

        os.makedirs(case_dir, exist_ok=True)

        os.makedirs(files_dir, exist_ok=True)

       

        # Guardar metadatos del caso

        cls.save_case(legal_case)

       

        return legal_case

   

    @classmethod

    def save_case(cls, legal_case: LegalCase) -> None:

        """Guarda los metadatos del caso"""

        legal_case.updated_at = datetime.now().isoformat()

        meta_path = cls._get_case_meta_path(legal_case.case_id)

       

        with open(meta_path, 'w', encoding='utf-8') as f:

            json.dump(legal_case.to_dict(), f, ensure_ascii=False, indent=2)

   

    @classmethod

    def get_case(cls, case_id: str) -> Optional[LegalCase]:

        """

        Obtiene un caso

       

        Args:

            case_id: ID del caso

           

        Returns:

            Objeto LegalCase, o None si no existe

        """

        meta_path = cls._get_case_meta_path(case_id)

       

        if not os.path.exists(meta_path):

            return None

       

        with open(meta_path, 'r', encoding='utf-8') as f:

            data = json.load(f)

       

        return LegalCase.from_dict(data)

   

    @classmethod

    def list_cases(cls, limit: int = 50) -> List[LegalCase]:

        """

        Lista todos los casos

       

        Args:

            limit: Límite de cantidad a devolver

           

        Returns:

            Lista de casos, ordenados de forma descendente por fecha de creación

        """

        cls._ensure_cases_dir()

       

        cases = []

        for case_id in os.listdir(cls.CASES_DIR):

            legal_case = cls.get_case(case_id)

            if legal_case:

                cases.append(legal_case)

       

        # Ordenar por fecha de creación descendente

        cases.sort(key=lambda c: c.created_at, reverse=True)

       

        return cases[:limit]

   

    @classmethod

    def delete_case(cls, case_id: str) -> bool:

        """

        Elimina el caso y todos sus archivos asociados

       

        Args:

            case_id: ID del caso

           

        Returns:

            Booleano indicando si se eliminó con éxito

        """

        case_dir = cls._get_case_dir(case_id)

       

        if not os.path.exists(case_dir):

            return False

       

        shutil.rmtree(case_dir)

        return True

   

    @classmethod

    def save_file_to_case(cls, case_id: str, file_storage, original_filename: str) -> Dict[str, str]:

        """

        Guarda un archivo subido en el directorio del caso

       

        Args:

            case_id: ID del caso

            file_storage: Objeto FileStorage de Flask/FastAPI

            original_filename: Nombre original del archivo

           

        Returns:

            Diccionario con la información del archivo {filename, path, size}

        """

        files_dir = cls._get_case_files_dir(case_id)

        os.makedirs(files_dir, exist_ok=True)

       

        # Generar un nombre de archivo seguro

        ext = os.path.splitext(original_filename)[1].lower()

        safe_filename = f"{uuid.uuid4().hex[:8]}{ext}"

        file_path = os.path.join(files_dir, safe_filename)

       

        # Guardar archivo

        file_storage.save(file_path)

       

        # Obtener tamaño del archivo

        file_size = os.path.getsize(file_path)

       

        return {

            "original_filename": original_filename,

            "saved_filename": safe_filename,

            "path": file_path,

            "size": file_size

        }

   

    @classmethod

    def save_extracted_text(cls, case_id: str, text: str) -> None:

        """Guarda el texto extraído (ej. OCR de los documentos probatorios)"""

        text_path = cls._get_case_text_path(case_id)

        with open(text_path, 'w', encoding='utf-8') as f:

            f.write(text)

   

    @classmethod

    def get_extracted_text(cls, case_id: str) -> Optional[str]:

        """Obtiene el texto extraído"""

        text_path = cls._get_case_text_path(case_id)

       

        if not os.path.exists(text_path):

            return None

       

        with open(text_path, 'r', encoding='utf-8') as f:

            return f.read()

   

    @classmethod

    def get_case_files(cls, case_id: str) -> List[str]:

        """Obtiene todas las rutas de los archivos asociados al caso"""

        files_dir = cls._get_case_files_dir(case_id)

       

        if not os.path.exists(files_dir):

            return []

       

        return [

            os.path.join(files_dir, f)

            for f in os.listdir(files_dir)

            if os.path.isfile(os.path.join(files_dir, f))

        ]