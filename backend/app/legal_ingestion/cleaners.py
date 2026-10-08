"""Conservative repeated page furniture removal."""
from collections import Counter
import re
from .models import Block
from .identity import search_normalize


def remove_repeated_page_furniture(blocks: list[Block]) -> tuple[list[Block], int]:
    pages: dict[int, list[Block]] = {}
    for block in blocks:
        if block.page is not None:
            pages.setdefault(block.page, []).append(block)
    if len(pages) < 3:
        return blocks, 0
    candidates = Counter()
    for page_blocks in pages.values():
        edges = page_blocks[:5] + page_blocks[-5:]
        seen_on_page = set()
        for block in edges:
            key = search_normalize(block.text).casefold()
            if 2 <= len(key) <= 120 and key not in seen_on_page:
                candidates[key] += 1
                seen_on_page.add(key)
    repeated = {key for key, count in candidates.items() if count >= max(3, len(pages) - 1)}
    kept, removed = [], 0
    for block in blocks:
        page_blocks = pages.get(block.page, [])
        edge = page_blocks and any(block is item for item in page_blocks[:5] + page_blocks[-5:])
        key = search_normalize(block.text).casefold()
        # Never strip a line that starts a legal unit, even if repeated.
        legal_start = re.match(r"^(art[ií]culos?|fundamentos?|decisi[oó]n|resuelve|sumilla|libro|secci[oó]n|t[ií]tulo|cap[ií]tulo|visto|antecedentes|considerando|primero|segundo|tercero)\b", key)
        if edge and key in repeated and not legal_start:
            removed += 1
        else:
            kept.append(block)
    return kept, removed
