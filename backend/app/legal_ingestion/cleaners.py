"""Conservative repeated page furniture removal."""
from collections import Counter
import re
from .models import Block
from .identity import search_normalize


def remove_repeated_page_furniture(blocks: list[Block], *, strip_verification=False,
                                   expanded_top=False, strip_running_numbers=False,
                                   strip_two_page_headers=False) -> tuple[list[Block], int]:
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
    if len(pages) < 2 or (len(pages) == 2 and not strip_two_page_headers):
        return blocks, footer_removed
    top_lines = 7 if expanded_top else 5
    number_removed = 0
    if strip_running_numbers:
        # A running folio is an isolated number equal to the physical page,
        # at the same header position on most pages, beside a repeated header.
        # An isolated legal numeral or footnote cannot meet this pattern alone.
        number_positions = Counter()
        number_blocks = {}
        for page, page_blocks in pages.items():
            for position, block in enumerate(page_blocks[:top_lines]):
                if re.fullmatch(r"[1-9]\d{0,2}", block.text.strip()) and int(block.text.strip()) == page:
                    number_positions[position] += 1
                    number_blocks[page] = (position, block)
                    break
        minimum = max(3, (len(pages) * 7 + 9) // 10)
        if number_positions:
            position, count = number_positions.most_common(1)[0]
            if count >= minimum:
                header_counts = Counter()
                for page, page_blocks in pages.items():
                    if page not in number_blocks or number_blocks[page][0] != position:
                        continue
                    header_counts.update({search_normalize(block.text).casefold()
                                          for block in page_blocks[:top_lines]
                                          if block is not number_blocks[page][1]
                                          and 4 <= len(search_normalize(block.text)) <= 120})
                if any(count >= minimum for count in header_counts.values()):
                    discarded = {id(block) for pos, block in number_blocks.values() if pos == position}
                    number_removed = len(discarded)
                    blocks = [block for block in blocks if id(block) not in discarded]
                    pages = {}
                    for block in blocks:
                        if block.page is not None:
                            pages.setdefault(block.page, []).append(block)
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
    if len(pages) == 2:
        # A two-page resolution needs two independent, identical header lines
        # before either is treated as furniture; a single repeated phrase is
        # insufficient evidence for removing legal prose.
        first, second = list(pages.values())
        header_keys = [
            {search_normalize(block.text).casefold() for block in page[:top_lines]
             if 4 <= len(search_normalize(block.text)) <= 120}
            for page in (first, second)
        ]
        common = header_keys[0] & header_keys[1]
        common = {key for key in common if not re.match(
            r"^(art[ií]culos?|fundamentos?|decisi[oó]n|resuelve|sumilla|libro|secci[oó]n|"
            r"t[ií]tulo|cap[ií]tulo|visto|antecedentes|considerando|primero|segundo|tercero)\b", key)}
        repeated = common if len(common) >= 2 else set()
    kept, removed = [], 0
    for block in blocks:
        page_blocks = pages.get(block.page, [])
        edge_blocks = (page_blocks[:top_lines] if len(pages) == 2 else
                       page_blocks[:top_lines] + page_blocks[-5:])
        edge = page_blocks and any(block is item for item in edge_blocks)
        key = search_normalize(block.text).casefold()
        # Never strip a line that starts a legal unit, even if repeated.
        legal_start = re.match(r"^(art[ií]culos?|fundamentos?|decisi[oó]n|resuelve|sumilla|libro|secci[oó]n|t[ií]tulo|cap[ií]tulo|visto|antecedentes|considerando|primero|segundo|tercero)\b", key)
        if edge and key in repeated and not legal_start:
            removed += 1
        else:
            kept.append(block)
    return kept, removed + footer_removed + number_removed
