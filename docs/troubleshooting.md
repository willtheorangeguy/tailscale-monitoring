# Troubleshooting

## Dashboard shows no data

Select your Prometheus datasource, set the scrape job, and confirm the collector
target is up. These queries help distinguish scrape failures from missing
collector metrics:

```promql
up{job="tailscale-monitoring"}
homelab_monitor_last_run_timestamp_seconds{job="tailscale-monitoring"}
```

Native Tailscale metrics or node_exporter alone do not provide this project's
custom metrics. A zero expected total intentionally disables a summary.

## Metrics endpoint returns 403

Add Prometheus's actual connection source IP to `allowed_clients` and restart
the collector. Reverse-proxy headers are not trusted. Binding to a LAN address
does not automatically allow LAN clients.

```sh
curl http://127.0.0.1:9487/metrics
```

Use this request on a host with the example's loopback binding. For a custom
binding, query its configured address.

## Tailscale status reports an error

Run the two read-only commands as the service account to check daemon access:

```sh
tailscale status --json
tailscale debug prefs
```

Check the service PATH and local daemon permissions. The example systemd unit
runs as root for local client access. No API token resolves a local socket or
permission error.

## Expected node is offline or has a tag mismatch

Use the exact MagicDNS name without a trailing dot in `nodes`. Match its full
tag set. A node hidden by tailnet policy appears absent to this collector, even
if it is online for another user's identity.

## Optional alert table is empty

The table shows firing Prometheus alerts labeled `service="tailscale-monitoring"`.
Load `examples/alerts.yml` through Prometheus `rule_files` and configure your
notification destination separately. Grafana-managed alerts do not populate
the Prometheus `ALERTS` metric.
