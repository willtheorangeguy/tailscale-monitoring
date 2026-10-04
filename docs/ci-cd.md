# CI/CD

<!-- markdownlint-disable MD046 -->

The repository provides tests, secret scanning and documentation workflows.
They become active when this folder is published as its own GitHub repository.

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `testing.yml` | Push and pull request | Test collector and dashboard on Python 3.10 and 3.12 |
| `gitleaks.yml` | Push, pull request, manual | Scan Git history for exposed secrets |
| `docs.yml` | Documentation push, manual | Build and deploy the shared MkDocs site |
| `docs-lint.yml` | Documentation pull request, manual | Shared Markdown, strict build and link checks |

## Documentation deployment

The site inherits the local configuration from the public
[MkDocs template](https://github.com/willtheorangeguy/mkdocs). Enable GitHub Pages
with **GitHub Actions** as the source after creating the repository. Site and
repository URLs in `mkdocs.yml` target `willtheorangeguy/tailscale-monitoring`;
change them when publishing under a different owner or name.

The caller workflows obtain the shared configuration and design system during
CI. A plain local `mkdocs build` also needs those files staged. With the template
repository cloned alongside this repository, run its preview helper from this
repository's root:

=== "Windows"

    ```powershell
    ../mkdocs/scripts/docs-serve.ps1 -Build
    ```

=== "Linux / macOS"

    ```sh
    ../mkdocs/scripts/docs-serve.sh --build
    ```

## Collector tests

The testing workflow runs the same command as a local test:

```sh
python3 -m unittest discover -s tests -v
```
