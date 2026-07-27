"""Synchronize canonical WSPRadar query entries without changing page navigation."""

from collections.abc import Sequence

import streamlit as st


URL_QUERY_SYNCHRONIZER_KEY = "wspradar_url_query_synchronizer"

_URL_QUERY_SYNCHRONIZER_HTML = """
<span class="url-query-synchronizer-sentinel" aria-hidden="true"></span>
"""

_URL_QUERY_SYNCHRONIZER_CSS = """
:host {
    display: block;
    height: 1px;
    margin: 0;
    overflow: hidden;
    padding: 0;
}

.url-query-synchronizer-sentinel {
    display: block;
    height: 1px;
    pointer-events: none;
    width: 100%;
}
"""

_URL_QUERY_SYNCHRONIZER_JS = """
export default function(component) {
    const { data } = component;
    const ownedKeys = data?.ownedKeys ?? [];
    const canonicalEntries = data?.entries ?? [];
    const searchParameters = new URLSearchParams(window.location.search);

    for (const ownedKey of ownedKeys) {
        searchParameters.delete(ownedKey);
    }
    for (const [key, value] of canonicalEntries) {
        searchParameters.append(key, value);
    }

    const encodedQuery = searchParameters.toString();
    const nextSearch = encodedQuery ? `?${encodedQuery}` : '';
    const currentRelativeUrl = (
        `${window.location.pathname}${window.location.search}${window.location.hash}`
    );
    const nextRelativeUrl = (
        `${window.location.pathname}${nextSearch}${window.location.hash}`
    );
    if (nextRelativeUrl !== currentRelativeUrl) {
        window.history.replaceState(
            window.history.state,
            '',
            nextRelativeUrl
        );
    }
}
"""

_URL_QUERY_SYNCHRONIZER = st.components.v2.component(
    "wspradar_url_query_synchronizer",
    html=_URL_QUERY_SYNCHRONIZER_HTML,
    css=_URL_QUERY_SYNCHRONIZER_CSS,
    js=_URL_QUERY_SYNCHRONIZER_JS,
)


def _normalize_synchronizer_payload(
    entries: Sequence[tuple[str, str]],
    owned_keys: Sequence[str],
) -> tuple[tuple[tuple[str, str], ...], tuple[str, ...]]:
    """Validate the structural boundary between canonical Python state and the browser."""
    if isinstance(owned_keys, (str, bytes)):
        raise ValueError("URL-owned keys must be provided as a sequence.")
    normalized_owned_keys = tuple(owned_keys)
    if any(not isinstance(key, str) or not key for key in normalized_owned_keys):
        raise ValueError("URL-owned keys must be non-empty strings.")
    if len(set(normalized_owned_keys)) != len(normalized_owned_keys):
        raise ValueError("URL-owned keys must be unique.")

    normalized_entries: list[tuple[str, str]] = []
    owned_key_set = set(normalized_owned_keys)
    for entry in entries:
        if not isinstance(entry, (tuple, list)) or len(entry) != 2:
            raise ValueError("Canonical URL entries must contain key/value pairs.")
        key, value = entry
        if not isinstance(key, str) or not key or not isinstance(value, str):
            raise ValueError("Canonical URL entries must contain string keys and values.")
        if key not in owned_key_set:
            raise ValueError(f"Canonical URL entry is not WSPRadar-owned: {key!r}")
        normalized_entries.append((key, value))

    return tuple(normalized_entries), normalized_owned_keys


def render_url_query_synchronizer(
    entries: Sequence[tuple[str, str]],
    *,
    owned_keys: Sequence[str],
    key: str = URL_QUERY_SYNCHRONIZER_KEY,
) -> None:
    """Atomically replace owned query keys while preserving the path, hash, and others."""
    normalized_entries, normalized_owned_keys = _normalize_synchronizer_payload(
        entries,
        owned_keys,
    )
    _URL_QUERY_SYNCHRONIZER(
        data={
            "ownedKeys": list(normalized_owned_keys),
            "entries": [list(entry) for entry in normalized_entries],
        },
        key=key,
        width="stretch",
        height=1,
    )
