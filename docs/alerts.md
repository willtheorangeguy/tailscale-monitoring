# Alerts

`examples/alerts.yml` contains Prometheus rules for failed dependencies, offline
resources, tag drift, disabled SSH, missing route advertisements, unreachable
collectors and stale collection. Add its path to Prometheus `rule_files`, check
configuration, then reload. These rules use the example job name; change their
selectors if you rename the job. Configure your own Alertmanager destination.
Importing the dashboard alone does not install rules or send notifications.

The dashboard's alert table shows firing Prometheus `ALERTS` with
`service="tailscale-monitoring"`. Grafana-managed alert rules do not appear in
that table. Keep the alerting stack independent of the hosts it monitors if you
need notifications during an outage of your Prometheus/Grafana host.

Route metrics report configured advertisements and the selected router visible
to each collector. They do not prove packet forwarding works, validate every
approved route, guarantee seamless failover, or provide exit-node failover.
SSH metrics indicate the enabled flag, not a successful login test.
