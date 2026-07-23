import re
from pathlib import Path

from ui import css as ui_css


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_guided_workflow_actions_share_key_scoped_green_emphasis(monkeypatch):
    """Emphasize Guided actions while leaving the launcher secondary."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    assert re.search(
        r'key="run_analysis_button",\s+type="primary"',
        app_source,
    )
    assert re.search(
        r'key="load_demo_launcher",\s+type="secondary"',
        app_source,
    )
    assert app_source.count('key="load_selected_demo_configuration"') == 2
    assert 'key="reset_configuration"' in app_source
    assert "nth-child(5)" not in app_source
    assert ".st-key-reset_configuration button" in app_source
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
    glow_selectors = (
        ".st-key-load_selected_demo_configuration "
        'button[kind="primary"]:not(:disabled)',
        ".st-key-guided_demo_walkthrough "
        'button[kind="primary"]:not(:disabled)',
        ".st-key-guided_demo_skip_to_review "
        'button[kind="primary"]:not(:disabled)',
        'div[class*="st-key-guided_continue_"] '
        'button[kind="primary"]:not(:disabled)',
        ".st-key-run_analysis_button "
        'button[kind="primary"]:not(:disabled)',
    )
    selector_start = stylesheet.index(glow_selectors[0])
    rule_open = stylesheet.index("{", selector_start)
    selector_group = stylesheet[selector_start:rule_open]
    assert all(selector in selector_group for selector in glow_selectors)
    assert ".st-key-load_demo_launcher" not in stylesheet
    assert (
        'div[data-testid="stHorizontalBlock"] > div:nth-child(2)'
        not in selector_group
    )

    rule_close = stylesheet.index("}", rule_open)
    rule_body = stylesheet[rule_open:rule_close]
    assert "border-color: #39ff14 !important" in rule_body
    assert "box-shadow: 0 0 3px rgba(57, 255, 20, 0.65) !important" in rule_body
    assert (
        "filter: drop-shadow(0 0 3px rgba(57, 255, 20, 0.45)) !important"
        in rule_body
    )

    hover_selectors = tuple(f"{selector}:hover" for selector in glow_selectors)
    hover_start = stylesheet.index(hover_selectors[0], rule_close)
    hover_rule_open = stylesheet.index("{", hover_start)
    hover_selector_group = stylesheet[hover_start:hover_rule_open]
    assert all(
        selector in hover_selector_group for selector in hover_selectors
    )
    hover_rule_close = stylesheet.index("}", hover_rule_open)
    hover_rule_body = stylesheet[hover_rule_open:hover_rule_close]
    assert "border-color: #39ff14 !important" in hover_rule_body
    assert (
        "box-shadow: 0 0 5px rgba(57, 255, 20, 0.75) !important"
        in hover_rule_body
    )


def test_guided_demo_info_matches_caption_size_without_overriding_blue(
    monkeypatch,
):
    """Match caption typography while retaining Streamlit's information color."""
    renderer_source = (
        REPOSITORY_ROOT / "ui" / "guided_inputs" / "renderer.py"
    ).read_text(encoding="utf-8")
    assert re.search(
        r'with st\.container\(key="guided_demo_context"\):[\s\S]+'
        r'st\.info\(messages\["demo_preset"\]\)',
        renderer_source,
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
    info_selector = (
        '.st-key-guided_demo_context div[data-testid="stAlert"] p'
    )
    selector_start = stylesheet.index(info_selector)
    rule_open = stylesheet.index("{", selector_start)
    rule_close = stylesheet.index("}", rule_open)
    rule_body = stylesheet[rule_open:rule_close]
    assert "font-size: 0.875rem !important" in rule_body
    assert "line-height: 1.55 !important" in rule_body
    assert "color:" not in rule_body


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
