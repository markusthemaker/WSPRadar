"""Build the public WSPRadar website from its reviewed content bundle.

No application checkout, runtime import, database query, or credentials are
required. Imported content is verified before any build output is written.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from string import Template
from urllib.parse import unquote, urlsplit

import markdown

if __package__:
    from .external_links import check_external_links, collect_external_links
    from .landing_page import render_landing
    from .demo_walkthrough import demo_launch_url, heading_and_body, read_sections, render_demo, resource_files, safe_path
else:
    from external_links import check_external_links, collect_external_links
    from landing_page import render_landing
    from demo_walkthrough import demo_launch_url, heading_and_body, read_sections, render_demo, resource_files, safe_path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "generated"
SITE = ROOT / "site"
OUTPUT = ROOT / "dist"
APP_URL = "https://wspradar.streamlit.app/"
# Community Cloud serves app-owned files through its hosted application route.
APP_STATIC_URL = APP_URL + "~/+/app/static/"
SITE_URL = "https://wspradar.org"
COMMUNITY_URL = "https://github.com/markusthemaker/WSPRadar/discussions"
HELP_URL = COMMUNITY_URL + "/new?category=ask-a-question"
EXPERIMENTS_URL = COMMUNITY_URL + "/new?category=discuss-your-experiments"
IDEAS_URL = COMMUNITY_URL + "/new?category=ideas-and-feature-requests"
REPORT_URL = COMMUNITY_URL + "/new?category=report-a-bug-or-concern"
# Match the border-box site shell and its horizontal padding in site/site.css.
HEADER_IMAGE_SIZES = "(max-width:580px) calc(100vw - 34px), (max-width:1280px) calc(100vw - 48px), 1232px"
LANGUAGE_NAMES = {"en": "English", "de": "Deutsch"}

COPY = {
    "en": {
        "home": "Overview", "why": "Why WSPRadar", "docs": "Documentation", "demos": "Demo walkthrough",
        "community": "Community", "bug": "Report a Bug", "nav_demos": "Demo Walkthrough",
        "open": "Open WSPRadar App", "skip": "Skip to content", "menu": "Menu", "language": "Language", "change_language": "Change language",
        "eyebrow": """A practical route to assess your station with WSPR evidence""",
        "hero": """Start with your question. Set up your station. Learn from your WSPR data.""",
        "intro": """Does a setup change or a new antenna make a difference? Where is your station heard, and whom do you hear? Explore a worked Benchmark example to compare against a reference antenna or station.""",
        "hero_note": "For receiving and transmitting. Read the result in the context of your station, the radio paths, and the experiment.",
        "start": "Explore a worked example", "follow": "Follow the evidence",
        "choose_title": "Choose the Question",
        "choose_body": """Choose RX or TX, then Benchmark to compare against a reference antenna or station, or Performance to explore your station without a reference.""",
        "choose_link": "Choose your analysis",
        "experiment_title": "Perform the Experiment",
        "experiment_body": """Set up your station and WSPR software, then receive or transmit to generate the WSPR observations your question needs.""",
        "experiment_link": "Prepare your station",
        "run_title": "Run WSPRadar App",
        "run_body": """Select your station, band, and experiment period. Run the analysis, explore your WSPR data, and interpret the evidence.""",
        "benchmark": "Compare a station or setup",
        "benchmark_body": "Use Benchmark to examine paired signal differences, Decode Outcomes, and the evidence behind a comparison.",
        "performance": "Understand station performance",
        "performance_body": "Use Performance to examine reach, Decode Rate, and successful Target SNR across direction, distance, and time.",
        "demo_feature": "Explore the experiments behind the app",
        "demo_context": """These demos draw on published WSPR studies, comparing reported findings with WSPRadar analyses of the available observations. They demonstrate station comparisons, calibration, Performance analysis, and tracing results back to individual reports, while explaining differences in methods, presentation, and data coverage.""",
        "demo_summary": "Griffiths: RX comparison, day/night reversal, and Performance · Vanhamel: calibration and antenna rotation · Zander: TX comparison · Milazzo: historical reconstruction.",
        "browse_demos": "Browse all demo walkthroughs", "all_docs": "The complete documentation",
        "full_manual": "Read the complete manual",
        "manual_start_title": "Start here: Why WSPRadar?",
        "manual_start_body": """Did your station change really help—or did conditions change? Explore what WSPR observations can reveal, which questions WSPRadar can answer, and where the limits lie.""",
        "manual_start_link": "Read Why WSPRadar?",
        "connect": "Connect with the community", "connect_body": "Ask a question, discuss an experiment, or share what you learned from a result.",
        "improve": "Help improve WSPRadar", "improve_body": "Report a possible problem, propose a feature, or raise a scientific concern.",
        "experiment": "Experimental station analysis", "disclaimer": "Experimental Use & Disclaimer",
        "content_version": "Documentation for", "demo_title": "One experiment at a time. Every demo explained.",
        "demo_intro": "Explore the question, reproduce the setup, follow the observations, and understand the limits of each result.",
        "filter": "Find a demo by name, station, or topic", "walkthrough": "Explore walkthrough",
        "no_figures": "Dedicated figures for this walkthrough are deferred. The maintained demo description and configuration remain available below.",
        "download_config": "Download demo configuration",
        "run_demo": "Run in WSPRadar App",
        "original_description": "Experiment and interpretation", "walkthrough_steps": "Work through the result",
        "figures": "Publication and reconstruction figures", "screenshots": "Inside the running app",
        "contents": "On this page", "full_size": "Open full-size image", "english_capture": "Captured from the English app interface.",
        "guides_title": "Understand your results", "guides_intro": "Follow a pattern from its geographic context to the observations behind it. Read every result with its supporting evidence and the conditions of the experiment.",
        "read_manual": "Read the full explanation", "related_demo": "Explore a worked example",
        "community_title": "Get help, share experiments, and improve WSPRadar",
        "community_intro": """Use GitHub Discussions to discuss experiments, ask questions, and keep useful findings connected to their resolution.""",
        "participation": """Hosted on GitHub. A free GitHub account is required to post. No programming knowledge is needed. Please write all posts and replies in English. Posts are public; support is provided as time permits.""",
        "share_experiment": "Share an experiment",
        "questions": "Ask a question", "questions_body": """Discuss setup choices, using WSPRadar, and interpretations of a result. Please check the <a href="{manual_url}">manual</a> first. If your question is unanswered or something is unclear, ask here. Share your setup and what you have already tried.""",
        "experiments": "Discuss your experiments", "experiments_body": """Discuss experiment setups, share your findings, and compare interpretations. Explain what you wanted to learn, how you ran the experiment, and what the results suggest. Add relevant settings or screenshots to help others follow.""",
        "ask": "Ask a question", "feature": "Ideas and feature requests", "feature_body": """Suggest improvements or share an early idea for WSPRadar. Describe the question or workflow a new capability would support, who would benefit, and how it would help. A detailed technical solution is not required.""",
        "report_category": "Report a bug or concern", "scientific_body": """For a scientific or methodological concern, identify a specific assumption, calculation, interpretation, or claim that needs review.""",
        "report_summary": """Report unexpected behavior or concerns about WSPRadar’s methods or results. Describe what you tried, what happened, and what you expected. Include steps or evidence if available. You do not need a confirmed diagnosis.""",
        "bug_intro": """Describe what you tried, what you expected, and what happened. If you know how to reproduce the problem, include the smallest set of steps. You do not need a confirmed diagnosis.""",
        "report_body": """Start with what you have. For analysis-related reports, the app version, analysis mode, exact station identities, band, UTC interval, settings, and a configuration or screenshot can help; these details are optional when you first post. Review attachments before posting: reports are public.""",
        "report_followup": """Post in Report a bug or concern. The maintainer will request additional information if needed, track engineering work in an Issue when useful, and return the outcome to your discussion.""",
        "continue": "Start a discussion", "print": "Print / save as PDF using your browser",
        "previous": "Previous", "next": "Next", "manual_intro": "The complete operator and scientific manual, published from the same source used by WSPRadar. Choose a chapter or read the continuous version.",
        "preview": "First website implementation · review preview",
    },
    "de": {
        "home": "Überblick", "why": "Warum WSPRadar", "docs": "Dokumentation", "demos": "Demo-Anleitung",
        "community": "Community", "bug": "Fehler melden", "nav_demos": "Demo-Anleitung",
        "open": "WSPRadar App öffnen", "skip": "Zum Inhalt", "menu": "Menü", "language": "Sprache", "change_language": "Sprache ändern",
        "eyebrow": """Ein praktischer Weg, deine Station anhand von WSPR-Beobachtungen zu beurteilen""",
        "hero": """Beginne mit deiner Frage. Richte deine Station ein. Lerne aus deinen WSPR-Daten.""",
        "intro": """Macht eine Änderung am Aufbau oder eine neue Antenne einen Unterschied? Wo wird deine Station gehört, und wen hörst du? Erkunde ein ausgearbeitetes Benchmark-Beispiel für den Vergleich mit einer Referenzantenne oder Referenzstation.""",
        "hero_note": "Für Empfang und Aussendung. Betrachte das Ergebnis im Zusammenhang mit deiner Station, den Funkwegen und dem Versuchsaufbau.",
        "start": "Ein Beispiel durcharbeiten", "follow": "Der Evidenz folgen",
        "choose_title": "Wähle die Fragestellung",
        "choose_body": """Wähle RX oder TX und anschließend Benchmark für den Vergleich mit einer Referenzantenne oder Referenzstation oder Performance, um deine Station ohne Referenz zu untersuchen.""",
        "choose_link": "Wähle deine Analyse",
        "experiment_title": "Führe das Experiment durch",
        "experiment_body": """Richte deine Station und WSPR-Software ein. Empfange oder sende anschließend, um die WSPR-Beobachtungen für deine Fragestellung zu erzeugen.""",
        "experiment_link": "Bereite deine Station vor",
        "run_title": "Starte die WSPRadar App",
        "run_body": """Wähle deine Station, das Band und den Versuchszeitraum. Starte die Analyse, untersuche deine WSPR-Daten und interpretiere die Beobachtungen.""",
        "benchmark": "Stationen oder Aufbauten vergleichen",
        "benchmark_body": "Untersuche mit Benchmark gepaarte Signalunterschiede, Decode Outcomes und die Beobachtungen, auf denen der Vergleich beruht.",
        "performance": "Das Verhalten deiner Station verstehen",
        "performance_body": "Untersuche mit Performance Reichweite, Decode Rate und erfolgreiches Target-SNR nach Richtung, Entfernung und Zeit.",
        "demo_feature": "Die Experimente hinter der Anwendung erkunden",
        "demo_context": """Diese Demos greifen veröffentlichte WSPR-Studien auf und vergleichen deren Ergebnisse mit WSPRadar-Analysen der verfügbaren Beobachtungen. Sie zeigen Stationsvergleiche, Kalibrierung, Performance-Analysen und die Rückverfolgung von Ergebnissen bis zu einzelnen Empfangsberichten und erläutern dabei Unterschiede in Methoden, Darstellung und Datenabdeckung.""",
        "demo_summary": "Griffiths: RX-Vergleich, Tag-Nacht-Umkehr und Performance · Vanhamel: Kalibrierung und Antennendrehung · Zander: TX-Vergleich · Milazzo: historische Rekonstruktion.",
        "browse_demos": "Alle Demo-Anleitungen ansehen", "all_docs": "Die vollständige Dokumentation",
        "full_manual": "Das vollständige Handbuch lesen",
        "manual_start_title": "Einstieg: Warum WSPRadar?",
        "manual_start_body": """Hat die Änderung an deiner Station wirklich geholfen – oder haben sich die Bedingungen verändert? Erfahre, was WSPR-Beobachtungen zeigen können, welche Fragen WSPRadar beantworten kann und wo die Grenzen liegen.""",
        "manual_start_link": "Lies „Warum WSPRadar?“",
        "connect": "Mit der Community austauschen", "connect_body": "Stelle eine Frage, diskutiere ein Experiment oder teile Erkenntnisse aus einem Ergebnis.",
        "improve": "WSPRadar gemeinsam verbessern", "improve_body": "Melde ein mögliches Problem, schlage eine Funktion vor oder benenne ein wissenschaftliches Problem.",
        "experiment": "Experimentelle Stationsanalyse", "disclaimer": "Experimentelle Nutzung und Haftungsausschluss",
        "content_version": "Dokumentation für", "demo_title": "Ein Experiment nach dem anderen. Jede Demo erklärt.",
        "demo_intro": "Verstehe die Fragestellung, stelle den Aufbau nach, folge den Beobachtungen und erkenne die Grenzen des jeweiligen Ergebnisses.",
        "filter": "Demo nach Name, Station oder Thema suchen", "walkthrough": "Anleitung ansehen",
        "no_figures": "Eigene Abbildungen für diese Anleitung folgen später. Die gepflegte Demo-Beschreibung und Konfiguration stehen unten bereit.",
        "download_config": "Demo-Konfiguration herunterladen",
        "run_demo": "In WSPRadar App starten",
        "original_description": "Experiment und Interpretation", "walkthrough_steps": "Das Ergebnis Schritt für Schritt untersuchen",
        "figures": "Abbildungen aus Veröffentlichung und Rekonstruktion", "screenshots": "Ansichten der laufenden Anwendung",
        "contents": "Auf dieser Seite", "full_size": "Bild in voller Größe öffnen", "english_capture": "Aufnahme der englischen Benutzeroberfläche.",
        "guides_title": "Deine Ergebnisse verstehen", "guides_intro": "Verfolge ein Muster von seinem geografischen Zusammenhang bis zu den zugrunde liegenden Beobachtungen. Betrachte jedes Ergebnis zusammen mit seiner Evidenz und den Bedingungen des Experiments.",
        "read_manual": "Die vollständige Erklärung lesen", "related_demo": "Ein Beispiel durcharbeiten",
        "community_title": "Hilfe erhalten, Experimente teilen und WSPRadar verbessern",
        "community_intro": """Nutze GitHub Discussions, um Experimente zu diskutieren, Fragen zu stellen und Erkenntnisse mit ihrer Klärung zu verbinden.""",
        "participation": """Die Community ist auf GitHub. Zum Schreiben ist ein kostenloses GitHub-Konto erforderlich. Programmierkenntnisse sind nicht nötig. Bitte verfasse alle Beiträge und Antworten auf Englisch. Beiträge sind öffentlich; Unterstützung erfolgt, soweit es die Zeit erlaubt.""",
        "share_experiment": "Ein Experiment vorstellen",
        "questions": "Eine Frage stellen", "questions_body": """Diskutiere Versuchsaufbauten, die Nutzung von WSPRadar und die Interpretation von Ergebnissen. Sieh bitte zuerst im <a href="{manual_url}">Handbuch</a> nach. Wenn deine Frage unbeantwortet bleibt oder etwas unklar ist, stelle deine Frage hier. Beschreibe deinen Aufbau und was du bereits versucht hast.""",
        "experiments": "Experimente diskutieren", "experiments_body": """Diskutiere Versuchsaufbauten, teile deine Erkenntnisse und vergleiche Interpretationen. Beschreibe, was du herausfinden wolltest, wie du das Experiment durchgeführt hast und was die Ergebnisse nahelegen. Ergänze passende Einstellungen oder Screenshots, damit andere dir folgen können.""",
        "ask": "Eine Frage stellen", "feature": "Ideen und Funktionswünsche", "feature_body": """Schlage Verbesserungen vor oder teile eine erste Idee für WSPRadar. Beschreibe die Fragestellung oder den Arbeitsablauf, den eine neue Funktion unterstützen würde, wem sie hilft und welchen Nutzen sie hat. Eine detaillierte technische Lösung ist nicht erforderlich.""",
        "report_category": "Fehler oder Bedenken melden", "scientific_body": """Benenne bei wissenschaftlichen oder methodischen Bedenken eine konkrete Annahme, Berechnung, Interpretation oder Aussage, die überprüft werden sollte.""",
        "report_summary": """Melde unerwartetes Verhalten oder Bedenken zu WSPRadars Methoden oder Ergebnissen. Beschreibe, was du versucht hast, was passiert ist und was du erwartet hast. Ergänze Schritte oder Belege, falls vorhanden. Du brauchst keine bestätigte Diagnose.""",
        "bug_intro": """Beschreibe, was du versucht und erwartet hast und was tatsächlich passiert ist. Falls du weißt, wie sich das Problem reproduzieren lässt, nenne die dafür nötigen Schritte. Du brauchst keine bestätigte Diagnose.""",
        "report_body": """Beginne mit den Informationen, die du hast. Bei analysebezogenen Meldungen können App-Version, Analysemodus, genaue Stationskennungen, Band, UTC-Zeitraum, Einstellungen sowie eine Konfiguration oder ein Screenshot helfen; diese Angaben sind beim ersten Beitrag optional. Prüfe Anhänge vor dem Absenden: Meldungen sind öffentlich.""",
        "report_followup": """Schreibe unter Report a bug or concern (Fehler oder Bedenken melden). Der Maintainer fragt bei Bedarf nach weiteren Informationen, verfolgt Entwicklungsarbeit bei Bedarf in einem Issue und meldet das Ergebnis in deiner Diskussion zurück.""",
        "continue": "Eine Diskussion beginnen", "print": "Über den Browser drucken oder als PDF speichern",
        "previous": "Zurück", "next": "Weiter", "manual_intro": "Das vollständige Bedien- und wissenschaftliche Handbuch aus derselben Quelle wie in WSPRadar. Wähle ein Kapitel oder lies die zusammenhängende Fassung.",
        "preview": "Erste Website-Umsetzung · Vorschau zur Prüfung",
    },
}


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    level: int
    text: str
    anchors: tuple[str, ...]


def json_read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_bundle(directory: Path) -> dict:
    manifest = json_read(directory / "manifest.json")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unsupported public-content manifest version")
    declared = manifest.get("files")
    if not isinstance(declared, dict) or not declared:
        raise ValueError("Manifest contains no file inventory")
    for name, expected in declared.items():
        relative = PurePosixPath(name)
        if not isinstance(name, str) or relative.is_absolute() or relative.as_posix() != name or any(part in (".", "..") for part in relative.parts) or ":" in name:
            raise ValueError(f"Unsafe manifest path: {name}")
        candidate = (directory / name).resolve()
        if not candidate.is_relative_to(directory.resolve()) or "\\" in name:
            raise ValueError(f"Unsafe manifest path: {name}")
        data = candidate.read_bytes()
        if len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise ValueError(f"Imported content is stale or modified: {name}")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if actual != set(declared) | {"manifest.json"}:
        raise ValueError("Imported content inventory differs from manifest")
    return manifest


def split_manual(text: str) -> list[Section]:
    """Partition the entire source; no sentence or compatibility anchor is dropped."""
    lines = text.splitlines(keepends=True)
    starts = []
    heading_data = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if not match:
            continue
        start = index
        while start and (not lines[start - 1].strip() or re.fullmatch(r'<a id="[^"]+"></a>\s*', lines[start - 1])):
            start -= 1
        starts.append(start)
        heading_data.append((len(match[1]), match[2], index))
    if not starts:
        raise ValueError("Manual has no recognized section headings")
    starts[0] = 0
    sections = []
    used_keys = set()
    for number, start in enumerate(starts):
        end = starts[number + 1] if number + 1 < len(starts) else len(lines)
        source = "".join(lines[start:end])
        anchors = tuple(re.findall(r'<a\s+id="([^"]+)"', source))
        level, title, heading_index = heading_data[number]
        leading = "".join(lines[start:heading_index])
        leading_ids = re.findall(r'<a\s+id="([^"]+)"', leading)
        key = leading_ids[0] if leading_ids else f"section-{number}"
        if key in used_keys:
            raise ValueError(f"Duplicate manual section key: {key}")
        used_keys.add(key)
        sections.append(Section(key, title, level, source, anchors))
    if "".join(section.text for section in sections) != text:
        raise ValueError("Manual partition changed the source text")
    return sections


def route(lang: str, suffix: str = "") -> str:
    return f"/{lang}/" + suffix


def chapter_url(lang: str, key: str) -> str:
    return route(lang, f"documentation/{key}/")


def render_markdown(text: str, lang: str, anchor_map: dict[str, str], *, continuous=False) -> str:
    expressions = {}
    def math_replace(match):
        expression = match[2]
        delimiter = r"\[" if match[1] == "$$" else r"\("
        ending = r"\]" if match[1] == "$$" else r"\)"
        token = 'WSPRADARMATH' + hashlib.sha256(match[0].encode()).hexdigest() + 'END'
        expressions[token] = '<span class="math">' + delimiter + escape(expression) + ending + '</span>'
        return token

    text = re.sub(r"(\${1,2})(.+?)\1", math_replace, text, flags=re.DOTALL)
    rendered = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    for token, expression in expressions.items():
        rendered = rendered.replace(token, expression)
    rendered = re.sub(r'<a([^>]*?)href="app/static/([^"<>]+)"', lambda m: f'<a{m[1]}href="{APP_STATIC_URL}{m[2]}"', rendered)
    if not continuous:
        rendered = re.sub(r'href="#([^"]+)"', lambda m: f'href="{anchor_map.get(m[1], route(lang, "documentation/full/"))}#{m[1]}"', rendered)
    rendered = rendered.replace("<table>", '<div class="table-scroll" role="region" aria-label="' + ("Scrollable table" if lang == "en" else "Scrollbare Tabelle") + '" tabindex="0"><table>')
    return rendered.replace("</table>", "</table></div>")


class _PDFLinkPolicyParser(HTMLParser):
    """Locate real anchors while leaving their surrounding source untouched."""

    CDATA_CONTENT_ELEMENTS = (
        "script", "style", "textarea", "title", "xmp", "iframe", "noembed",
        "noframes", "plaintext",
    )
    _attribute = re.compile(
        r"""(?P<name>[^\s=/>]+)(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?"""
    )

    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.line_offsets = [0] + [match.end() for match in re.finditer("\n", source)]
        self.replacements: list[tuple[int, int, str]] = []

    def handle_starttag(self, tag, attrs):
        self._handle_anchor(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        self._handle_anchor(tag, attrs, self_closing=True)

    def _handle_anchor(self, tag, attrs, *, self_closing):
        if tag != "a":
            return
        # The first href is the effective attribute when malformed HTML repeats it.
        href = next((value for name, value in attrs if name == "href"), None)
        if not href:
            return
        try:
            is_pdf = unquote(urlsplit(href).path).casefold().endswith(".pdf")
        except ValueError:
            return
        if not is_pdf:
            return

        tokens = [token for name, value in attrs if name == "rel"
                  for token in (value or "").split()]
        for required in ("noopener", "noreferrer"):
            if required not in {token.casefold() for token in tokens}:
                tokens.append(required)
        values = {"target": "_blank", "rel": " ".join(tokens)}
        raw = self.get_starttag_text()
        tag_end = re.match(r"<a\b", raw, re.IGNORECASE).end()
        edits = []
        found = set()
        for match in self._attribute.finditer(raw, tag_end):
            name = match["name"]
            key = name.casefold()
            if key == "download":
                # A download hint can override opening a local PDF in a new tab.
                edits.append((match.start(), match.end(), ""))
            elif key in values:
                found.add(key)
                edits.append((match.start(), match.end(),
                              name + '="' + escape(values[key], quote=True) + '"'))
        missing = ''.join(' ' + key + '="' + escape(value, quote=True) + '"'
                          for key, value in values.items() if key not in found)
        if missing:
            close_at = len(raw) - (2 if self_closing else 1)
            edits.append((close_at, close_at, missing))
        updated = raw
        for start, end, replacement in sorted(edits, reverse=True):
            updated = updated[:start] + replacement + updated[end:]
        if updated != raw:
            line, column = self.getpos()
            start = self.line_offsets[line - 1] + column
            self.replacements.append((start, start + len(raw), updated))


def open_pdf_links_in_new_tabs(html: str) -> str:
    """Apply the shared PDF policy without reserializing unrelated markup."""
    parser = _PDFLinkPolicyParser(html)
    parser.feed(html)
    parser.close()
    for start, end, replacement in reversed(parser.replacements):
        html = html[:start] + replacement + html[end:]
    return html


class _PrintImageParser(HTMLParser):
    """Promote real image loading hints without rewriting content or sources."""

    CDATA_CONTENT_ELEMENTS = _PDFLinkPolicyParser.CDATA_CONTENT_ELEMENTS

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.line_offsets = [0] + [match.end() for match in re.finditer("\n", source)]
        self.replacements = []

    def handle_starttag(self, tag, attrs):
        if tag != "img" or not any(name == "loading" and (value or "").lower() == "lazy" for name, value in attrs):
            return
        raw = self.get_starttag_text()
        tag_end = re.match(r"<img\b", raw, re.IGNORECASE).end()
        updated = raw
        for match in reversed(list(_PDFLinkPolicyParser._attribute.finditer(raw, tag_end))):
            if match["name"].lower() == "loading":
                updated = updated[:match.start()] + 'loading="eager"' + updated[match.end():]
        line, column = self.getpos()
        start = self.line_offsets[line - 1] + column
        self.replacements.append((start, start + len(raw), updated))

    handle_startendtag = handle_starttag


def load_print_images_with_page(html: str) -> str:
    """Native print can snapshot before lazy-image requests from beforeprint finish."""
    parser = _PrintImageParser(html)
    parser.feed(html)
    parser.close()
    for start, end, replacement in reversed(parser.replacements):
        html = html[:start] + replacement + html[end:]
    return html


def button(label: str, href: str, *, secondary=False, external=False, download=False) -> str:
    attributes = ' target="_blank" rel="noopener noreferrer"' if external else ""
    if download:
        attributes += " download"
    return f'<a class="button{" secondary" if secondary else ""}" href="{escape(href, quote=True)}"{attributes}>{escape(label)}{" ↗" if external else ""}</a>'


class SiteBuilder:
    def __init__(self, content=CONTENT):
        self.content = Path(content)
        self.manifest = verify_bundle(self.content)
        self.brand = json_read(self.content / "brand.json")
        self.demos = json_read(self.content / "demos.json")
        self.website = json_read(self.content / "website.json")
        self.figures = json_read(self.content / "figures.json")
        self.screenshots = json_read(self.content / "screenshots.json")
        self.manuals = {lang: (self.content / f"manual.{lang}.md").read_text(encoding="utf-8") for lang in COPY}
        self.sections = {lang: split_manual(value) for lang, value in self.manuals.items()}
        self.anchors = {lang: {anchor: chapter_url(lang, s.key) for s in sections for anchor in s.anchors} for lang, sections in self.sections.items()}
        for lang in COPY:
            all_anchors = [anchor for s in self.sections[lang] for anchor in s.anchors]
            if len(all_anchors) != len(set(all_anchors)):
                raise ValueError(f"Duplicate manual anchors in {lang}")
        self.template = Template((SITE / "page.html").read_text(encoding="utf-8"))
        self.landing_css_version = hashlib.sha256((SITE / "landing.css").read_bytes()).hexdigest()[:16]
        self.print_assets_version = hashlib.sha256((SITE / "print.css").read_bytes() + (SITE / "print.js").read_bytes()).hexdigest()[:16]
        self.copy = COPY
        self.landing = json_read(SITE / "landing.json")
        self.landing_assets = json_read(SITE / "assets" / "landing" / "manifest.json")
        self.demo_walkthroughs = json_read(SITE / "demo_walkthroughs.json")
        self.demo_root = SITE / "demos"
        self.pages: dict[str, str] = {}

    def md(self, text, lang, **kwargs):
        return render_markdown(text, lang, self.anchors[lang], **kwargs)

    def language_selector(self, lang: str, suffix: str) -> str:
        """Show the current language and preserve the route for both choices."""
        label = COPY[lang]["change_language"]
        options = []
        for language, name in LANGUAGE_NAMES.items():
            current = ' aria-current="true"' if language == lang else ""
            options.append(
                f'<a class="language-option" href="{route(language, suffix)}" lang="{language}" hreflang="{language}"{current}>'
                f'<span>{name}</span></a>'
            )
        return (
            '<details class="language-selector">'
            f'<summary aria-label="{label}: {LANGUAGE_NAMES[lang]}" title="{label}">'
            '<svg class="language-globe" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.6">'
            '<circle cx="12" cy="12" r="9"></circle><ellipse cx="12" cy="12" rx="4" ry="9"></ellipse><path d="M3 12h18"></path></svg>'
            f'<span class="language-current" lang="{lang}">{lang.upper()}</span>'
            '<span class="language-chevron" aria-hidden="true">⌄</span></summary>'
            f'<div class="language-options" role="group" aria-label="{label}">' + ''.join(options) + '</div></details>'
        )

    def header(self, lang: str, active: str, suffix: str) -> str:
        t = COPY[lang]
        demo_id = suffix.removeprefix("demos/").removesuffix("/") if suffix.startswith("demos/") else ""
        is_demo = demo_id in self.demo_walkthroughs.get("demos", {})
        launch_url = demo_launch_url(self.demo_walkthroughs["demos"][demo_id]) if is_demo else APP_URL
        launch_label = t["run_demo"] if is_demo else t["open"]
        links = []
        for key, path, label in (
            ("home", "", t["home"]),
            ("demos", "demos/", t["nav_demos"]),
            ("docs", "documentation/", t["docs"]),
            ("community", "community/", t["community"]),
        ):
            current = ' aria-current="page"' if key == active else ""
            links.append(f'<a href="{route(lang,path)}"{current}>{label}</a>')
        hero = self.landing_assets["hero"]
        fallback = hero["fallback"]
        candidates = sorted(hero["images"], key=lambda image: image["width"])
        srcset = ", ".join(f'/assets/landing/{image["path"]} {image["width"]}w' for image in candidates)
        print_artwork = candidates[-1]
        print_header_style = escape('--print-header-image:url("/assets/landing/' + print_artwork["path"] + '")', quote=True)
        hero_entry = ''
        hero_actions = ''
        if active == 'home':
            landing = self.landing[lang]
            hero_actions = '<div class="hero-actions">' + button(landing['try_demo'] + ' →', route(lang, '#real-example')) + button(t['open'], APP_URL, secondary=True, external=True) + '</div>'
            hero_entry = ('<section class="hero-entry" aria-labelledby="landing-title">'
                          '<div class="mobile-intro"><h1 id="landing-title">' + escape(landing['headline']) + '</h1><p>' + escape(landing['intro']) + '</p></div>'
                          '<p class="hero-reassurance">' + escape(landing['no_station']) + '</p></section>')
        artwork_class = 'hero-artwork-stage hero-artwork-with-actions' if hero_actions else 'hero-artwork-stage'
        return (
            '<header class="site-header landing-header" style="' + print_header_style + '"><nav class="navigation" aria-label="' + t["menu"] + '">'
            '<a class="nav-brand" href="' + route(lang) + '" aria-label="WSPRadar.org — ' + t['home'] + '"><span>WSPRadar.org</span></a>'
            '<button class="nav-toggle" aria-controls="nav-links" aria-expanded="true">' + t["menu"] + '</button><div class="nav-links" id="nav-links">' + ''.join(links) + '</div>'
            + self.language_selector(lang, suffix) + '<span class="launch">' + button(launch_label, launch_url, external=True) + '</span></nav>'
            '<div class="radar-visual"><div class="' + artwork_class + '"><picture class="radar-artwork" lang="en">'
            '<source type="image/webp" srcset="' + srcset + '" sizes="' + HEADER_IMAGE_SIZES + '" width="' + str(fallback['width']) + '" height="' + str(fallback['height']) + '">'
            '<img lang="' + lang + '" src="/assets/landing/' + fallback['path'] + '" width="' + str(fallback['width']) + '" height="' + str(fallback['height']) + '" alt="' + escape(self.landing[lang]['hero_alt'], quote=True) + '" fetchpriority="high" loading="eager">'
            '</picture>' + hero_actions + '</div>' + hero_entry + '</div></header>'
        )

    def page(self, lang, suffix, title, body, active, *, math=False, root_alias=False, case_study=False):
        t = COPY[lang]
        credit = self.brand['credit_html'][lang]
        release_prefix = 'Release ' + self.brand['app_version'] + ' | '
        developer_credit = credit.removeprefix(release_prefix)
        footer = ('<footer class="site-footer"><div class="footer-main"><span class="footer-wordmark">WSPRadar ' + escape(self.brand['app_version']) + '</span> <span class="footer-tagline">' + self.landing[lang]['footer_tagline'] + '</span> <span class="footer-credit">' + developer_credit + '</span></div><div class="footer-actions"><div class="footer-links"><a href="' + route(lang,'report/') + '">' + t['bug'] + '</a><a href="https://github.com/markusthemaker/WSPRadar" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div><div class="footer-legal"><a href="' + route(lang,'documentation/full/#sec-disclaimer') + '">' + t['disclaimer'] + '</a></div></div></footer>')
        scripts = ''
        if math:
            scripts = '<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]},options:{ignoreHtmlClass:".*",processHtmlClass:"math"}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>'
        entry_script='<script src="/assets/entry.js"></script>' if root_alias else ''
        component_assets = '<link rel="stylesheet" href="/assets/demo-walkthrough.css"><script src="/assets/demo-walkthrough.js" defer></script>' if case_study else ''
        html = self.template.substitute(lang=lang,title=escape(title),description=escape(t["intro"],quote=True),canonical=SITE_URL+route(lang,suffix),alternate_en=SITE_URL+route("en",suffix),alternate_de=SITE_URL+route("de",suffix),skip_label=t["skip"],header=self.header(lang,active,suffix),body=body,footer=footer,math_scripts=scripts,entry_script=entry_script,component_assets=component_assets,landing_css_version=self.landing_css_version,print_assets_version=self.print_assets_version,body_attrs=' class="demo-case-page"' if case_study else '')
        destination = "index.html" if root_alias else f"{lang}/{suffix}index.html"
        self.pages[destination] = load_print_images_with_page(open_pdf_links_in_new_tabs(html))

    def manual_index(self, lang, *, include_disclaimer=True, include_introduction=True):
        """Present the manual parts with optional orientation and disclaimer links."""
        t = COPY[lang]
        groups = []
        current = []
        for section in self.sections[lang]:
            if section.level == 2 and current:
                groups.append(current)
                current = []
            current.append(section)
        if current:
            groups.append(current)
        supplementary_links = []
        chunks = []
        for group in groups:
            first = group[0]
            if first.level != 2:
                # The introductory chapter has its own featured card; the contents
                # section remains available in the manual and chapter navigation.
                continue
            if len(group) == 1:
                if not include_disclaimer and 'sec-disclaimer' in first.anchors:
                    continue
                supplementary_links.append('<a href="' + chapter_url(lang, first.key) + '">' + escape(first.title) + '</a>')
                continue
            entries = []
            for section in group[1:]:
                numbered = re.match(r'(?:(?:Appendix|Anhang) )?([0-9]+|[A-Z])[.:] (.+)', section.title)
                if numbered:
                    label = '<span class="chapter-number" aria-hidden="true">' + escape(numbered[1]) + '</span><span>' + escape(numbered[2]) + '</span>'
                    attributes = ' class="numbered-chapter" aria-label="' + escape(section.title, quote=True) + '"'
                else:
                    label = escape(section.title)
                    attributes = ' class="unnumbered-chapter"'
                entries.append('<li><a' + attributes + ' href="' + chapter_url(lang, section.key) + '">' + label + '</a></li>')
            heading_link = '<a href="' + chapter_url(lang, first.key) + '">' + escape(first.title) + '</a>'
            chunks.append('<section class="manual-group"><h3>' + heading_link + '</h3><ul>' + ''.join(entries) + '</ul></section>')
        introduction = ''
        if include_introduction:
            introduction = ('<section class="manual-start" aria-labelledby="manual-start-title">'
                            + '<h2 id="manual-start-title">' + t['manual_start_title'] + '</h2>'
                            + '<p>' + t['manual_start_body'] + '</p>'
                            + '<a class="text-link" href="' + self.anchors[lang]['sec-1'] + '">'
                            + t['manual_start_link'] + ' →</a></section>')
        return (introduction
                + '<div class="manual-index">' + ''.join(chunks) + '</div>'
                + ('<div class="manual-supplementary">' + ''.join(supplementary_links) + '</div>' if supplementary_links else ''))

    def evidence_items(self, lang):
        return self.website["evidence"][lang]

    def evidence_path(self, lang):
        evidence = ''.join('<a class="evidence-step" href="'+route(lang,'guides/read-results/#'+item["id"])+'"><span class="step-number">'+f'{number:02d}'+'</span><span><strong>'+escape(item["title"])+'</strong><small>'+escape(item["question"])+'</small></span></a>' for number,item in enumerate(self.evidence_items(lang),1))
        return '<div class="evidence-path"><p class="eyebrow">'+COPY[lang]["follow"]+'</p>'+evidence+'</div>'

    def home(self, lang):
        t = COPY[lang]
        body = '<section class="hero overview-hero"><p class="eyebrow">'+t["eyebrow"]+'</p><h2>'+t["hero"]+'</h2><p class="intro">'+t["intro"]+'</p><div class="actions">'+button(t["start"]+' →',route(lang,'demos/'))+button(t["open"],APP_URL,secondary=True,external=True)+'</div></section>'
        steps = (
            ('choose', self.anchors[lang]['sec-2-2']+'#sec-2-2', t['choose_link']),
            ('experiment', self.anchors[lang]['sec-2-1']+'#sec-2-1', t['experiment_link']),
            ('run', APP_URL, t['open']),
        )
        cards = []
        for number, (key, href, label) in enumerate(steps, 1):
            external = href == APP_URL
            attributes = ' target="_blank" rel="noopener noreferrer"' if external else ''
            cards.append('<article class="journey-card"><span class="journey-number" aria-hidden="true">'+f'{number:02d}'+'</span><h2>'+t[key+'_title']+'</h2><p>'+t[key+'_body']+'</p><a class="text-link" href="'+href+'"'+attributes+'>'+label+(' ↗' if external else ' →')+'</a></article>')
        body += '<section class="journey">'+''.join(cards)+'</section>'
        body += '<section class="feature"><h2>'+t["demo_feature"]+'</h2><p>'+t["demo_context"]+'</p><p class="muted">'+t["demo_summary"]+'</p>'+button(t["browse_demos"]+' →',route(lang,'demos/'))+'</section>'
        body += '<section><div class="section-heading"><h2>'+t["all_docs"]+'</h2></div>'+self.manual_index(lang, include_disclaimer=False, include_introduction=False)+'</section>'
        body += '<section class="support-strip"><div><h2>'+t["connect"]+'</h2><p>'+t["connect_body"]+'</p><a class="text-link" href="'+route(lang,'community/')+'">'+t["community"]+' →</a></div><div><h2>'+t["improve"]+'</h2><p>'+t["improve_body"]+'</p><a class="text-link" href="'+route(lang,'report/')+'">'+t["bug"]+' →</a></div></section>'
        body = render_landing(self, lang, button, route, APP_URL) + '<details class="more-guidance" id="more-guidance"><summary>' + escape(self.landing[lang]['more_guidance']) + '</summary>' + body + '</details>'
        self.page(lang,'',t["home"],body,'home')
        if lang == 'en':
            self.page(lang,'',t["home"],body,'home',root_alias=True)

    def documentation(self, lang):
        t = COPY[lang]
        index = '<p class="eyebrow">'+t["docs"]+'</p><h1>'+t["all_docs"]+'</h1><p class="intro">'+t["manual_intro"]+'</p>'+self.manual_index(lang, include_disclaimer=False)
        self.page(lang,'documentation/',t["docs"],index,'docs')
        sidebar = '<details class="reader-index" open><summary>'+t["docs"]+'</summary>' + ''.join('<a class="'+('part-link' if s.level==2 else 'chapter-link')+'" href="'+chapter_url(lang,s.key)+'">'+escape(s.title)+'</a>' for s in self.sections[lang]) + '</details>'
        for number,section in enumerate(self.sections[lang]):
            selected = sidebar.replace('href="'+chapter_url(lang,section.key)+'"','aria-current="page" href="'+chapter_url(lang,section.key)+'"')
            article = self.md(section.text,lang)
            article = re.sub(r'<h([23])>(.*?)</h\1>', r'<h1>\2</h1>', article, count=1, flags=re.DOTALL)
            adjacent=[]
            for delta,key in ((-1,"previous"),(1,"next")):
                if 0 <= number+delta < len(self.sections[lang]):
                    neighbor=self.sections[lang][number+delta]
                    adjacent.append('<a href="'+chapter_url(lang,neighbor.key)+'">'+t[key]+': '+escape(neighbor.title)+'</a>')
            body='<p class="breadcrumb"><a href="'+route(lang,'documentation/')+'">'+t["docs"]+'</a> / '+escape(section.title)+'</p><div class="reader-layout">'+selected+'<article class="prose">'+article+'<nav class="doc-actions" aria-label="'+t["docs"]+'">'+''.join(adjacent)+'</nav></article></div>'
            active = 'docs'
            self.page(lang,'documentation/'+section.key+'/',section.title,body,active,math=True)
        body='<h1>'+t["all_docs"]+'</h1><p class="print-note">'+t["print"]+'</p><div class="prose">'+self.md(self.manuals[lang],lang,continuous=True)+'</div>'
        self.page(lang,'documentation/full/',t["full_manual"],body,'docs',math=True)

    def media(self, item, lang, *, screenshot=False):
        t=COPY[lang]
        url='/content/'+item['asset_path']
        caption=self.md(item.get('caption',{}).get(lang,''),lang)
        provenance=item.get('provenance',{})
        detail=''
        if screenshot:
            captured_utc = str(provenance.get('captured_at_utc', provenance.get('captured_utc', '')))
            detail = escape(t['english_capture']) + ' <span class="technical-value">' + escape(captured_utc) + '</span>'
        size=provenance.get('image_px', [item.get('width'),item.get('height')])
        dimensions=f' width="{int(size[0])}" height="{int(size[1])}"' if all(size) else ''
        label=escape(t['full_size']+': '+item['title'][lang],quote=True)
        return '<figure class="figure-block"><a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer" aria-label="'+label+'"><img loading="lazy"'+dimensions+' src="'+escape(url,quote=True)+'" alt="'+escape(item['alt'][lang],quote=True)+'"></a><figcaption><strong>'+escape(item['title'][lang])+'</strong>'+caption+'<a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer">'+t['full_size']+' ↗</a>'+('<span class="source-note">'+detail+'</span>' if detail else '')+'</figcaption></figure>'

    def demo_pages(self,lang):
        t=COPY[lang]
        cards=[]
        authored={d['id']:d for d in self.website['demos']}
        for demo in self.demos:
            identity=demo['id']
            presentation = self.demo_walkthroughs.get('demos', {}).get(identity)
            if not presentation:
                raise ValueError('Missing default Markdown walkthrough for demo: ' + identity)
            hero = read_sections(safe_path(self.demo_root, presentation['markdown_paths'][lang]))['hero']
            title, _ = heading_and_body(hero, 1)
            figures=[f for f in self.figures if f['demo_id']==identity]
            screenshots=[s for s in self.screenshots if s['demo_id']==identity]
            steps=authored.get(identity,{}).get('walkthrough',{}).get(lang,[])
            settings=demo['settings']['core_parameters']
            meta=settings['analysis_direction'].upper()+' · '+settings['band']+' · '+settings['callsign']
            summary=steps[0]['body'] if steps else ''
            preview=('<img src="/content/'+figures[0]['asset_path']+'" alt="'+escape(figures[0]['alt'][lang],quote=True)+'" loading="lazy">') if figures else ''
            cards.append('<article class="demo-card" data-filter-text="'+escape(title+' '+meta+' '+summary,quote=True)+'">'+preview+'<p class="meta">'+escape(meta)+'</p><h2>'+escape(title)+'</h2><a class="text-link" href="'+route(lang,'demos/'+identity+'/')+'">'+t['walkthrough']+' →</a></article>')
            body = render_demo(self, lang, demo, presentation, button, route, APP_URL)
            self.page(lang,'demos/'+identity+'/',title,body,'demos',math=True,case_study=True)
        body='<p class="eyebrow">'+t['demos']+'</p><h1>'+t['demo_title']+'</h1><p class="intro">'+t['demo_intro']+'</p><label class="search-label">'+t['filter']+'<input type="search" data-filter-input autocomplete="off"></label><p class="small muted" data-filter-status aria-live="polite">7 / 7</p><div class="demo-grid">'+''.join(cards)+'</div>'
        self.page(lang,'demos/',t['demos'],body,'demos')

    def guides(self,lang):
        t=COPY[lang]
        anchor_names={'map-view':'sec-3-4','segment-inspector':'sec-3-6','station-insights':'sec-3-7','drill-down':'sec-3-8'}
        capture_stages={'map-view':'map','segment-inspector':'segment','station-insights':'stations','drill-down':'drilldown'}
        body='<p class="breadcrumb"><a href="'+route(lang,'documentation/')+'">'+t['docs']+'</a></p><p class="eyebrow">'+t['follow']+'</p><h1>'+t['guides_title']+'</h1><p class="intro">'+t['guides_intro']+'</p><nav class="guide-links" aria-label="'+t['follow']+'">'+''.join('<a href="#'+i['id']+'">'+escape(i['title'])+'</a>' for i in self.evidence_items(lang))+'</nav>'
        for n,item in enumerate(self.evidence_items(lang),1):
            shots=[s for s in self.screenshots if s.get('stage')==capture_stages[item['id']]]
            shot=shots[0] if shots else None
            body+='<section class="guide-section" id="'+item['id']+'"><p class="eyebrow">'+f'{n:02d}'+' · '+escape(item['title'])+'</p><h2>'+escape(item['question'])+'</h2><div class="prose">'+self.md(item['body'],lang)+'</div>'
            if shot:body+=self.media(shot,lang,screenshot=True)
            anchor=anchor_names[item['id']]
            example=shot['demo_id'] if shot else self.demos[0]['id']
            body+='<div class="guide-links"><a href="'+self.anchors[lang][anchor]+'#'+anchor+'">'+t['read_manual']+' →</a><a href="'+route(lang,'demos/'+example+'/')+'">'+t['related_demo']+' →</a></div></section>'
        self.page(lang,'guides/read-results/',t['guides_title'],body,'guides',math=True)

    def support(self,lang):
        t=COPY[lang]
        options=[
            ('questions',('questions_body',),HELP_URL,'ask'),
            ('experiments',('experiments_body',),EXPERIMENTS_URL,'share_experiment'),
            ('feature',('feature_body',),IDEAS_URL,'continue'),
            ('report_category',('report_summary',),REPORT_URL,'continue'),
        ]
        cards='<div class="report-options">'
        for key,paragraphs,url,action in options:
            cards+='<article><h2>'+t[key]+'</h2>'+''.join('<p>'+t[body].format(manual_url=route(lang,'documentation/full/'))+'</p>' for body in paragraphs)
            cards+='<div class="actions">'+button(t[action],url,external=True)
            cards+='</div></article>'
        cards+='</div>'
        participation='<p>'+t['participation']+'</p>'
        self.page(lang,'community/',t['community'],'<p class="eyebrow">'+t['community']+'</p><h1>'+t['community_title']+'</h1><p class="intro">'+t['community_intro']+'</p>'+participation+cards,'community')
        self.page(lang,'report/',t['bug'],'<p class="eyebrow">'+t['improve']+'</p><h1>'+t['bug']+'</h1><p class="intro">'+t['bug_intro']+'</p>'+participation+'<div class="actions">'+button(t['continue'],REPORT_URL,external=True)+'</div><p>'+t['scientific_body']+'</p><p>'+t['report_body']+'</p><p>'+t['report_followup']+'</p>'+cards,'bug')

    def render(self):
        for lang in COPY:
            self.home(lang)
            self.documentation(lang)
            self.demo_pages(lang)
            self.guides(lang)
            self.support(lang)
        return self.pages


class LinkInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.links=[]
        self.images=[]
    def handle_starttag(self,tag,attributes):
        attrs=dict(attributes)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag in ('a','link') and 'href' in attrs:self.links.append(attrs['href'])
        if tag in ('img','script') and attrs.get('src','').startswith('/'):self.links.append(attrs['src'])
        if tag in ('source','img') and attrs.get('srcset'):
            self.links.extend(candidate.strip().split()[0] for candidate in attrs['srcset'].split(',') if candidate.strip().startswith('/'))
        if tag=='img':self.images.append(attrs)


def validate_site(directory: Path):
    inventories={}
    errors=[]
    for page in directory.rglob('*.html'):
        inventory=LinkInventory()
        inventory.feed(page.read_text(encoding='utf-8'))
        inventories[page.resolve()]=inventory
        if len(inventory.ids)!=len(set(inventory.ids)):errors.append(f'Duplicate HTML IDs: {page.relative_to(directory)}')
        if any('alt' not in image or (not image['alt'] and image.get('aria-hidden') != 'true') for image in inventory.images):errors.append(f'Image missing alt: {page.relative_to(directory)}')
    for page,inventory in inventories.items():
        for href in inventory.links:
            url=urlsplit(href)
            if url.scheme or url.netloc:continue
            target=((directory / unquote(url.path).lstrip('/')) if url.path.startswith('/') else (page.parent / unquote(url.path))).resolve() if url.path else page
            if not target.is_relative_to(directory.resolve()):errors.append(f'Escaping link: {href}');continue
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append(f'Missing local target: {page.relative_to(directory)} -> {href}');continue
            if url.fragment and target in inventories and unquote(url.fragment) not in inventories[target].ids:
                errors.append(f'Missing anchor: {page.relative_to(directory)} -> {href}')
    if errors:raise ValueError('\n'.join(sorted(set(errors))))
    return len(inventories)


def output_files(builder: SiteBuilder) -> dict[str, bytes]:
    """Construct the complete static payload before writing or checking it."""
    pages=builder.render()
    files={name:value.encode('utf-8') for name,value in pages.items()}
    for name in ('site.css','landing.css','print.css','print.js','site.js','entry.js','demo-walkthrough.css','demo-walkthrough.js'):
        files['assets/'+name]=(SITE/name).read_bytes()
    asset_root = SITE / 'assets' / 'landing'
    for name in builder.landing_assets['publish_files']:
        relative = PurePosixPath(name)
        source = (asset_root / name).resolve()
        if relative.is_absolute() or '..' in relative.parts or not source.is_relative_to(asset_root.resolve()):
            raise ValueError('Unsafe landing asset path: ' + name)
        files['assets/landing/' + name] = source.read_bytes()
    files.update(resource_files(builder.demo_root, builder.demo_walkthroughs["demos"]))
    colors=builder.brand.get('colors',{})
    theme={variable:colors[key] for variable,key in (('--bg','background'),('--green','primary'),('--text','text')) if key in colors}
    if any(not re.fullmatch(r'#[0-9a-fA-F]{6}',value) for value in theme.values()):
        raise ValueError('Invalid imported brand color')
    if theme:
        files['assets/site.css']+=('\n:root{'+''.join(key+':'+value+';' for key,value in theme.items())+'}\n').encode('utf-8')
    fonts=[]
    for font in builder.brand['fonts']:
        fonts.append('@font-face{font-family:"'+font['family']+'";font-style:'+font['style']+';font-weight:'+str(font['weight'])+';font-display:swap;src:url("/content/'+font['path']+'") format("woff2");'+('unicode-range:'+font['unicode_range']+';' if font.get('unicode_range') else '')+'}')
    files['assets/fonts.css']=('\n'.join(fonts)+'\n').encode('utf-8')
    for name in (*builder.manifest['files'],'manifest.json'):
        files['content/'+name]=(builder.content/name).read_bytes()
    files['CNAME']=b'wspradar.org\n'
    files['.nojekyll']=b''
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+SITE_URL+'/'+name.removesuffix('index.html')+'</loc></url>' for name in sorted(pages) if name!='index.html')+'</urlset>\n'
    files['sitemap.xml']=sitemap.encode('utf-8')
    files['robots.txt']=('User-agent: *\nAllow: /\nSitemap: '+SITE_URL+'/sitemap.xml\n').encode('utf-8')
    return files


def build(*, check=False, offline=False):
    if offline and not check:
        raise ValueError('--offline is only valid with --check')
    builder=SiteBuilder()
    files=output_files(builder)
    actual={p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob('*') if p.is_file()}
    extra=actual-set(files)
    if extra:
        raise ValueError('Unexpected build files; review before removal: '+', '.join(sorted(extra)))
    for name,data in files.items():
        path=OUTPUT/name
        if not path.resolve().is_relative_to(OUTPUT.resolve()):
            raise ValueError(f'Unsafe build output path: {name}')
        if check:
            if not path.is_file() or path.read_bytes()!=data:
                raise ValueError(f'Missing or stale built file: {name}')
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
    count=validate_site(OUTPUT)
    if check:
        print(f'Checked {count} pages, {len(files)} files, local links, anchors, and image alternatives.')
        if offline:
            print('External URLs not checked (--offline); only local build validation completed.')
            return
        links=collect_external_links(files,SITE_URL)
        print(f'Checking {len(links)} distinct external HTTP(S) URLs without authentication...',flush=True)
        results=check_external_links(links,community_url=COMMUNITY_URL)
        counts={status:sum(result.status==status for result in results)
                for status in ('available','redirected','broken','unverified')}
        for result in results:
            if result.status=='available':
                continue
            locations=', '.join(result.locations[:3])
            if len(result.locations)>3:
                locations+=f' (+{len(result.locations)-3} more files)'
            print(f'{result.status.upper()}: {result.url}\n  {result.detail}\n  Referenced in: {locations}')
        print('External URLs: '+', '.join(f'{count} {status}' for status,count in counts.items())+'.')
        if counts['broken'] or counts['unverified']:
            raise ValueError('External URL validation incomplete: broken or unverified URLs remain; see details above.')
        return
    print(f'Built {count} pages with complete bilingual manuals and {len(builder.demos)} demos.')
    print(f'Imported {len(builder.figures)} figures and {len(builder.screenshots)} live screenshots.')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Verify generated files, local links, and live external HTTP(S) URLs without writing')
    parser.add_argument('--offline',action='store_true',help='With --check, explicitly skip live external URL validation')
    args=parser.parse_args(argv)
    if args.offline and not args.check:
        parser.error('--offline requires --check')
    try:
        build(check=args.check,offline=args.offline)
    except ValueError as error:
        parser.exit(1,f'Validation failed: {error}\n')


if __name__=='__main__':
    main()


