"""Publication triggers and permissions must keep intermediate backups lightweight."""

from pathlib import Path
import re
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/deploy-pages.yml"


class PagesWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_expected_website_domain_is_www(self):
        self.assertEqual((WORKFLOW.parents[2] / "CNAME").read_text(encoding="utf-8").strip(),
                         "www.wspradar.org")
        self.assertIn(".cname == \"www.wspradar.org\"", self.workflow)
        self.assertIn('test "$(cat generated/CNAME)" = \'www.wspradar.org\'', self.workflow)

    def test_automatic_push_runs_are_main_only(self):
        triggers = re.search(r"(?ms)^on:\n(.*?)(?=^\S)", self.workflow).group(1)
        push = re.search(r"(?ms)^  push:\n(.*?)(?=^  \S|\Z)", triggers).group(1)
        branches = re.search(r"(?m)^    branches: \[([^\]]+)\]$", push).group(1)
        self.assertEqual([branch.strip() for branch in branches.split(",")], ["main"])

    def test_manual_validation_is_available_without_pull_request_triggers(self):
        triggers = re.search(r"(?ms)^on:\n(.*?)(?=^\S)", self.workflow).group(1)
        self.assertEqual(re.findall(r"(?m)^  ([a-z_]+):", triggers), ["push", "workflow_dispatch"])
        self.assertRegex(triggers, r"(?m)^  workflow_dispatch:\s*$")

    def test_upload_and_deployment_stay_restricted_to_canonical_main(self):
        upload = self.workflow.split("      - name: Upload generated website only\n", 1)[1].split("  deploy:\n", 1)[0]
        deploy = self.workflow.split("  deploy:\n", 1)[1]
        for block in (upload, deploy):
            guard = re.search(r"(?ms)^ +if: >-\n((?: +github\.[^\n]+\n)+)", block).group(1)
            conditions = [line.strip().removesuffix("&&").strip() for line in guard.splitlines()]
            self.assertEqual(conditions, [
                "github.repository == 'markusthemaker/WSPRadar'",
                "github.ref == 'refs/heads/main'",
                "github.event_name != 'pull_request'",
            ])
        self.assertIn("          path: generated\n", upload)
        self.assertIn("    needs: build\n", deploy)
        self.assertIn("    permissions:\n      pages: write\n      id-token: write\n", deploy)


if __name__ == "__main__":
    unittest.main()
