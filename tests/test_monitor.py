import importlib.util
import json
from pathlib import Path
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("monitor", ROOT / "src/tailscale_monitor.py")
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.config = {"host": "test-host", "state_directory": self.directory.name,
                       "checks": [], "nodes": {"missing.example.ts.net": ["tag:server"]},
                       "subnet_route": "10.20.0.0/16"}

    def response(self, argv, timeout=35):
        if argv[1] == "status":
            return json.dumps({"BackendState": "Running", "Self": {
                "DNSName": "test.example.ts.net.", "Tags": []}, "Peer": {}})
        return json.dumps({"RunSSH": True, "AdvertiseRoutes": ["10.20.0.0/16"]})

    def test_missing_expected_node_is_failed_not_omitted(self):
        collector = monitor.Monitor(self.config)
        with patch.object(monitor, "command", self.response):
            collector.collect()
        self.assertIn('homelab_tailnet_node_online{host="test-host",node="missing.example.ts.net"} 0', collector.metrics)
        self.assertIn('homelab_tailnet_tags_match{host="test-host",node="missing.example.ts.net"} 0', collector.metrics)

    def test_configurable_route_and_optional_ssh(self):
        self.config["monitor_ssh"] = False
        collector = monitor.Monitor(self.config)
        with patch.object(monitor, "command", self.response):
            collector.collect()
        self.assertIn('homelab_subnet_route_advertised{host="test-host",route="10.20.0.0/16"} 1', collector.metrics)
        self.assertNotIn("homelab_tailscale_ssh_enabled", collector.metrics)
        self.assertEqual((Path(self.directory.name) / "metrics.prom").read_text(), collector.metrics)

    def test_daemon_failure_preserves_dependency_results(self):
        self.config["checks"] = [{"id": "dns", "type": "dns", "name": "example.com"}]
        collector = monitor.Monitor(self.config)
        with patch.object(monitor.socket, "getaddrinfo", return_value=[("resolved",)]), \
                patch.object(monitor, "command", side_effect=PermissionError("private detail")):
            collector.collect()
        self.assertIn('homelab_dependency_up{check="dns",host="test-host"} 1', collector.metrics)
        self.assertIn('homelab_tailscale_running{host="test-host"} 0', collector.metrics)
        self.assertNotIn("private detail", collector.metrics)

    def test_probe_errors_do_not_expose_response_details(self):
        collector = monitor.Monitor(self.config)
        with patch.object(monitor, "http_check", side_effect=ValueError("private response")):
            _, result = collector.probe({"id": "api", "type": "http"})
        self.assertEqual(result["up"], 0)
        self.assertEqual(result["error"], "ValueError")
        self.assertNotIn("private response", json.dumps(result))

    def test_unknown_probe_is_not_treated_as_http(self):
        _, result = monitor.Monitor(self.config).probe({"id": "bad", "type": "unknown"})
        self.assertEqual(result["up"], 0)
        self.assertEqual(result["error"], "ValueError")

    def test_http_checks_validate_nested_json_and_false_values(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = b'{"health":{"ok":false}}'
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            check = {"url": f"http://127.0.0.1:{server.server_port}/",
                     "json_key": "health.ok", "equals": False}
            self.assertTrue(monitor.http_check(check))
            check["equals"] = True
            self.assertFalse(monitor.http_check(check))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_bad_peer_metadata_does_not_duplicate_running_metric(self):
        def malformed(argv, timeout=35):
            if argv[1] != "status":
                return self.response(argv, timeout)
            status = json.loads(self.response(argv, timeout))
            status["Self"]["KeyExpiry"] = "invalid timestamp"
            self.config["nodes"]["test.example.ts.net"] = []
            return json.dumps(status)

        collector = monitor.Monitor(self.config)
        with patch.object(monitor, "command", malformed):
            collector.collect()
        samples = [line for line in collector.metrics.splitlines()
                   if line.startswith("homelab_tailscale_running{")]
        self.assertEqual(samples, ['homelab_tailscale_running{host="test-host"} 0'])


class DashboardTests(unittest.TestCase):
    def test_datasources_and_summary_totals_are_portable(self):
        dashboard = json.loads((ROOT / "dashboards/tailscale-overview.json").read_text())
        self.assertEqual(len(dashboard["panels"]), 15)
        variables = {v["name"] for v in dashboard["templating"]["list"]}
        for panel in dashboard["panels"]:
            self.assertEqual(panel["datasource"]["uid"], "${datasource}")
            for target in panel["targets"]:
                import re
                used = re.findall(r"\$\{(\w+)\}", target["expr"])
                self.assertTrue(set(used).issubset(variables))
        for panel in dashboard["panels"][:5]:
            self.assertIn("${expected_", panel["targets"][0]["expr"])


if __name__ == "__main__":
    unittest.main()
