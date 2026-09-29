"""Run-time Reference lookup and explicit site decisions in the input flow."""

from ui.analysis_submission_state import begin_main_analysis_submission
from ui.reference_location_state import (
    current_location_resolution, location_request_signature,
    select_reference_location, store_location_discovery,
)


_TEXT = {
    "en": {
        "loading": "Finding reported Target and Reference locations…",
        "failure": "The location lookup could not complete. Your callsigns have not been classified as invalid. Try again or adjust the measurement window.",
        "no_reference": "No valid Reference location was found for this callsign, direction, band and time window. Check those settings or choose another measurement window.",
        "target_mismatch": "The database has no eligible Target reports matching your entered Target QTH. Check the Target callsign, QTH and measurement window. The analysis origin has not been changed.",
        "target_locations": "Reported Target locations: {locations}",
        "choice_title": "Choose the Reference location",
        "choice": "The Reference has reports from more than one Grid-4 during your selected period. Choose the location you intend to compare. Reports from other grids will be excluded. Full reported locator variants are shown; a grid does not confirm one physical site.",
        "select": "Reference location",
        "candidate": "{grid} · {reports} reports · {first} to {last} UTC · reported: {locators}",
        "continue": "Use this location and continue",
        "resolved": "Reference location: {grid} · reported locators: {locators}",
        "invalid": "{count} reports with missing or invalid endpoint locators cannot establish a selectable location.",
        "source": "Location lookup: {source} · {policy}",
    },
    "de": {
        "loading": "Gemeldete Target- und Referenzstandorte werden gesucht…",
        "failure": "Die Standortsuche konnte nicht abgeschlossen werden. Deine Rufzeichen wurden nicht als ungültig eingestuft. Versuche es erneut oder passe den Messzeitraum an.",
        "no_reference": "Für dieses Referenz-Rufzeichen, diese Richtung, dieses Band und diesen Zeitraum wurde kein gültiger Standort gefunden. Prüfe die Einstellungen oder wähle einen anderen Messzeitraum.",
        "target_mismatch": "Die Datenbank enthält keine geeigneten Target-Meldungen für das eingegebene Target-QTH. Prüfe Target-Rufzeichen, QTH und Messzeitraum. Der Analyseursprung wurde nicht geändert.",
        "target_locations": "Gemeldete Target-Standorte: {locations}",
        "choice_title": "Referenzstandort wählen",
        "choice": "Für die Referenz liegen im gewählten Zeitraum Meldungen aus mehreren Grid-4-Feldern vor. Wähle den Standort, den du vergleichen möchtest. Meldungen aus anderen Feldern werden ausgeschlossen. Die vollständig gemeldeten Locatorvarianten werden angezeigt; ein Feld bestätigt keinen einzelnen physischen Standort.",
        "select": "Referenzstandort",
        "candidate": "{grid} · {reports} Meldungen · {first} bis {last} UTC · gemeldet: {locators}",
        "continue": "Diesen Standort verwenden und fortfahren",
        "resolved": "Referenzstandort: {grid} · gemeldete Locator: {locators}",
        "invalid": "{count} Meldungen mit fehlendem oder ungültigem Endpunkt-Locator können keinen auswählbaren Standort bestimmen.",
        "source": "Standortsuche: {source} · {policy}",
    },
}


def _continue_selected(state, selection_key):
    selected = state.get(selection_key)
    if selected:
        select_reference_location(state, selected)
        begin_main_analysis_submission(state)


def resolve_reference_before_analysis(state, start_utc, end_utc, *, request_lookup=False):
    """Return readiness; pending choices hold neither analysis nor provider slots."""
    import streamlit as st
    from core.input_validation import normalize_ascii_upper

    if state.get("val_comp_mode") != "reference_station":
        return True
    text = _TEXT.get(state.get("lang", "en"), _TEXT["en"])
    resolution = current_location_resolution(state, start_utc, end_utc)
    target_grid = normalize_ascii_upper(state.get("val_qth"))[:4]
    if request_lookup and resolution is not None and (
        not resolution["reference_locations"]
        or target_grid not in {item["grid"] for item in resolution["target_locations"]}
    ):
        # A deliberate retry can recover after new archive reports arrive.
        state.pop("_reference_location_resolution", None)
        state["val_ref_qth"] = ""
        resolution = None
    if resolution is None and state.get("_reference_location_resolution"):
        state.pop("_reference_location_resolution", None)
        state["val_ref_qth"] = ""
    selected_grid = normalize_ascii_upper(state.get("val_ref_qth"))
    # Saved resolved configurations retain their declared scientific selection.
    if resolution is None and selected_grid:
        return True
    if resolution is None and not selected_grid:
        if not request_lookup:
            return False
        from core.reference_location import LocationDiscoveryError, discover_reference_locations
        try:
            with st.spinner(text["loading"]):
                discovery = discover_reference_locations(
                    direction=state.get("val_analysis_direction"),
                    target_callsign=state.get("val_callsign"), target_qth=state.get("val_qth"),
                    reference_callsign=state.get("val_ref_callsign"), band=state.get("val_band"),
                    start_utc=start_utc, end_utc=end_utc,
                    exclude_special_callsigns=state.get("val_exclude_special_callsigns", False),
                )
            resolution = store_location_discovery(state, discovery, location_request_signature(state, start_utc, end_utc))
        except LocationDiscoveryError as exc:
            st.error(text["failure"])
            st.caption(str(exc))
            return False
    if resolution is not None:
        st.caption(text["source"].format(source=resolution["database_source"], policy=resolution["decode_filter_mode"]))
        if resolution.get("invalid_reports"):
            st.warning(text["invalid"].format(count=resolution["invalid_reports"]))
        if target_grid not in {item["grid"] for item in resolution["target_locations"]}:
            st.error(text["target_mismatch"])
            if resolution["target_locations"]:
                st.caption(text["target_locations"].format(locations=", ".join(item["grid"] for item in resolution["target_locations"])))
            return False
        candidates = resolution["reference_locations"]
        if not candidates:
            st.warning(text["no_reference"])
            return False
        if len(candidates) == 1 and not resolution.get("selected_grid"):
            select_reference_location(state, candidates[0]["grid"])
            resolution = current_location_resolution(state, start_utc, end_utc)
        selected_grid = resolution.get("selected_grid")
        if not selected_grid:
            st.info(text["choice"])
            candidate_by_grid = {item["grid"]: item for item in candidates}

            def format_candidate(grid):
                item = candidate_by_grid[grid]
                return text["candidate"].format(
                    grid=grid, reports=item["reports"], locators=", ".join(item["locators"]),
                    first=item["first_utc"][:16].replace("T", " "),
                    last=item["last_utc"][:16].replace("T", " "),
                )

            selection_key = "_reference_location_choice_" + resolution["signature"][:16]
            choice = st.selectbox(text["select"], list(candidate_by_grid), index=None,
                                  format_func=format_candidate, key=selection_key)
            st.button(text["continue"], key="reference_location_continue", disabled=choice is None,
                      on_click=_continue_selected, args=(state, selection_key))
            return False
        item = next(item for item in candidates if item["grid"] == selected_grid)
        st.caption(text["resolved"].format(grid=selected_grid, locators=", ".join(item["locators"])))
    return True
