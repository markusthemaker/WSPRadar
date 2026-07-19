import re
from pathlib import Path

from ui import css as ui_css


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_run_analysis_action_shares_enabled_green_emphasis(monkeypatch):
    """The enabled Run action must share the existing highlighted-action rule."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    assert re.search(
        r'key="run_analysis_button",\s+type="primary"',
        app_source,
    )
    assert 'class="wspr-analysis-run-busy"' in app_source

    rendered_styles = []
    monkeypatch.setattr(
        ui_css.st,
        "markdown",
        lambda body, **_kwargs: rendered_styles.append(body),
    )

    ui_css.apply_custom_css()

    assert len(rendered_styles) == 1
    stylesheet = rendered_styles[0]
    run_selector = (
        '.st-key-run_analysis_button button[kind="primary"]:not(:disabled)'
    )
    selector_start = stylesheet.index(run_selector)
    rule_open = stylesheet.index("{", selector_start)
    selector_group = stylesheet[selector_start:rule_open]
    assert (
        'div[data-testid="stHorizontalBlock"] > div:nth-child(2) '
        'div.stButton > button[kind="secondary"]'
        in selector_group
    )

    rule_close = stylesheet.index("}", rule_open)
    rule_body = stylesheet[rule_open:rule_close]
    assert "border-color: #39ff14 !important" in rule_body
    assert "box-shadow: 0 0 3px rgba(57, 255, 20, 0.65) !important" in rule_body
    assert (
        "filter: drop-shadow(0 0 3px rgba(57, 255, 20, 0.45)) !important"
        in rule_body
    )


def test_profile_descriptions_use_white_text_in_scoped_containers(monkeypatch):
    """Demo and loaded-metadata captions must share opaque white styling."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    assert re.search(
        r'with st\.container\(key="demo_description"\):\s+'
        r'st\.caption\(prepare_demo_description_markdown\(demo_description\)\)',
        app_source,
    )

    rendered_styles = []
    monkeypatch.setattr(
        ui_css.st,
        "markdown",
        lambda body, **_kwargs: rendered_styles.append(body),
    )

    ui_css.apply_custom_css()

    assert len(rendered_styles) == 1
    stylesheet = rendered_styles[0]
    caption_selector = (
        '.st-key-demo_description div[data-testid="stCaptionContainer"] p'
    )
    selector_start = stylesheet.index(caption_selector)
    rule_open = stylesheet.index("{", selector_start)
    selector_group = stylesheet[selector_start:rule_open]
    assert (
        ".st-key-loaded_config_metadata_description "
        'div[data-testid="stCaptionContainer"] p'
        in selector_group
    )
    rule_close = stylesheet.index("}", rule_open)
    assert "color: #ffffff !important" in stylesheet[rule_open:rule_close]

    container_selector = (
        '.st-key-demo_description div[data-testid="stCaptionContainer"]'
    )
    selector_start = stylesheet.index(container_selector, rule_close + 1)
    rule_open = stylesheet.index("{", selector_start)
    selector_group = stylesheet[selector_start:rule_open]
    assert (
        ".st-key-loaded_config_metadata_description "
        'div[data-testid="stCaptionContainer"]'
        in selector_group
    )
    rule_close = stylesheet.index("}", rule_open)
    assert "opacity: 1 !important" in stylesheet[rule_open:rule_close]
