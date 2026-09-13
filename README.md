<div align="center">

# 🔎 recon-forge

**Modular async reconnaissance framework with HTML reporting.**

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white) ![MIT](https://img.shields.io/badge/License-MIT-00FF9C?style=flat-square) ![asyncio](https://img.shields.io/badge/asyncio-concurrent-00D9FF?style=flat-square)

![tests](https://github.com/anonymoustest137/recon-forge/actions/workflows/tests.yml/badge.svg)

</div>

---

## Overview

recon-forge runs subdomain enumeration, port scanning and HTTP fingerprinting concurrently, then renders everything into a single self-contained HTML report. Built on asyncio with bounded concurrency so it stays fast without flooding the target.

## Features

- **Async subdomain enumeration** with a configurable wordlist and semaphore-bounded concurrency
- **Port scanning** across a curated set of 17 high-signal ports
- **HTTP fingerprinting** that extracts `Server` and `X-Powered-By` headers
- **Self-contained HTML reports** with a dark theme and no external assets
- **Zero third-party dependencies** — standard library only

## Install

```bash
git clone https://github.com/anonymoustest137/recon-forge.git
cd recon-forge
pip install -r requirements.txt   # only pytest, for the test suite
```

## Usage

```bash
# scan a domain you are authorized to test
python -m reconforge.cli example.com

# custom output and concurrency
python -m reconforge.cli example.com -o scan.html -c 100
```

## Project structure

| Path | Purpose |
|---|---|
| `reconforge/modules.py` | DNS resolution, port scanning, fingerprinting |
| `reconforge/report.py` | HTML report renderer |
| `reconforge/cli.py` | command line entry point |
| `tests/` | pytest suite |

## How it works

1. **Resolve** — each candidate subdomain is resolved concurrently via `loop.getaddrinfo`, with a semaphore capping in-flight lookups.
2. **Scan** — every live host is port-scanned using `asyncio.open_connection` with a 1.5 s timeout per port.
3. **Fingerprint** — a raw `HEAD /` request is issued and response headers parsed.
4. **Report** — results are rendered to standalone HTML.

## Tests

```bash
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built by [@anonymoustest137](https://github.com/anonymoustest137) · [Portfolio](https://anonymoustest137.github.io/anonymoustest137/)

⚠️ *For educational and authorized testing purposes only.*

</div>