"""Local dependency probes and Tailscale status metrics; no API credentials needed."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import struct
import subprocess
import threading
import time
import urllib.request


def command(argv, timeout=35):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=True)
    return result.stdout


def http_check(check):
    body = check.get("body")
    request = urllib.request.Request(check["url"],
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"} if body is not None else {})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=check.get("timeout", 10)) as response:
        data = response.read(2_000_000)
        if response.status != 200:
            return False
        if check.get("json_key"):
            value = json.loads(data)
            for key in check["json_key"].split("."):
                value = value[key]
            return value == check["equals"] if "equals" in check else bool(value)
        return True


def dns_check(check):
    identifier = int(time.time_ns()) & 65535
    question = b"".join(bytes([len(part)]) + part.encode() for part in check["name"].split("."))
    packet = struct.pack("!HHHHHH", identifier, 0x0100, 1, 0, 0, 0) + question + b"\0\0\1\0\1"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)
        sock.connect((check["server"], 53))
        sock.send(packet)
        answer = sock.recv(4096)
    ident, flags, _, count, _, _ = struct.unpack("!HHHHHH", answer[:12])
    return ident == identifier and flags & 0xF == 0 and count > 0 and socket.inet_aton(check["address"]) in answer


def escape(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def metric(name, value, **labels):
    suffix = "{" + ",".join(f'{key}="{escape(item)}"' for key, item in sorted(labels.items())) + "}" if labels else ""
    return f"{name}{suffix} {value}\n"


class Monitor:
    def __init__(self, config):
        self.config = config
        self.results = {}
        self.lock = threading.Lock()
        self.metrics = "homelab_monitor_last_run_timestamp_seconds 0\n"

    def probe(self, check):
        started = time.monotonic()
        try:
            if check["type"] == "dns":
                passed = bool(socket.getaddrinfo(check["name"], check.get("port", 443)))
            elif check["type"] == "dns_server":
                passed = dns_check(check)
            elif check["type"] == "http":
                passed = http_check(check)
            else:
                raise ValueError("Unsupported check type")
            error = "" if passed else "UnexpectedResponse"
        except Exception as exc:
            # Never expose HTTP bodies, auth data, or guest output in metrics/logs.
            passed, error = False, type(exc).__name__
        return check["id"], {"up": int(passed), "duration": time.monotonic() - started,
                             "checked": time.time(), "error": error}

    def collect(self):
        now = time.time()
        checks = [check for check in self.config.get("checks", [])
                  if now - self.results.get(check["id"], {}).get("checked", 0) >= check.get("period", 60)]
        with ThreadPoolExecutor(max_workers=5) as executor:
            for key, result in executor.map(self.probe, checks):
                self.results[key] = result
        host = self.config["host"]
        text = metric("homelab_monitor_last_run_timestamp_seconds", time.time(), host=host)
        for key, result in self.results.items():
            labels = {"host": host, "check": key}
            text += metric("homelab_dependency_up", result["up"], **labels)
            text += metric("homelab_dependency_duration_seconds", result["duration"], **labels)
            text += metric("homelab_dependency_last_checked_timestamp_seconds", result["checked"], **labels)
            if result["error"]:
                text += metric("homelab_dependency_error", 1, error=result["error"], **labels)
        try:
            status_text = ""
            status = json.loads(command(["tailscale", "status", "--json"], timeout=10))
            prefs = json.loads(command(["tailscale", "debug", "prefs"], timeout=10))
            status_text += metric("homelab_tailscale_running", int(status.get("BackendState") == "Running"), host=host)
            if self.config.get("monitor_ssh", True):
                status_text += metric("homelab_tailscale_ssh_enabled", int(bool(prefs.get("RunSSH"))), host=host)
            route = self.config.get("subnet_route")
            if route:
                status_text += metric("homelab_subnet_route_advertised", int(route in (prefs.get("AdvertiseRoutes") or [])), host=host, route=route)
            peers = {peer["DNSName"].rstrip("."): peer for peer in status.get("Peer", {}).values()}
            status["Self"]["Online"] = status.get("BackendState") == "Running"
            peers[status["Self"]["DNSName"].rstrip(".")] = status["Self"]
            for name, expected_tags in self.config.get("nodes", {}).items():
                peer = peers.get(name, {})
                status_text += metric("homelab_tailnet_node_online", int(bool(peer.get("Online"))), host=host, node=name)
                status_text += metric("homelab_tailnet_tags_match", int(sorted(peer.get("Tags") or []) == sorted(expected_tags)), host=host, node=name)
                if peer.get("KeyExpiry"):
                    expiry = datetime.datetime.fromisoformat(peer["KeyExpiry"].replace("Z", "+00:00"))
                    status_text += metric("homelab_tailnet_key_expiry_timestamp_seconds", expiry.timestamp(), host=host, node=name)
            for peer in peers.values():
                for route in peer.get("PrimaryRoutes") or []:
                    status_text += metric("homelab_subnet_primary_route", 1, host=host, node=peer["DNSName"].rstrip("."), route=route)
            text += status_text
        except Exception as exc:
            text += metric("homelab_tailscale_running", 0, host=host)
            text += metric("homelab_tailscale_status_error", 1, host=host, error=type(exc).__name__)
        state = Path(self.config["state_directory"])
        state.mkdir(parents=True, exist_ok=True)
        temporary = state / "metrics.prom.tmp"
        temporary.write_text(text)
        temporary.replace(state / "metrics.prom")
        with self.lock:
            self.metrics = text

    def loop(self):
        while True:
            try:
                self.collect()
            except Exception as exc:
                print("Collector failure:", type(exc).__name__, flush=True)
            time.sleep(self.config.get("poll_interval", 30))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    checks = config.get("checks", [])
    if len({check["id"] for check in checks}) != len(checks):
        parser.error("Check IDs must be unique within a collector")
    if any(check["type"] not in {"http", "dns", "dns_server"} for check in checks):
        parser.error("Supported check types: http, dns, dns_server")
    if config.get("poll_interval", 30) < 1 or any(check.get("period", 60) < 1 for check in checks):
        parser.error("Poll and check intervals must be positive")
    monitor = Monitor(config)
    if args.once:
        monitor.collect()
        print(monitor.metrics, end="")
        return

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.client_address[0] not in config["allowed_clients"]:
                self.send_error(403)
                return
            if self.path not in ("/metrics", "/health"):
                self.send_error(404)
                return
            with monitor.lock:
                body = monitor.metrics.encode() if self.path == "/metrics" else b"OK\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    threading.Thread(target=monitor.loop, daemon=True).start()
    ThreadingHTTPServer((config["bind"], config["port"]), Handler).serve_forever()


if __name__ == "__main__":
    main()
