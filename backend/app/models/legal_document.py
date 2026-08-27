from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class LegalDocument:

    id: str

    hash_documento: str

    rama: str

    fuente: str

    tipo_documento: str

    jerarquia: str

    articulo: str

    texto: str

    resumen: str

    vigencia: str

    entidad: str

    numero: str

    fecha_publicacion: str

    keywords: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    embedding: Optional[List[float]] = None

    def to_dict(self):

        return asdict(self)