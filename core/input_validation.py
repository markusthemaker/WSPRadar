"""Dependency-free validation for callsigns and Maidenhead locators."""

import re


# Strict allowlist for amateur-radio callsigns interpolated into ClickHouse SQL.
_CALLSIGN_RE = re.compile(r"^[A-Z0-9/]{3,15}$")
_LOCATOR_RE = re.compile(r"^[A-Z]{2}[0-9]{2}([A-Z]{2})?$")


def is_valid_callsign(callsign: str) -> bool:
    """Return whether a callsign contains only allowed characters and length."""
    return bool(_CALLSIGN_RE.match(callsign.upper().strip()))


def is_valid_locator(locator: str) -> bool:
    """Return whether a locator has the accepted four- or six-character form."""
    return bool(_LOCATOR_RE.match(locator.upper().strip()))


def is_valid_6char_locator(locator: str) -> bool:
    """Return whether a locator is an exact six-character Maidenhead locator."""
    locator = locator.upper().strip()
    if len(locator) != 6:
        return False
    if not ("A" <= locator[0] <= "R" and "A" <= locator[1] <= "R"):
        return False
    if not (locator[2].isdigit() and locator[3].isdigit()):
        return False
    return "A" <= locator[4] <= "X" and "A" <= locator[5] <= "X"
