"""Build presentation-only contexts from Streamlit UI state."""

from core.presentation_context import PresentationContext
from i18n import T


def build_presentation_context_from_session_state(session_state, *, theme="dark"):
    """Capture localized labels and rendering choices without scientific values."""
    language = session_state.get("lang", "en")
    labels = T.get(language, T["en"])
    solar_value = str(session_state.get("val_solar", labels.get("opt_solar_all", "All")))
    return PresentationContext(
        language=language,
        labels=labels,
        theme=theme,
        solar_label=solar_value.split(" ")[0],
    )
