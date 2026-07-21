"""Dependency-free validation for callsigns and Maidenhead locators."""

import re


# Strict ASCII allowlists for identities that can reach ClickHouse SQL.
_CALLSIGN_RE = re.compile(
    r"^(?=.{3,15}$)(?:[A-Z0-9]+/)*"
    r"(?:[A-Z0-9]*[A-Z][A-Z0-9]*[0-9][A-Z0-9]*|"
    r"[A-Z0-9]*[0-9][A-Z0-9]*[A-Z][A-Z0-9]*)"
    r"(?:/[A-Z0-9]+)*$"
)
_GRID4_RE = re.compile(r"^[A-R]{2}[0-9]{2}$")
_LOCATOR_RE = re.compile(r"^[A-R]{2}[0-9]{2}(?:[A-X]{2})?$")


def normalize_ascii_upper(value) -> str:
    """Strip text and uppercase it only when every input character is ASCII.

    Preserving non-ASCII text prevents Unicode case expansion from converting
    invalid input into a different, apparently valid identifier before the
    validator can reject it.
    """
    stripped_value = str(value or "").strip()
    return stripped_value.upper() if stripped_value.isascii() else stripped_value


def is_valid_callsign(callsign: str) -> bool:
    """Return whether a value is a plausible, SQL-safe WSPR callsign token.

    The validator accepts three to fifteen ASCII characters, optional non-empty
    slash-separated prefixes or suffixes, and requires at least one segment
    containing both a letter and a digit. It validates archive-token syntax,
    not whether a callsign has been legally assigned.
    """
    normalized_callsign = str(callsign or "").strip()
    if not normalized_callsign.isascii():
        return False
    normalized_callsign = normalized_callsign.upper()
    return bool(_CALLSIGN_RE.fullmatch(normalized_callsign))


def is_valid_grid4(locator: str) -> bool:
    """Return whether a locator is an exact four-character Maidenhead grid."""
    normalized_locator = str(locator or "").strip()
    if not normalized_locator.isascii():
        return False
    return bool(_GRID4_RE.fullmatch(normalized_locator.upper()))


def is_valid_locator(locator: str) -> bool:
    """Return whether a locator is a valid four- or six-character Maidenhead token."""
    normalized_locator = str(locator or "").strip()
    if not normalized_locator.isascii():
        return False
    return bool(_LOCATOR_RE.fullmatch(normalized_locator.upper()))


def is_valid_6char_locator(locator: str) -> bool:
    """Return whether a locator is an exact six-character Maidenhead locator."""
    locator = str(locator or "").strip()
    if not locator.isascii():
        return False
    locator = locator.upper()
    if len(locator) != 6:
        return False
    if not ("A" <= locator[0] <= "R" and "A" <= locator[1] <= "R"):
        return False
    if not (locator[2].isdigit() and locator[3].isdigit()):
        return False
    return "A" <= locator[4] <= "X" and "A" <= locator[5] <= "X"
