"""Deterministic legal case identity and decision intent for V2 queries."""

import re
import unicodedata


_TC_CASE = re.compile(
    r"(?<![\w/])(?P<number>\d{1,5})\s*[-\u2013\u2014]\s*"
    r"(?P<year>(?:19|20)\d{2})\s*[-\u2013\u2014]\s*"
    r"(?P<kind>[A-Za-z]{1,6})\s*/\s*TC\b",
    re.IGNORECASE,
)
_DECISION = re.compile(r"\b(?:resolvio|resuelve|resuelto|decision|decidio|fallo|parte resolutiva)\b")
_VIGENCIA = re.compile(r"\b(?:vigente|vigencia|derogada?|derogacion|validez|valido|actualmente en vigor)\b")
_NUMBERED_UNIT = re.compile(r"\b(fundamento|fundamentos|articulo|articulos)\s+(?:n\s*\.?\s*[°ºo]?\s*)?(\d{1,4})\b")
_VOTE = re.compile(r"\b(?:voto|votos|opinion separada)\b")


def _plain(text):
    decomposed = unicodedata.normalize("NFD", str(text or "").casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def explicit_tc_expediente(query):
    """Return one canonical TC expediente; reject ambiguous multiple identities."""
    found = {
        f"{match.group('number').zfill(5)}-{match.group('year')}-{match.group('kind').upper()}/TC"
        for match in _TC_CASE.finditer(str(query or ""))
    }
    if len(found) > 1:
        raise ValueError("MULTIPLE_EXACT_CASES")
    return next(iter(found), None)


def asks_for_decision(query):
    return bool(_DECISION.search(_plain(query)))


def exact_unit_intent(query):
    """Identify one explicit unit request; ambiguous numbered requests fail closed."""
    plain = _plain(query)
    numbered = {(('foundation' if kind.startswith('fundamento') else 'article'), str(int(number)))
                for kind, number in _NUMBERED_UNIT.findall(plain)}
    if len(numbered) > 1:
        raise ValueError("MULTIPLE_EXACT_UNITS")
    if numbered:
        return next(iter(numbered))
    if _VOTE.search(plain):
        return ("separate_opinion", None)
    if asks_for_decision(query):
        return ("decision", None)
    return None


def asks_about_vigencia(query):
    return bool(_VIGENCIA.search(_plain(query)))
