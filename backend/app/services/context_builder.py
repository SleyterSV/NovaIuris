"""Build model context together with the exact, traceable source records."""

from app.services.source_contracts import normalize_public_source


class ContextBuilder:
    MAX_DOCUMENTS = 5
    MAX_CHARS_PER_DOCUMENT = 1800

    def build(self, query: str, documents: list[dict]) -> dict:
        if not documents:
            return {"text": "", "sources": []}
        blocks, sources = [], []
        for document in documents[:self.MAX_DOCUMENTS]:
            excerpt = str(document.get("texto") or "")[:self.MAX_CHARS_PER_DOCUMENT]
            source = normalize_public_source(document, excerpt=excerpt)
            sources.append(source)
            metadata = source.get("metadata") or {}
            details = [
                f"Título: {source.get('title')}",
                f"Tipo: {source.get('source_type')}",
                f"Jerarquía: {document.get('jerarquia') or ''}",
                f"Rama: {document.get('rama') or ''}",
                f"Entidad: {source.get('entity') or ''}",
                f"Tribunal: {source.get('court') or ''}",
                f"Expediente: {source.get('case_number') or ''}",
                f"Materia: {document.get('materia') or ''}",
                f"Instancia: {document.get('instancia') or ''}",
                f"Número: {source.get('document_number') or ''}",
                f"Artículo: {source.get('article') or ''}",
                f"Fundamento: {source.get('legal_basis') or ''}",
                f"Fecha de resolución: {document.get('fecha_resolucion') or ''}",
                f"Fecha de publicación: {document.get('fecha_publicacion') or ''}",
                f"Precedente vinculante: {document.get('precedente_vinculante') or ''}",
                f"Sumilla: {document.get('sumilla') or metadata.get('sumilla') or ''}",
                f"Resumen: {document.get('resumen') or 'No disponible.'}",
                f"Fragmento exacto: {excerpt}",
            ]
            blocks.append(f"[{source['source_id']}]\n" + "\n".join(details))
        context = (
            "CONSULTA DEL USUARIO\n" + str(query or "") +
            "\n\nFUENTES JURÍDICAS RECUPERADAS\n\n" + "\n\n".join(blocks)
        )
        return {"text": context, "sources": sources}

    @staticmethod
    def is_valid_context(context: str | dict) -> bool:
        value = context.get("text", "") if isinstance(context, dict) else context
        return bool(value and len(value.strip()) >= 50)

    @staticmethod
    def statistics(context: str | dict) -> dict:
        value = context.get("text", "") if isinstance(context, dict) else context or ""
        return {"characters": len(value), "words": len(value.split()), "lines": len(value.splitlines())}
