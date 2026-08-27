from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class JurisprudenceDocument:
    """
    Modelo que representa un documento jurisprudencial
    listo para ser indexado dentro de legal_knowledge.
    """

    # ==========================
    # Identificación
    # ==========================

    id: str
    hash_documento: str

    # ==========================
    # Clasificación
    # ==========================

    rama: str
    fuente: str

    tipo_documento: str
    jerarquia: str

    # ==========================
    # Información principal
    # ==========================

    articulo: str
    texto: str
    resumen: str

    # ==========================
    # Estado
    # ==========================

    vigencia: str = "Vigente"

    # ==========================
    # Metadatos generales
    # ==========================

    entidad: str = ""
    numero: str = ""
    fecha_publicacion: Optional[str] = None

    # ==========================
    # Metadatos jurisprudenciales
    # ==========================

    organo_emisor: str = ""

    expediente: str = ""

    tipo_resolucion: str = ""

    ponente: str = ""

    fecha_resolucion: Optional[str] = None

    sumilla: str = ""

    precedente_vinculante: bool = False

    materia: str = ""

    instancia: str = ""

    # ==========================
    # IA
    # ==========================

    keywords: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    embedding: Optional[List[float]] = None

    search_text: Optional[str] = None

    # ==========================
    # Conversión
    # ==========================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el dataclass a diccionario.
        """

        return asdict(self)

    # ==========================
    # Texto enriquecido
    # ==========================

    def build_search_text(self) -> str:
        """
        Construye un texto enriquecido para generar embeddings
        mucho más precisos.
        """

        partes = [

            self.rama,

            self.tipo_documento,

            self.tipo_resolucion,

            self.organo_emisor,

            self.expediente,

            self.materia,

            self.instancia,

            self.articulo,

            self.resumen,

            self.sumilla,

            " ".join(self.keywords),

            self.texto

        ]

        return "\n".join(
            p.strip()
            for p in partes
            if p and str(p).strip()
        )