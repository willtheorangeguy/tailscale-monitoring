<h1 align="center">tailscale-monitoring</h1>
<h4 align="center">A Tailscale status and dependency collector with a configurable Grafana dashboard.</h4>

<div align="center">
  <img alt="GitHub Issues" src="https://img.shields.io/github/issues/willtheorangeguy/tailscale-monitoring">
  <img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/willtheorangeguy/tailscale-monitoring">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="gitleaks workflow" src="https://github.com/willtheorangeguy/tailscale-monitoring/actions/workflows/gitleaks.yml/badge.svg">
  <img alt="testing workflow" src="https://github.com/willtheorangeguy/tailscale-monitoring/actions/workflows/testing.yml/badge.svg">
</div>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support">Support</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

A Tailscale status and dependency collector with a configurable Grafana dashboard.
Uses local Tailscale client commands, Prometheus, and Grafana. No Tailscale admin
API token or paid Tailscale feature is required.

## Key Features

- Six colored summary panels for dependencies, resources, SSH, routers, collectors, and freshness.
- Detailed node availability, tag baseline, route, and probe latency views.
- Configurable datasource, scrape job, and expected totals for different networks.
- Portable Python collector with HTTP and DNS checks, without pip dependencies.
- Example systemd service, Prometheus scrape configuration, and optional alert rules.

## Installation

Requires a Linux Tailscale client, Python 3.10+, Prometheus, and Grafana. The
included collector exports the custom metrics required by the dashboard.
Native Tailscale metrics or node_exporter alone cannot populate its panels.

```sh
cp examples/config.json config.json
python3 src/tailscale_monitor.py --config config.json --once
python3 src/tailscale_monitor.py --config config.json
```

Edit the configuration for your hosts and dependencies. Merge
[examples/prometheus-scrape.yml](examples/prometheus-scrape.yml) into your
Prometheus configuration. The example binds to localhost; see
[installation](docs/installation.md) for remote scraping and startup at boot.

## Usage

Import [tailscale-overview.json](dashboards/tailscale-overview.json) through
**Dashboards → New → Import**. Select your Prometheus datasource and set the
scrape job and expected totals. See [dashboard usage](docs/usage.md).

## Documentation

Documentation lives in [docs/](docs/index.md): [Quickstart](docs/getting-started.md) ·
[Configuration](docs/configuration.md) · [Architecture](docs/architecture.md) ·
[Dashboard usage](docs/usage.md) · [Troubleshooting](docs/troubleshooting.md).
The MkDocs site uses the shared [documentation template](https://github.com/willtheorangeguy/mkdocs).

## Support

File an [issue](https://github.com/willtheorangeguy/tailscale-monitoring/issues/new/choose).

## Contributing

Contributions welcome. See the shared [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md)
and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).
Run `python3 -m unittest discover -s tests -v` before submitting a change.

## License

MIT — see [LICENSE.md](LICENSE.md). This is an independent community project.
