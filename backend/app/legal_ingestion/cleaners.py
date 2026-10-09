"""Conservative repeated page furniture removal."""
from collections import Counter
import re
from .models import Block
from .identity import search_normalize


def remove_repeated_page_furniture(blocks: list[Block], *, strip_verification=False,
                                   expanded_top=False) -> tuple[list[Block], int]:
    if strip_verification:
        footer_lines = (
            "esta es una representación impresa cuya autenticidad puede ser contrastada",
            "localizada en la sede digital del tribunal constitucional",
            "de publicación web de la presente resolución. base legal:",
            "029-2021-pcm y la directiva",
        )
        discard = set()
        for start, block in enumerate(blocks):
            first = search_normalize(block.text).casefold()
            if not first.startswith(footer_lines[0]):
                continue
            for end in range(start + 1, min(start + 6, len(blocks))):
                candidate = blocks[end]
                if candidate.page != block.page:
                    break
                line = search_normalize(candidate.text).casefold()
                if re.match(r"^url:\s*https?://(?:www\.)?tc\.gob\.pe/", line):
                    discard.update(range(start, end + 1))
                    break
                if not any(line.startswith(prefix) for prefix in footer_lines[1:]):
                    break
        footer_removed = len(discard)
        blocks = [block for index, block in enumerate(blocks) if index not in discard]
    else:
        footer_removed = 0
    pages: dict[int, list[Block]] = {}
    for block in blocks:
        if block.page is not None:
            pages.setdefault(block.page, []).append(block)
    if len(pages) < 3:
        return blocks, footer_removed
    top_lines = 7 if expanded_top else 5
    candidates = Counter()
    for page_blocks in pages.values():
        edges = page_blocks[:top_lines] + page_blocks[-5:]
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
        edge = page_blocks and any(block is item for item in page_blocks[:top_lines] + page_blocks[-5:])
        key = search_normalize(block.text).casefold()
        # Never strip a line that starts a legal unit, even if repeated.
        legal_start = re.match(r"^(art[ií]culos?|fundamentos?|decisi[oó]n|resuelve|sumilla|libro|secci[oó]n|t[ií]tulo|cap[ií]tulo|visto|antecedentes|considerando|primero|segundo|tercero)\b", key)
        if edge and key in repeated and not legal_start:
            removed += 1
        else:
            kept.append(block)
    return kept, removed + footer_removed
