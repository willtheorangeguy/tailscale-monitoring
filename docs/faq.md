# FAQ

???+ question "Does this need a Tailscale API key or paid plan?"
    No. The collector reads the local client's status and preferences. Its
    optional SSH and router observations use existing client configuration.
    It does not create users, tags, keys or approved routes.

??? question "Can I use native Tailscale metrics instead of the collector?"
    Not with this dashboard unchanged. Its `homelab_*` metric names come from
    the included collector. These are not native Tailscale metric names.

??? question "Why do some summaries start without data?"
    The example has no node baseline or expected subnet route. Their expected
    totals default to zero, which disables those summaries. Add your own
    baselines and route, then set the corresponding totals.

??? question "Does a green SSH card mean a login was tested?"
    No. It means `RunSSH` is enabled on the monitored collectors. Policy,
    identity checks and operating-system users still determine login access.

??? question "Can I publish this without sharing my home network?"
    The supplied examples use placeholders and loopback addresses. Keep your
    live `config.json`, state files and screenshots private or sanitize them.
    Copy this folder's contents into a separate repository rather than copying
    a containing homelab repository's Git history.
