# Testing

Run the standard-library test suite from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q src
```

Tests mock Tailscale commands and network resolution. They check missing node
handling, configurable routes, optional SSH monitoring, daemon failures,
sanitized probe errors, unsupported check types and dashboard portability.
They do not connect to a real tailnet or perform router outage drills.

## Integration checks

On a configured collector host:

```sh
python3 src/tailscale_monitor.py --config examples/config.json --once
```

Check its metrics endpoint, then confirm its target is up in Prometheus. Set
dashboard totals to your deployment and inspect dependency failures before
relying on summary colors.
