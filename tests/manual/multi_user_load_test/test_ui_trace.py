"""Structural trace contracts with real protobuf messages; no browser or server."""

from datetime import datetime, timezone
import json
import unittest

from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from streamlit.proto.BackMsg_pb2 import BackMsg

try:
    from .ui_trace import UITrace
except ImportError:
    from ui_trace import UITrace


def observe(trace, message, **context):
    decoded = ForwardMsg()
    decoded.ParseFromString(message.SerializeToString())
    trace.observe(decoded, script_run_id=context.get("script_run_id", "run-1"),
                  fragment_ids=context.get("fragment_ids", ["inspector"]),
                  action_phase=context.get("action_phase", "scope"))


def markdown_message(message_hash, path, body="omitted content"):
    message = ForwardMsg(hash=message_hash)
    message.metadata.delta_path.extend(path)
    message.delta.fragment_id = "inspector"
    message.delta.new_element.markdown.body = body
    return message


class UITraceTests(unittest.TestCase):
    def test_records_paths_node_types_and_ids_without_rendered_content(self):
        trace = UITrace()
        block = ForwardMsg(hash="block-hash")
        block.metadata.delta_path.extend([0, 2])
        block.delta.add_block.vertical.SetInParent()
        block.delta.add_block.id = "scope-container"
        observe(trace, block)

        widget = ForwardMsg(hash="widget-hash")
        widget.metadata.delta_path.extend([0, 2, 0])
        widget.delta.new_element.selectbox.id = "scope-widget"
        widget.delta.new_element.selectbox.label = "SECRET LABEL"
        widget.delta.new_element.selectbox.options.extend(["SECRET OPTION"])
        observe(trace, widget)
        observe(trace, markdown_message("markdown-hash", [0, 2, 1], "SECRET MARKDOWN"))

        image = ForwardMsg(hash="image-hash")
        image.delta.new_element.imgs.imgs.add(url="SECRET IMAGE", caption="SECRET CAPTION")
        observe(trace, image)
        table = ForwardMsg(hash="table-hash")
        table.delta.new_element.dataframe.id = "station-table"
        table.delta.new_element.dataframe.arrow_data.data = b"SECRET TABLE DATA"
        table.delta.new_element.dataframe.selection_state = "SECRET SELECTION"
        observe(trace, table)

        snapshot = trace.snapshot()
        records = snapshot["records"]
        self.assertEqual(records[0]["metadata"]["delta_path"], [0, 2])
        self.assertEqual(records[0]["structure"]["delta"]["block"],
                         {"type": "vertical", "id": "scope-container"})
        self.assertEqual(records[1]["structure"]["delta"]["element"],
                         {"type": "selectbox", "id": "scope-widget"})
        self.assertEqual(records[-1]["structure"]["delta"]["element"],
                         {"type": "dataframe", "id": "station-table"})
        self.assertNotIn("SECRET", json.dumps(snapshot))
        self.assertNotIn("SECRET", repr(trace.__dict__), "The compact cache must omit content too")

    def test_reference_uses_cached_structure_with_current_reference_metadata(self):
        trace = UITrace()
        original = markdown_message("cached-node", [0, 1, 2])
        original.metadata.cacheable = True
        original.metadata.active_script_hash = "old-script"
        observe(trace, original)
        reference = ForwardMsg(ref_hash="cached-node")
        reference.metadata.delta_path.extend([0, 9, 4])
        reference.metadata.active_script_hash = "new-script"
        observe(trace, reference, script_run_id="run-2", action_phase="export_download")
        resolved = trace.snapshot()["records"][-1]
        self.assertEqual(resolved["message_type"], "ref_hash")
        self.assertFalse(resolved["unresolved_reference"])
        self.assertEqual(resolved["structure"]["type"], "delta")
        self.assertEqual(resolved["structure"]["delta"]["element"]["type"], "markdown")
        self.assertEqual(resolved["metadata"]["delta_path"], [0, 9, 4])
        self.assertEqual(resolved["metadata"]["active_script_hash"], "new-script")
        self.assertFalse(resolved["metadata"]["cacheable"])
        self.assertEqual(resolved["script_run_id"], "run-2")
        self.assertEqual(resolved["action_phase"], "export_download")

    def test_records_and_cache_are_bounded_and_reference_reads_refresh_lru(self):
        trace = UITrace(limit=2, cache_limit=2)
        observe(trace, markdown_message("a", [0, 1]))
        observe(trace, markdown_message("b", [0, 2]))
        observe(trace, ForwardMsg(ref_hash="a"))
        observe(trace, markdown_message("c", [0, 3]))
        observe(trace, ForwardMsg(ref_hash="b"))
        observe(trace, ForwardMsg(ref_hash="a"))
        snapshot = trace.snapshot()
        self.assertEqual([record["sequence"] for record in snapshot["records"]], [5, 6])
        self.assertEqual(snapshot["observed_message_count"], 6)
        self.assertEqual(snapshot["dropped_record_count"], 4)
        self.assertEqual(snapshot["cache_entry_count"], 2)
        self.assertEqual(snapshot["cache_eviction_count"], 1)
        self.assertEqual(snapshot["unresolved_reference_count"], 1)
        self.assertTrue(snapshot["records"][0]["unresolved_reference"])
        self.assertIsNone(snapshot["records"][0]["structure"]["type"])
        self.assertFalse(snapshot["records"][1]["unresolved_reference"])

    def test_transients_record_structural_types_and_explicit_empty_clear(self):
        trace = UITrace()
        transient = ForwardMsg()
        transient.metadata.delta_path.extend([0, 7])
        transient.delta.new_transient.elements.add().spinner.text = "SECRET SPINNER"
        transient.delta.new_transient.elements.add().markdown.body = "SECRET TRANSIENT MARKDOWN"
        observe(trace, transient)
        clear = ForwardMsg()
        clear.metadata.delta_path.extend([0, 7])
        clear.delta.new_transient.SetInParent()
        observe(trace, clear)
        records = trace.snapshot()["records"]
        self.assertEqual(records[0]["structure"]["delta"]["transient"]["elements"],
                         [{"type": "spinner"}, {"type": "markdown"}])
        self.assertEqual(records[1]["structure"]["delta"]["transient"]["element_count"], 0)
        self.assertNotIn("SECRET", repr(trace.__dict__))

    def test_transient_summary_has_a_per_message_bound(self):
        trace = UITrace()
        message = ForwardMsg()
        for _ in range(40):
            message.delta.new_transient.elements.add().spinner.text = "omitted"
        observe(trace, message)
        transient = trace.snapshot()["records"][0]["structure"]["delta"]["transient"]
        self.assertEqual(transient["element_count"], 40)
        self.assertEqual(len(transient["elements"]), 32)
        self.assertTrue(transient["elements_truncated"])

    def test_lifecycle_records_keep_run_and_completion_status_without_session_content(self):
        trace = UITrace()
        started = ForwardMsg()
        started.new_session.script_run_id = "run-fragment"
        started.new_session.fragment_ids_this_run.append("inspector")
        observe(trace, started)
        observe(trace, ForwardMsg(script_finished=ForwardMsg.FINISHED_FRAGMENT_RUN_SUCCESSFULLY))
        records = trace.snapshot()["records"]
        self.assertEqual(records[0]["structure"]["new_session"],
                         {"script_run_id": "run-fragment", "fragment_ids": ["inspector"]})
        self.assertEqual(records[1]["structure"]["script_finished"],
                         "FINISHED_FRAGMENT_RUN_SUCCESSFULLY")
        self.assertEqual(datetime.fromisoformat(records[0]["timestamp_utc"]).tzinfo, timezone.utc)
        self.assertLessEqual(records[0]["monotonic_seconds"], records[1]["monotonic_seconds"])

    def test_snapshot_mutation_cannot_change_stored_records_or_cached_structure(self):
        trace = UITrace()
        observe(trace, markdown_message("cached-node", [0, 1]))
        snapshot = trace.snapshot()
        snapshot["records"][0]["metadata"]["delta_path"].append(999)
        snapshot["records"][0]["structure"]["delta"]["element"]["type"] = "corrupted"
        observe(trace, ForwardMsg(ref_hash="cached-node"))
        records = trace.snapshot()["records"]
        self.assertEqual(records[0]["metadata"]["delta_path"], [0, 1])
        self.assertEqual(records[-1]["structure"]["delta"]["element"]["type"], "markdown")

    def test_invalid_capacities_fail_before_observation(self):
        for capacity in (0, -1, True, 1.5):
            with self.subTest(capacity=capacity):
                with self.assertRaises(ValueError):
                    UITrace(limit=capacity)
                with self.assertRaises(ValueError):
                    UITrace(cache_limit=capacity)

    def test_outgoing_scope_change_is_distinguished_from_unchanged_widget_states(self):
        trace = UITrace()

        def send(scope):
            message = BackMsg()
            request = message.rerun_script
            request.fragment_id = "inspector-fragment"
            request.is_auto_rerun = False
            request.query_string = "SECRET QUERY STRING"
            request.widget_states.widgets.add(id="scope-widget").string_array_value.data.append(scope)
            request.widget_states.widgets.add(id="time-bin-widget", string_value="SECRET TIME BIN")
            decoded = BackMsg()
            decoded.ParseFromString(message.SerializeToString())
            trace.observe_back_message(decoded, script_run_id="run-6",
                                       fragment_ids=["inspector-fragment"], action_phase="scope")

        send("SECRET FULL RANGE")
        send("SECRET NEW SCOPE")
        send("SECRET NEW SCOPE")
        records = trace.snapshot()["records"]
        baseline = records[0]["structure"]["rerun_script"]
        changed = records[1]["structure"]["rerun_script"]
        unchanged = records[2]["structure"]["rerun_script"]
        self.assertTrue(baseline["initial_widget_baseline"])
        self.assertEqual(baseline["changed_widget_count"], 2)
        self.assertFalse(changed["initial_widget_baseline"])
        self.assertEqual(changed["fragment_id"], "inspector-fragment")
        self.assertFalse(changed["is_auto_rerun"])
        self.assertEqual(changed["changed_widget_count"], 1)
        self.assertEqual(changed["changed_widgets"][0]["id"], "scope-widget")
        self.assertEqual(changed["changed_widgets"][0]["value_type"], "string_array_value")
        self.assertEqual(changed["changed_widgets"][0]["change"], "changed")
        self.assertEqual(len(changed["changed_widgets"][0]["digest"]), 64)
        self.assertNotEqual(changed["changed_widgets"][0]["digest"], baseline["changed_widgets"][0]["digest"])
        self.assertEqual(unchanged["changed_widgets"], [])
        self.assertEqual(unchanged["changed_widget_count"], 0)
        self.assertEqual([record["direction"] for record in records], ["out", "out", "out"])
        self.assertNotIn("SECRET", json.dumps(trace.snapshot()))
        self.assertNotIn("SECRET", repr(trace.__dict__))

    def test_outgoing_uses_shared_chronology_bounded_lookup_and_capped_ids(self):
        trace = UITrace(limit=2, cache_limit=2)
        observe(trace, markdown_message("incoming", [0]))
        message = BackMsg()
        message.rerun_script.widget_states.widgets.add(id="a" * 600, string_value="SECRET VALUE")
        message.rerun_script.widget_states.widgets.add(id="widget-b", int_value=1)
        message.rerun_script.widget_states.widgets.add(id="widget-c", int_value=2)
        trace.observe_back_message(message, script_run_id="run-1", fragment_ids=[], action_phase="scope")
        trace.observe_back_message(BackMsg(app_heartbeat=True), script_run_id="run-1",
                                   fragment_ids=[], action_phase="scope")
        snapshot = trace.snapshot()
        self.assertEqual([record["sequence"] for record in snapshot["records"]], [2, 3])
        self.assertEqual(snapshot["dropped_record_count"], 1)
        self.assertEqual(snapshot["widget_digest_count"], 2)
        self.assertEqual(snapshot["widget_digest_limit"], 2)
        changed = snapshot["records"][0]["structure"]["rerun_script"]["changed_widgets"][0]
        self.assertEqual(len(changed["id"]), 512)
        self.assertTrue(changed["id_truncated"])
        self.assertEqual(snapshot["records"][1]["structure"], {"type": "app_heartbeat"})
        self.assertNotIn("SECRET", repr(trace.__dict__))


if __name__ == "__main__":
    unittest.main()
