# Tailscale Monitoring

A Tailscale status and dependency collector with a configurable Grafana dashboard.
The collector reads the local Tailscale daemon and probes configured HTTP/DNS
dependencies. Prometheus stores the metrics; Grafana displays their status.

## Key features

- Two gauges and four colored status cards with configurable expected totals.
- SSH flags, advertised routes, selected routers, node availability and tag drift.
- HTTP and DNS dependency checks, with latency and collector freshness.
- No Tailscale admin API token, pip dependency or Proxmox requirement.

## Quick start

Run from the repository root on a Linux Tailscale host:

```sh
cp examples/config.json config.json
python3 src/tailscale_monitor.py --config config.json --once
```

Follow [Getting started](getting-started.md) to run the HTTP collector, configure
Prometheus and import the dashboard.

## Where to next

<div class="wt-grid" markdown>

[:material-rocket-launch: **Getting started**<br>Collect and display metrics](getting-started.md){ .wt-card }

[:material-download: **Installation**<br>Run the collector at boot](installation.md){ .wt-card }

[:material-tune: **Configuration**<br>Set routes, resources and checks](configuration.md){ .wt-card }

[:material-sitemap: **Architecture**<br>Follow the monitoring data flow](architecture.md){ .wt-card }

[:material-view-dashboard: **Dashboard usage**<br>Configure summary totals](usage.md){ .wt-card }

</div>

## Support

{{ support() }}
