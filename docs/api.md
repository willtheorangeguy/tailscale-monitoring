# API

The collector exposes read-only HTTP endpoints and a command-line entry point.
Requests cannot change configuration or run probes on demand.

## Command line

```sh
python3 src/tailscale_monitor.py --config examples/config.json --once
```

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--config` | path | Required | JSON configuration file |
| `--once` | flag | Off | Collect once, print metrics and exit |
| `--help` | flag | Off | Print command usage and exit |

## GET /metrics

Returns the latest Prometheus text snapshot. No query parameters or request
body are used. A collection cycle must complete before the full snapshot appears.

```sh
curl http://127.0.0.1:9487/metrics
```

```text
homelab_tailscale_running{host="server-1"} 1
homelab_tailscale_ssh_enabled{host="server-1"} 1
```

Metric values reflect the actual host; the two lines above illustrate a running
daemon with Tailscale SSH enabled.

| Status | Meaning |
| --- | --- |
| 200 | Prometheus text snapshot |
| 403 | Client IP is absent from `allowed_clients` |

## GET /health

Returns process-level HTTP health, without guaranteeing freshness or passing
dependency checks. No parameters or request body are used.

```sh
curl http://127.0.0.1:9487/health
```

```text
OK
```

Allowed clients receive 200. Other clients receive 403. An allowed client
requesting an unknown path receives 404. Unsupported HTTP methods receive 501.

## Metrics

All metrics are gauges. Prometheus adds `job` and `instance` labels when scraping.

| Metric | Labels | Meaning |
| --- | --- | --- |
| `homelab_monitor_last_run_timestamp_seconds` | host | Last completed cycle, Unix seconds |
| `homelab_dependency_up` | host, check | 1 when the last probe passes; otherwise 0 |
| `homelab_dependency_duration_seconds` | host, check | Last probe duration |
| `homelab_dependency_last_checked_timestamp_seconds` | host, check | Last probe completion time |
| `homelab_dependency_error` | host, check, error | 1 for failed probes; class name only |
| `homelab_tailscale_running` | host | 1 for a running local daemon |
| `homelab_tailscale_ssh_enabled` | host | SSH enabled flag; optional |
| `homelab_subnet_route_advertised` | host, route | Configured route advertisement flag; optional |
| `homelab_tailnet_node_online` | host, node | Expected node visible and online |
| `homelab_tailnet_tags_match` | host, node | Node tags match the complete expected set |
| `homelab_tailnet_key_expiry_timestamp_seconds` | host, node | Key expiry, when supplied by the client |
| `homelab_subnet_primary_route` | host, node, route | Selected router visible to this collector |
| `homelab_tailscale_status_error` | host, error | 1 when local status collection fails |
