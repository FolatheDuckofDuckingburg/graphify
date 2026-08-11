Title: chore: upgrade pypdf to >=6.14.2 to mitigate parsing DoS CVEs

This PR updates the optional `pdf` extras and the `all` extras list to require `pypdf>=6.14.2`.

Motivation
- Several CVEs and security advisories have been published against older `pypdf` releases describing infinite-loop and resource-exhaustion (DoS) parsing issues. Upgrading to `pypdf>=6.14.2` pulls in fixes for these vulnerabilities.

What changed
- `pyproject.toml` (optional extras): `pypdf>=6.12.0` → `pypdf>=6.14.2`
- `pyproject.toml` (all extras list): updated the `pypdf` entry to `>=6.14.2`

Testing
- Please run the repo unit tests and `pip-audit` in CI; the bump is scoped to optional extras and should not affect default installs, but CI will validate compatibility.

References
- pypdf security advisories: https://github.com/py-pdf/pypdf/security/advisories
- Representative CVEs: CVE-2025-55197, CVE-2026-54651
