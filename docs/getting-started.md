# Getting started

On a collector host, copy the sample configuration and change `host` to a unique
label. Replace the example HTTPS/DNS checks with your own services:

```sh
cp examples/config.json config.json
python3 src/tailscale_monitor.py --config config.json --once
python3 src/tailscale_monitor.py --config config.json
```

The sample listens only on `127.0.0.1:9487`. Check it from the same host:

```sh
curl http://127.0.0.1:9487/metrics
```

For Prometheus on another host, set `bind` to this host's reachable LAN or
Tailscale address and add the actual Prometheus source IP to `allowed_clients`.
Keep a restrictive client allowlist and network access policy: the HTTP endpoint
has no TLS or login of its own. Its `/metrics` and `/health` endpoints accept
no commands or configuration changes. Health indicates the HTTP process is up;
collector freshness is monitored separately.

Merge `examples/prometheus-scrape.yml` into your existing Prometheus configuration,
adjust the target address, validate it with `promtool check config`, and reload.
Do not replace unrelated scrape jobs. The job name defaults to
`tailscale-monitoring`.

In Grafana, choose **Dashboards → New → Import**, upload
`dashboards/tailscale-overview.json`, and choose your Prometheus
datasource from the dashboard dropdown. There is no fixed datasource UID.
[Grafana variables](https://grafana.com/docs/grafana/latest/visualizations/dashboards/variables/)
let you change these controls without editing panel queries:

| Control | Value to enter |
| --- | --- |
| Scrape job | Your collector Prometheus job name |
| Expected checks | Total configured checks across all collector hosts |
| Expected resources | Number of distinct entries in the monitored node baselines |
| Expected SSH hosts | Number of collectors where SSH monitoring is enabled |
| Expected routers | Number of collectors with a configured `subnet_route` |
| Expected collectors | Number of configured Prometheus scrape targets |

Use non-negative integers for totals. A zero expected total disables its
summary rather than dividing by zero. The sample defaults to two checks, one
SSH host and one collector; resource and router summaries start disabled.
Counts are independent of currently available metrics so missing metrics cannot
silently lower the expected total. Resource summaries deduplicate nodes observed
by multiple collectors. Give each collector a distinct `host` label.
