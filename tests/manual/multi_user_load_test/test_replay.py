"""Scoped checks for offline preparation and the real query-cache boundary."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HARNESS_DIRECTORY = Path(__file__).resolve().parent
if str(HARNESS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIRECTORY))

from replay import REPOSITORY_ROOT, prepare_streamlit_entrypoint


class ReplayTests(unittest.TestCase):
    def test_launcher_preserves_static_asset_bytes(self):
        with tempfile.TemporaryDirectory(prefix="wspradar replay ") as temporary_directory:
            output_directory = Path(temporary_directory)
            entrypoint = output_directory / prepare_streamlit_entrypoint(output_directory)
            compile(entrypoint.read_text(encoding="utf-8"), str(entrypoint), "exec")
            font_name = "fonts/space-mono-v17-400-normal-latin.woff2"
            self.assertEqual(
                (entrypoint.parent / "static" / font_name).read_bytes(),
                (REPOSITORY_ROOT / "static" / font_name).read_bytes(),
            )

    def test_prepared_url_queries_use_real_cache_and_unknown_query_fails_closed(self):
        """Check the full preparation/URL/cache boundary in isolated processes."""
        with tempfile.TemporaryDirectory(prefix="wspradar-replay-test-") as temporary_directory:
            preparation = subprocess.run(
                [sys.executable, str(HARNESS_DIRECTORY / "replay.py"), "--prepare", temporary_directory],
                cwd=REPOSITORY_ROOT, capture_output=True, text=True, timeout=180,
            )
            self.assertEqual(preparation.returncode, 0, preparation.stdout + preparation.stderr)
            verification_script = r'''
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import parse_qs

sys.path.insert(0, sys.argv[1])
from replay import install_offline_runtime

output_directory = Path(sys.argv[2])
manifest = install_offline_runtime(output_directory)
from config import BAND_MAP
from core.analysis_runner import build_analysis_batches
from core.data_engine import fetch_wspr_data
from core.math_utils import locator_to_latlon
from core.presentation_context import PresentationContext
from i18n import T
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.config_io import apply_config_state_values
from ui.url_state import build_config_from_url, parse_url_query

assert (output_directory / manifest['entrypoint']).is_file()
assert {scenario['id'] for scenario in manifest['scenarios']} >= {'benchmark-large', 'performance'}
for scenario in manifest['scenarios']:
    configuration = build_config_from_url(parse_url_query(parse_qs(scenario['query_string'])))
    state = {'lang': 'en'}
    apply_config_state_values(configuration, state)
    state['run_mode'] = configuration['analysis_direction'].upper()
    context = build_analysis_context_from_session_state(state)
    latitude, longitude = locator_to_latlon(context.qth)
    analyses = build_analysis_batches(
        context, configuration['start_utc'], configuration['end_utc'], latitude, longitude,
        f"AND band = '{BAND_MAP[context.band]}'",
        presentation_context=PresentationContext(solar_label='All', labels=T['en']),
    )
    prepared_counts = {entry['sha256']: entry['rows'] for entry in scenario['query_row_counts']}
    has_nonempty_rows = False
    for analysis in analyses:
        for query in filter(None, (analysis.query, analysis.legacy_query)):
            query_digest = hashlib.sha256(query.encode('utf-8')).hexdigest()
            fetched = fetch_wspr_data(query, response_format=analysis.response_format)
            assert fetched.error is None, fetched.error
            assert fetched.source.value in {'disk cache', 'memory cache'}, fetched.source
            assert len(fetched.dataframe) == prepared_counts[query_digest]
            has_nonempty_rows |= not fetched.dataframe.empty
    assert has_nonempty_rows, scenario['id']

try:
    fetch_wspr_data('SELECT 1 FORMAT CSVWithNames')
except RuntimeError as error:
    assert 'Offline load-test network guard' in str(error)
else:
    raise AssertionError('An unprepared exact query was not rejected')
print('URL/cache identity and fail-closed network checks passed')
'''
            verification = subprocess.run(
                [sys.executable, "-c", verification_script, str(HARNESS_DIRECTORY), temporary_directory],
                cwd=REPOSITORY_ROOT, capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(verification.returncode, 0, verification.stdout + verification.stderr)


if __name__ == "__main__":
    unittest.main()
