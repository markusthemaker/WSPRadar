"""Build presentation-only contexts from Streamlit UI state."""

from core.presentation_context import PresentationContext
from i18n import T
from ui.config_io import SOLAR_KEYS


def build_presentation_context_from_session_state(session_state, *, theme="dark"):
    """Capture localized labels and rendering choices without scientific values."""
    language = session_state.get("lang", "en")
    labels = T.get(language, T["en"])
    solar_state = str(session_state.get("val_solar", "all"))
    solar_value = labels.get(SOLAR_KEYS.get(solar_state, "opt_solar_all"), "All")
    return PresentationContext(
        language=language,
        labels=labels,
        theme=theme,
        solar_label=solar_value.split(" ")[0],
    )
