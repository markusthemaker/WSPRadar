import re
from pathlib import Path

from ui import css as ui_css


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_top_row_places_configuration_actions_before_view_and_language():
    """Keep setup actions first and presentation selectors last."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")

    assert (
        "col_b1, col_b2, col_b3, col_view, col_lang = st.columns("
        in app_source
    )
    assert (
        'f"input_view_selector_{st.session_state.input_view}"'
        in app_source
    )


def test_classic_action_pairs_remove_control_specific_vertical_offsets(
    monkeypatch,
):
    """Align Classic demo and busy Run controls with their paired actions."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    assert re.search(
        r'key="run_selected_demo",\s+width="stretch"',
        app_source,
    )
    assert re.search(
        r"'<div class=\"wspr-analysis-run-busy-wrapper\">'\s+"
        r"'<button class=\"wspr-analysis-run-busy\"",
        app_source,
    )
    assert (
        '".wspr-analysis-run-busy-wrapper{width:100%;margin:0;padding:0;}"'
        in app_source
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
    selector = '.st-key-run_selected_demo button[kind="secondary"]'
    selector_start = stylesheet.index(selector)
    rule_open = stylesheet.index("{", selector_start)
    rule_close = stylesheet.index("}", rule_open)
    assert "margin-top: 0 !important" in stylesheet[rule_open:rule_close]


def test_result_hierarchy_uses_green_levels_and_responsive_fine_evidence_spine(
    monkeypatch,
):
    """Keep progressive zoom cues visible on desktop without narrowing mobile."""
    rendered_styles = []
    monkeypatch.setattr(
        ui_css.st,
        "markdown",
        lambda body, **_kwargs: rendered_styles.append(body),
    )

    ui_css.apply_custom_css()

    assert len(rendered_styles) == 1
    stylesheet = rendered_styles[0]
    assert ".stMarkdown h2.result-context-title" in stylesheet
    assert ".stMarkdown h3.result-evidence-level-title" in stylesheet
    assert ".stMarkdown h3.result-utility-title" in stylesheet
    assert "color: #39ff14 !important" in stylesheet
    assert ".stMarkdown h4.result-evidence-child-title" in stylesheet
    assert "color: #9be88c !important" in stylesheet

    spine_selector = 'div[class*="st-key-results_evidence_spine_"]::before'
    node_selector = (
        'div[class*="st-key-results_evidence_spine_"] '
        ".result-evidence-level-header::before"
    )
    assert spine_selector in stylesheet
    assert node_selector in stylesheet
    assert "linear-gradient(" in stylesheet
    assert "border-radius: 50%" in stylesheet
    assert ".result-scope-context.result-scope-context-data" in stylesheet
    assert "font-size: 0.88rem !important" in stylesheet
    assert ".result-scope-summary" in stylesheet
    assert "margin-top: 0.18rem !important" in stylesheet
    statistics_selector = ".result-segment-statistics {"
    statistics_start = stylesheet.index(statistics_selector)
    statistics_end = stylesheet.index("}", statistics_start)
    statistics_rule = stylesheet[statistics_start:statistics_end]
    assert "margin: -0.25rem 0 1rem !important" in statistics_rule
    assert "text-align: left !important" in statistics_rule
    assert (
        ".result-segment-statistics\n"
        "        .result-scope-context.result-scope-context-data"
        in stylesheet
    )
    supporting_text_selectors = (
        ".result-evidence-level-subtitle",
        ".result-evidence-child-subtitle",
        ".result-scope-context",
        ".result-evidence-transition",
        ".result-utility-subtitle",
    )
    for selector in supporting_text_selectors:
        rule_start = stylesheet.index(selector)
        rule_end = stylesheet.index("}", rule_start)
        assert "font-size: 0.88rem !important" in stylesheet[
            rule_start:rule_end
        ]

    label_selectors = (
        ".result-context-eyebrow",
        ".result-evidence-path-label",
    )
    for selector in label_selectors:
        rule_start = stylesheet.index(selector)
        rule_end = stylesheet.index("}", rule_start)
        assert "font-size: 0.80rem !important" in stylesheet[
            rule_start:rule_end
        ]

    overlay_selector = 'div[class*="st-key-results_evidence_level_"]::before'
    overlay_rule_start = stylesheet.index(overlay_selector)
    overlay_rule_end = stylesheet.index("}", overlay_rule_start)
    overlay_rule = stylesheet[overlay_rule_start:overlay_rule_end]
    assert "width: 1px;" in overlay_rule
    assert "--result-evidence-spine-width" not in stylesheet

    mobile_start = stylesheet.index("@media (max-width: 768px)")
    mobile_styles = stylesheet[mobile_start:]
    assert (
        'div[class*="st-key-results_evidence_spine_"] {\n'
        "                padding-left: 0 !important;"
    ) in mobile_styles
    assert spine_selector in mobile_styles
    assert node_selector in mobile_styles
    assert (
        'div[class*="st-key-results_evidence_level_"]::before'
        in mobile_styles
    )
    assert "display: none !important" in mobile_styles


def test_outlier_station_insights_action_matches_transition_prompt_green(
    monkeypatch,
):
    """Keep the path-level navigation action green without styling all buttons."""
    rendered_styles = []
    monkeypatch.setattr(
        ui_css.st,
        "markdown",
        lambda body, **_kwargs: rendered_styles.append(body),
    )

    ui_css.apply_custom_css()

    assert len(rendered_styles) == 1
    stylesheet = rendered_styles[0]
    action_selector = (
        'div[class*="st-key-outlier_path_heading_"] '
        'button[kind="tertiary"]'
    )
    selector_start = stylesheet.index(action_selector)
    rule_open = stylesheet.index("{", selector_start)
    rule_close = stylesheet.index("}", rule_open)
    assert "color: #84c97a !important" in stylesheet[rule_open:rule_close]

    hover_selector = f"{action_selector}:hover"
    hover_start = stylesheet.index(hover_selector, rule_close)
    hover_rule_open = stylesheet.index("{", hover_start)
    hover_rule_close = stylesheet.index("}", hover_rule_open)
    assert (
        "color: #a6ff8a !important"
        in stylesheet[hover_rule_open:hover_rule_close]
    )
    action_container_match = re.search(
        r'div\[class\*="st-key-outlier_path_actions_"\]\s+'
        r'div\[data-testid="stButton"\]',
        stylesheet,
    )
    assert action_container_match is not None
    action_container_start = action_container_match.start()
    action_container_rule_open = stylesheet.index(
        "{",
        action_container_start,
    )
    action_container_rule_close = stylesheet.index(
        "}",
        action_container_rule_open,
    )
    action_container_rule = stylesheet[
        action_container_rule_open:action_container_rule_close
    ]
    assert "display: flex !important" in action_container_rule
    assert "justify-content: flex-end !important" in action_container_rule
    assert (
        'div[class*="st-key-outlier_path_actions_"]\n'
        '        div[data-testid="stHorizontalBlock"]'
    ) in stylesheet
    assert "flex-wrap: nowrap !important" in stylesheet
    assert "white-space: nowrap !important" in stylesheet
    assert (
        'div[class*="st-key-d_zoom_selected_window_"]'
        in stylesheet
    )
    assert (
        'div[class*="st-key-outlier_episode_"]\n'
        '        div[data-testid="stVerticalBlock"]'
    ) in stylesheet
    assert "gap: 0.45rem !important" in stylesheet
    assert (
        'div[class*="st-key-outlier_episode_"] h5,\n'
        '        div[class*="st-key-outlier_episode_"] h6 {'
        in stylesheet
    )
    outlier_heading_selector = 'div[class*="st-key-outlier_episode_"] h5,'
    outlier_heading_start = stylesheet.index(outlier_heading_selector)
    outlier_heading_rule_open = stylesheet.index(
        "{",
        outlier_heading_start,
    )
    outlier_heading_rule_close = stylesheet.index(
        "}",
        outlier_heading_rule_open,
    )
    outlier_heading_rule = stylesheet[
        outlier_heading_rule_open:outlier_heading_rule_close
    ]
    assert "padding-bottom: 0 !important" in outlier_heading_rule
    assert "line-height: 1.3 !important" in stylesheet
    caption_container_match = re.search(
        r'div\[class\*="st-key-outlier_episode_"\]\s+'
        r'div\[data-testid="stCaptionContainer"\]\s*\{',
        stylesheet,
    )
    assert caption_container_match is not None
    caption_container_rule_open = stylesheet.index(
        "{",
        caption_container_match.start(),
    )
    caption_container_rule_close = stylesheet.index(
        "}",
        caption_container_rule_open,
    )
    caption_container_rule = stylesheet[
        caption_container_rule_open:caption_container_rule_close
    ]
    assert "margin-bottom: 0 !important" in caption_container_rule


def test_only_outlier_number_input_step_buttons_are_hidden(monkeypatch):
    """Retain direct numeric entry while scoping hidden steppers to outlier gates."""
    rendered_styles = []
    monkeypatch.setattr(
        ui_css.st,
        "markdown",
        lambda body, **_kwargs: rendered_styles.append(body),
    )

    ui_css.apply_custom_css()

    stylesheet = rendered_styles[0]
    hidden_stepper_rules = [
        (selectors, declarations)
        for selectors, declarations in re.findall(
            r"([^{}]*stNumberInputStep(?:Down|Up)[^{}]*)\{([^{}]*)\}",
            stylesheet,
        )
        if "display: none !important" in declarations
    ]
    assert len(hidden_stepper_rules) == 1
    selectors, declarations = hidden_stepper_rules[0]
    assert selectors.count('div[class*="st-key-val_delta_snr_outlier_"]') == 2
    assert 'button[data-testid="stNumberInputStepDown"]' in selectors
    assert 'button[data-testid="stNumberInputStepUp"]' in selectors
    assert "display: none !important" in declarations


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


def test_selectboxes_support_legacy_and_current_streamlit_dom_contracts(
    monkeypatch,
):
    """Keep toolbar select styling stable across BaseWeb and React Aria."""
    rendered_styles = []
    monkeypatch.setattr(
        ui_css.st,
        "markdown",
        lambda body, **_kwargs: rendered_styles.append(body),
    )

    ui_css.apply_custom_css()

    assert len(rendered_styles) == 1
    stylesheet = rendered_styles[0]
    legacy_control = (
        'div[data-testid="stSelectbox"] '
        'div[data-baseweb="select"] > div'
    )
    current_control = (
        'div[data-testid="stSelectbox"] '
        'div[role="group"]:has(> input[role="combobox"])'
    )
    control_start = stylesheet.index(legacy_control)
    control_rule_open = stylesheet.index("{", control_start)
    control_selectors = stylesheet[control_start:control_rule_open]
    assert current_control in control_selectors
    control_rule_close = stylesheet.index("}", control_rule_open)
    control_rule = stylesheet[control_rule_open:control_rule_close]
    assert "background-color: transparent !important" in control_rule
    assert (
        "border: 1px solid rgba(57, 255, 20, 0.35) !important"
        in control_rule
    )
    assert "font-family: 'Space Mono', monospace !important" in control_rule
    assert "min-height: 40px !important" in control_rule

    current_value = (
        'div[data-testid="stSelectbox"] '
        'div[role="group"] > input[role="combobox"]'
    )
    value_start = stylesheet.index(current_value)
    value_rule_open = stylesheet.index("{", value_start)
    value_rule_close = stylesheet.index("}", value_rule_open)
    value_rule = stylesheet[value_rule_open:value_rule_close]
    assert "font-family: 'Space Mono', monospace !important" in value_rule
    assert "font-size: 0.85rem !important" in value_rule
    assert "text-align: center !important" in value_rule
    assert "padding-left: 2.5rem !important" in value_rule
    assert (
        'div[data-testid="stSelectbox"] input[role="combobox"] {'
        not in stylesheet
    )

    current_arrow = (
        'div[data-testid="stSelectbox"] '
        'button[aria-label="Open"] svg'
    )
    arrow_start = stylesheet.index(current_arrow)
    arrow_rule_open = stylesheet.index("{", arrow_start)
    arrow_rule_close = stylesheet.index("}", arrow_rule_open)
    arrow_rule = stylesheet[arrow_rule_open:arrow_rule_close]
    assert "fill: rgba(57, 255, 20, 0.75) !important" in arrow_rule
    assert "color: rgba(57, 255, 20, 0.75) !important" in arrow_rule

    assert (
        'div[data-testid="stSelectboxVirtualDropdown"] [role="listbox"]'
        in stylesheet
    )
    assert (
        'div[data-testid="stSelectboxVirtualDropdown"] [role="option"]'
        in stylesheet
    )
    assert ".st-key-input_view_selector_guided .st-key-input_view" in stylesheet
    assert ".st-key-input_view_selector_classic .st-key-input_view" in stylesheet
    assert 'content: "route"' in stylesheet
    assert 'content: "tune"' in stylesheet
    assert "transform: translateY(0.08rem)" in stylesheet
    assert (
        'div[data-testid="stSelectbox"] '
        'div[role="group"]:has(> input[role="combobox"]:disabled)'
        in stylesheet
    )
