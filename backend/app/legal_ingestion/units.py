"""Split only oversized legal units, at paragraph then sentence boundaries."""
from copy import deepcopy
import re
from .identity import content_hash, search_normalize


class OversizedUnitError(ValueError):
    pass


def split_oversized_unit(unit, max_tokens: int = 800):
    if max_tokens < 1:
        raise ValueError("max_tokens must be positive")
    if len(unit.text.split()) <= max_tokens:
        return [unit]
    paragraphs = [part.strip() for part in unit.text.splitlines() if part.strip()]
    atoms = []
    for paragraph in paragraphs:
        if len(paragraph.split()) <= max_tokens:
            atoms.append(paragraph)
            continue
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])", paragraph) if part.strip()]
        if any(len(sentence.split()) > max_tokens for sentence in sentences):
            raise OversizedUnitError("Legal unit has a sentence exceeding the embedding limit")
        atoms.extend(sentences)
    groups, current, count = [], [], 0
    for atom in atoms:
        atom_count = len(atom.split())
        if current and count + atom_count > max_tokens:
            groups.append(current)
            current, count = [], 0
        current.append(atom)
        count += atom_count
    if current:
        groups.append(current)
    if len(groups) < 2:
        raise OversizedUnitError("Oversized legal unit could not be split safely")
    output = []
    for index, group in enumerate(groups, 1):
        part = deepcopy(unit)
        part.text = "\n".join(group)
        part.normalized_text = search_normalize(part.text)
        part.part_number, part.part_count = index, len(groups)
        part.token_count = len(part.text.split())
        part.excerpt = part.normalized_text[:240]
        part.metadata = {**part.metadata, "parent_content_hash": unit.content_hash}
        part.content_hash = content_hash(part.unit_type, part.unit_number, part.heading,
                                         part.normalized_text, part.part_number,
                                         hierarchy={"book": part.book, "section": part.section,
                                                    "title": part.title, "chapter": part.chapter})
        output.append(part)
    return output


def contextual_search_text(document, unit) -> str:
    parts = [document.title, document.metadata.get("court"), document.metadata.get("expediente"),
             document.metadata.get("resolution_type"), document.metadata.get("materia"),
             "Precedente vinculante" if document.metadata.get("precedent_binding") is True else None,
             unit.unit_type.replace("_", " ").title(), unit.unit_number,
             unit.heading, unit.normalized_text]
    return "\n".join(str(part).strip() for part in parts if part and str(part).strip())


def embedding_batches(units, embed_batch, batch_size=32):
    """Inject a provider adapter in a later pilot; no network dependency here."""
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    vectors = []
    for start in range(0, len(units), batch_size):
        batch = units[start:start + batch_size]
        generated = embed_batch([unit.search_text for unit in batch])
        if len(generated) != len(batch):
            raise ValueError("Embedding batch count mismatch")
        for vector in generated:
            if len(vector) != 1536:
                raise ValueError("Embedding dimension must be 1536")
            vectors.append(vector)
    return vectors
