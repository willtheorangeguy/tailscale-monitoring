# Configuration

The required `--config` file provides settings. There are no environment-variable
overrides. Values explicitly present in JSON override the code defaults listed
below. `examples/config.json` contacts `example.com` for two demonstration checks.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `host` | string | Required | Unique collector label, for example `server-1` |
| `bind` | string | Required | Listen address, for example `127.0.0.1` |
| `port` | integer | Required | Listen port, for example `9487` |
| `allowed_clients` | string array | Required | Exact source IPs, for example `["127.0.0.1"]`; no CIDR ranges |
| `state_directory` | string | Required | Writable snapshot directory, for example `./state` |
| `poll_interval` | number | `30` | Scheduler seconds; must be at least 1 |
| `monitor_ssh` | boolean | `true` | Report the local SSH enabled flag |
| `subnet_route` | string or null | `null` | Expected prefix such as `10.0.0.0/24`; null omits the metric |
| `nodes` | object | `{}` | Exact MagicDNS names mapped to complete expected tag lists |
| `checks` | object array | `[]` | HTTP, system DNS, or explicit DNS-server probes |

Duplicate check IDs, unsupported check types and non-positive intervals cause
startup to fail. Missing required fields or malformed JSON also cause startup
errors. A failing probe produces a zero status and sanitized error metric.

Example node baseline and optional subnet expectation; replace these placeholders
with names, tags and routes from your own network:

```json title="Node and route configuration"
{
  "subnet_route": "10.0.0.0/24",
  "nodes": {
    "server.your-tailnet.ts.net": ["tag:server"]
  }
}
```

Node status reflects the collector's accessible Tailscale network map, which
your access policy may restrict. A configured node absent from that map is
reported offline with a tag mismatch. This is not an admin-API inventory of
every tailnet device. For user-owned devices, the expected tag list is `[]`.

Each check requires a unique `id` on its collector and supports `period`
(default 60 seconds). Supported types:

```json title="Check configuration"
[
  {"id": "web", "type": "http", "url": "https://example.com/", "timeout": 10},
  {"id": "api", "type": "http", "url": "https://example.com/health", "json_key": "status", "equals": "ok"},
  {"id": "dns", "type": "dns", "name": "example.com"},
  {"id": "internal_dns", "type": "dns_server", "server": "10.0.0.53", "name": "app.example.com", "address": "10.0.0.10"}
]
```

HTTP requires a final 200 response, validates TLS, and bypasses system HTTP
proxies. `json_key` selects a dotted JSON path; without `equals`, its value must
be truthy. An optional `body` sends a JSON POST. Do not embed secrets in shared
example files. Errors expose only exception classes, not response bodies.
System DNS checks resolution through the host resolver. Explicit DNS checks
send an IPv4 A-record query over UDP and verify the expected IPv4 address; they
are lightweight reachability checks, not a comprehensive DNS validator.

Run collectors on the hosts where a dependency matters. A successful probe from
one host does not prove another application's container can reach that service.
The portable collector does not execute guest/container commands or perform
router outage drills, and does not enable SSH or approve routes.
