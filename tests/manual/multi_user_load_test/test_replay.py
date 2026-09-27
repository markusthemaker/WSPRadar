"""Scoped checks for offline preparation and the real query-cache boundary."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HARNESS_DIRECTORY = Path(__file__).resolve().parent
if str(HARNESS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIRECTORY))

from replay import REPOSITORY_ROOT, SCENARIO_DEFINITIONS, DEFAULT_SCENARIOS, prepare_streamlit_entrypoint


class ReplayTests(unittest.TestCase):
    def test_default_performance_uses_full_month_demo_capture(self):
        definitions = {scenario.id: scenario for scenario in SCENARIO_DEFINITIONS}
        self.assertEqual(DEFAULT_SCENARIOS, "benchmark-large,performance")
        self.assertEqual(definitions["performance"].source_mode, "query_capture")
        self.assertEqual(definitions["performance"].configuration_path.name,
                         "00c_griffiths_squibb_performance.config")
        self.assertEqual(definitions["performance-small"].source_mode, "frozen_reports")

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

    def test_captured_performance_queries_replay_raw_rows_through_real_cache(self):
        """Use synthetic captured query rows without making provider requests."""
        with tempfile.TemporaryDirectory(prefix="wspradar-captured-replay-test-") as temporary_directory:
            capture_directory = Path(temporary_directory) / "capture"
            output_directory = Path(temporary_directory) / "replay"
            capture_script = r'''
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, sys.argv[1])
from capture import CAPTURE_KIND, DEFAULT_CONFIGURATION, MANIFEST_NAME, build_query_plan, _file_record
import pandas as pd
import requests

def reject_provider_request(*args, **kwargs):
    raise AssertionError('Offline integration fixture attempted a provider request')

requests.sessions.Session.request = reject_provider_request
directory = Path(sys.argv[2])
directory.mkdir()
(directory / 'queries').mkdir()
(directory / 'results').mkdir()
configuration = directory / 'configuration.config'
shutil.copyfile(DEFAULT_CONFIGURATION, configuration)
_document, _normalized, plan = build_query_plan(DEFAULT_CONFIGURATION)
from config import WSPR_DATABASE_PROVIDERS
provider = WSPR_DATABASE_PROVIDERS[0]
raw_rows = pd.DataFrame({
    'time_slot': pd.Series([12425760], dtype='int64'),
    'peer_sign': pd.Series(['EA4URA'], dtype='string'),
    'peer_grid': pd.Series(['IN80CI'], dtype='string'),
    'target_seen': pd.Series([1], dtype='int64'),
    'external_seen': pd.Series([1], dtype='int64'),
    'target_snr': pd.Series([-10.123456789], dtype='float64'),
})
records = []
for index, query in enumerate(plan):
    sql_path = directory / 'queries' / f'{index:02d}.sql'
    sql_path.write_bytes(query['sql'].encode('utf-8'))
    result_path = directory / 'results' / f'{index:02d}.parquet'
    raw_rows.to_parquet(result_path, index=False)
    records.append({
        'analysis_id': query['analysis_id'], 'variant': query['variant'],
        'response_format': query['response_format'],
        'sql_sha256': hashlib.sha256(query['sql'].encode('utf-8')).hexdigest(),
        'sql_file': _file_record(sql_path, directory),
        'result_file': _file_record(result_path, directory), 'rows': len(raw_rows),
    })
manifest = {
    'schema_version': 1, 'kind': CAPTURE_KIND, 'status': 'complete',
    'captured_at_utc': '2026-09-27T00:00:00+00:00',
    'provider': {'key': provider.key, 'url': provider.url, 'display_name': provider.display_name},
    'configuration': _file_record(configuration, directory),
    'queries': records, 'query_result_rows': len(records),
    'source_note': 'Synthetic rows for the offline cache-boundary test only.',
}
(directory / MANIFEST_NAME).write_text(json.dumps(manifest), encoding='utf-8')
'''
            creation = subprocess.run(
                [sys.executable, "-c", capture_script, str(HARNESS_DIRECTORY), str(capture_directory)],
                cwd=REPOSITORY_ROOT, capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(creation.returncode, 0, creation.stdout + creation.stderr)
            preparation = subprocess.run(
                [sys.executable, str(HARNESS_DIRECTORY / "replay.py"), "--prepare", str(output_directory),
                 "--scenarios", "performance", "--performance-replay", str(capture_directory)],
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
capture_directory = Path(sys.argv[3])
manifest = install_offline_runtime(output_directory)
import pandas as pd
from capture import build_query_plan
from core.data_engine import fetch_wspr_data
from ui.url_state import build_config_from_url, parse_url_query

assert [scenario['id'] for scenario in manifest['scenarios']] == ['performance']
scenario = manifest['scenarios'][0]
assert scenario['source_mode'] == 'query_capture'
assert scenario['source_rows'] is None
assert scenario['source_fixture']['kind'] == 'exact-production-query-capture'
configuration = build_config_from_url(parse_url_query(parse_qs(scenario['query_string'])))
assert configuration['analysis_direction'] == 'rx'
assert configuration['callsign'] == 'G3ZIL'
assert configuration['benchmark_mode'] == 'none'
configuration_path = output_directory / scenario['config_path']
_document, _normalized, plan = build_query_plan(configuration_path)
captures = json.loads((capture_directory / 'capture.json').read_text(encoding='utf-8'))
captured_paths = {record['sql_sha256']: capture_directory / record['result_file']['path']
                  for record in captures['queries']}
prepared_queries = {record['sha256']: record for record in scenario['query_row_counts']}
assert scenario['query_result_rows'] == len(plan)
for query in plan:
    digest = hashlib.sha256(query['sql'].encode('utf-8')).hexdigest()
    captured_rows = pd.read_parquet(captured_paths[digest])
    for relative_cache_path in prepared_queries[digest]['cache_paths']:
        assert (output_directory / relative_cache_path).read_bytes() == captured_paths[digest].read_bytes()
        pd.testing.assert_frame_equal(pd.read_parquet(output_directory / relative_cache_path), captured_rows)
    fetched = fetch_wspr_data(query['sql'], response_format=query['response_format'])
    assert fetched.error is None, fetched.error
    assert fetched.source.value in {'disk cache', 'RAM cache'}, fetched.source
    assert len(fetched.dataframe) == len(captured_rows) == 1
    assert fetched.dataframe['peer_sign'].tolist() == ['EA4URA']
    # Reading through the production normalizer must not rewrite the raw cache.
    for relative_cache_path in prepared_queries[digest]['cache_paths']:
        retained_rows = pd.read_parquet(output_directory / relative_cache_path)
        pd.testing.assert_frame_equal(retained_rows, captured_rows)
        assert retained_rows['target_snr'].iloc[0] == -10.123456789
print('Captured-query replay, raw precision and real cache reads passed')
'''
            verification = subprocess.run(
                [sys.executable, "-c", verification_script, str(HARNESS_DIRECTORY),
                 str(output_directory), str(capture_directory)],
                cwd=REPOSITORY_ROOT, capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(verification.returncode, 0, verification.stdout + verification.stderr)

    def test_prepared_url_queries_use_real_cache_and_unknown_query_fails_closed(self):
        """Check the full preparation/URL/cache boundary in isolated processes."""
        with tempfile.TemporaryDirectory(prefix="wspradar-replay-test-") as temporary_directory:
            preparation = subprocess.run(
                [sys.executable, str(HARNESS_DIRECTORY / "replay.py"), "--prepare", temporary_directory,
                 "--scenarios", "benchmark-large,performance-small,benchmark-small"],
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
assert {scenario['id'] for scenario in manifest['scenarios']} == {'benchmark-large', 'performance-small', 'benchmark-small'}
for scenario in manifest['scenarios']:
    configuration = build_config_from_url(parse_url_query(parse_qs(scenario['query_string'])))
    state = {'lang': 'en'}
    apply_config_state_values(configuration, state)
    for state_key in (
        'val_results_selected_ranges_compare', 'val_results_selected_directions_compare',
        'val_results_selected_ranges_absolute', 'val_results_selected_directions_absolute',
    ):
        assert state[state_key] == 'all', (scenario['id'], state_key, state[state_key])
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
            assert fetched.source.value in {'disk cache', 'RAM cache'}, fetched.source
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
