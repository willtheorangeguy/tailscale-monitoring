# Dashboard usage

Import `dashboards/tailscale-overview.json` through **Dashboards → New → Import**, then choose your Prometheus datasource.

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
