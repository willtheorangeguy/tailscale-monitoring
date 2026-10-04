# Development

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q src
```

This folder is self-contained: copy its contents into a separate repository.
Local `config.json`, state snapshots and Python caches are ignored. Review your
own additions before publishing; node names and metrics labels can reveal
infrastructure details. The dashboard and collector are MIT licensed and are
an independent community project, not an official Tailscale integration.
