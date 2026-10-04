# Installation

## Requirements

- Linux host with a running, authenticated Tailscale client and Python 3.10+.
- Prometheus and Grafana with a Prometheus datasource. The dashboard uses built-in
  panels and classic dashboard JSON with schema version 39.
- Local permission to run `tailscale status --json` and `tailscale debug prefs`.
  The example systemd service runs as root for local daemon access; a restricted
  service account is also possible if your daemon permissions permit these calls.

This project exports its own `homelab_*` metrics for compatibility with the
original dashboard. **Native Tailscale metrics or node_exporter alone will not
populate this dashboard.** Proxmox is not required. The collector uses Python's
standard library, without pip dependencies.

## Run at boot

From the repository root on Linux:

```sh
sudo install -d /opt/tailscale-monitoring /etc/tailscale-monitoring
sudo install -m 0644 src/tailscale_monitor.py /opt/tailscale-monitoring/tailscale_monitor.py
sudo install -m 0600 config.json /etc/tailscale-monitoring/config.json
sudo install -m 0644 examples/tailscale-monitoring.service /etc/systemd/system/tailscale-monitoring.service
sudo systemctl daemon-reload
sudo systemctl enable --now tailscale-monitoring
sudo systemctl status tailscale-monitoring
```

The unit's working directory is its persistent `/var/lib/tailscale-monitoring`
state directory. The sample `./state` path therefore works there. The service
keeps operating when a temporary Tailscale admin API token expires because it
does not use one.
