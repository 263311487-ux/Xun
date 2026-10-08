import importlib.util
import unittest
from pathlib import Path
from urllib.error import HTTPError

SPEC = importlib.util.spec_from_file_location(
    "research_metrics", Path(__file__).resolve().parents[1] / "research_metrics.py"
)
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


class MetricsTests(unittest.TestCase):
    def test_unavailable_is_not_zero(self):
        def denied(_request, timeout):
            raise HTTPError("https://api.github.com/test", 401, "denied", {}, None)

        result = metrics.fetch_json("https://api.github.com/test", opener=denied)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["http_status"], 401)
        self.assertNotIn("data", result)
        self.assertNotIn("count", metrics.traffic_summary(result, "views"))

    def test_zero_is_a_measured_value(self):
        result = {"status": "ok", "data": {"count": 0, "uniques": 0, "views": []}}
        self.assertEqual(metrics.traffic_summary(result, "views")["count"], 0)

    def test_window_comes_from_data_not_retrieval_clock(self):
        result = {"status": "ok", "data": {"count": 8, "uniques": 8, "views": [
            {"timestamp": "2026-10-06T00:00:00Z", "count": 0, "uniques": 0},
            {"timestamp": "2026-09-23T00:00:00Z", "count": 8, "uniques": 8},
        ]}}
        summary = metrics.traffic_summary(result, "views")
        self.assertEqual(summary["last_day"], "2026-10-06")
        self.assertEqual(summary["first_day"], "2026-09-23")

    def test_zenodo_aggregate_and_version_are_separate(self):
        result = {"status": "ok", "data": {"id": 23146271, "metadata": {
            "version": "2.2.1"}, "stats": {"views": 9, "downloads": 1,
            "version_views": 3, "version_downloads": 0}}}
        summary = metrics.zenodo_summary(result)
        self.assertEqual(summary["all_versions"]["views"], 9)
        self.assertEqual(summary["this_version"]["views"], 3)
        self.assertEqual(summary["this_version"]["downloads"], 0)
        self.assertIsNone(summary["this_version"]["unique_views"])

    def test_missing_fields_are_not_invented(self):
        summary = metrics.traffic_summary({"status": "ok", "data": {}}, "views")
        self.assertIsNone(summary["count"])
        self.assertIsNone(summary["last_day"])

    def test_partial_endpoint_coverage_is_not_complete(self):
        snapshot = {"sources": {"views": {"status": "ok"},
                                 "clones": {"status": "unavailable"}}}
        self.assertFalse(metrics.github_complete(snapshot))
        snapshot["sources"]["clones"]["status"] = "ok"
        self.assertTrue(metrics.github_complete(snapshot))

    def test_auth_is_not_sent_to_non_github_sources(self):
        requests = []

        def capture(request, timeout):
            requests.append(request)
            raise HTTPError(request.full_url, 403, "denied", {}, None)

        result = metrics.fetch_json("https://zenodo.org/api/records/1", "secret", capture)
        self.assertIsNone(requests[0].get_header("Authorization"))
        self.assertNotIn("secret", str(result))
        metrics.fetch_json("https://api.github.com/user", "secret", capture)
        self.assertEqual(requests[1].get_header("Authorization"), "Bearer secret")


if __name__ == "__main__":
    unittest.main()
