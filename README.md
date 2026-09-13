<div align="center">

# recon-forge

**Modular async reconnaissance framework with self-contained HTML reporting.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00FF9C?style=flat-square)
![asyncio](https://img.shields.io/badge/asyncio-concurrent-00D9FF?style=flat-square)
![Dependencies](https://img.shields.io/badge/dependencies-none-00D9FF?style=flat-square)
![tests](https://github.com/anonymoustest137/recon-forge/actions/workflows/tests.yml/badge.svg)

</div>

---

## What is this?

**recon-forge is a reconnaissance tool.** Reconnaissance ("recon") is the first phase of any
authorized security assessment: before you can test whether a company's systems are secure,
you first have to find out *what systems they actually have*.

Most organisations have far more internet-facing infrastructure than they realise — a forgotten
`staging.company.com`, an old `vpn.company.com`, a `dev` box someone spun up two years ago.
Each one is a potential way in, and the ones nobody remembers are usually the ones nobody patches.

recon-forge automates the discovery of that attack surface and hands you a single readable report.

### The problem it solves

Doing this by hand means running three or four separate tools, each with different output
formats, then manually stitching the results together:

```
dig / dnsx        ->  which subdomains exist?
nmap              ->  which ports are open on each?
curl / whatweb    ->  what software is running there?
(manual work)     ->  combine into something a client can read
```

That's slow, and the glue work is error-prone. recon-forge does all four steps in one pass,
concurrently, and outputs a single HTML file you can hand to a client or attach to a ticket.

### Who it's for

- **Penetration testers** mapping a client's external perimeter at the start of an engagement
- **Bug bounty hunters** enumerating a program's in-scope assets
- **Blue teams / IT** auditing their *own* exposure — you can't defend what you don't know exists
- **Students** learning how asynchronous network programming works in Python

---

## How it works

The pipeline has four stages. Every stage is concurrent, which is where the speed comes from.

### Stage 1 — Subdomain enumeration

recon-forge takes a wordlist of common hostname prefixes (`www`, `api`, `dev`, `staging`,
`admin`, `vpn`, …), prepends each to the target domain, and attempts to resolve them all
**at the same time**.

A hostname that resolves to an IP address exists. One that doesn't, doesn't. This is
*passive* — you're only asking DNS servers a question, not touching the target's systems.

```
www.example.com     -> 93.184.216.34    exists
api.example.com     -> 93.184.216.35    exists
notreal.example.com -> NXDOMAIN         skipped
```

Concurrency is bounded by an `asyncio.Semaphore` (default 50) so you don't exhaust file
descriptors or hammer the resolver.

### Stage 2 — Port scanning

For every host discovered, recon-forge attempts a TCP connection to 17 high-signal ports —
the ones that actually matter in an assessment:

| Port | Service | Why it matters |
|---|---|---|
| 21 | FTP | Often anonymous-readable |
| 22 | SSH | Brute-force target, version leaks |
| 25 | SMTP | Open relay, user enumeration |
| 80 | HTTP | The main web surface |
| 110 | POP3 | Legacy mail |
| 143 | IMAP | Legacy mail |
| 443 | HTTPS | The main web surface |
| 445 | SMB | File shares, lateral movement |
| 3306 | MySQL | Exposed databases |
| 3389 | RDP | Remote desktop, ransomware entry |
| 5432 | PostgreSQL | Exposed databases |
| 6379 | Redis | Frequently unauthenticated |
| 8000 | HTTP-alt | Dev servers |
| 8080 | HTTP-alt | Proxies, Tomcat |
| 8443 | HTTPS-alt | Admin panels |
| 9200 | Elasticsearch | Frequently unauthenticated |

Each connection uses a 1.5-second timeout. If the TCP handshake completes, the port is open.
Up to 200 probes run concurrently.

### Stage 3 — HTTP fingerprinting

For any host with a web port open, recon-forge sends a raw `HEAD /` request and parses the
response headers, looking for `Server` and `X-Powered-By`:

```
Server: nginx/1.18.0
X-Powered-By: PHP/7.4.3
```

That tells you the software and version — which you can then cross-reference against known
CVEs. `HEAD` is used rather than `GET` because it returns headers without the response body,
making it faster and quieter.

### Stage 4 — Reporting

Everything is rendered into a single dark-themed HTML file with no external CSS, JS, fonts
or images. One file you can email, archive, or open on a machine with no internet access.

---

## Install

```bash
git clone https://github.com/anonymoustest137/recon-forge.git
cd recon-forge
pip install -r requirements.txt   # only pytest, for the test suite
```

There are **no runtime dependencies** — recon-forge uses nothing outside the Python
standard library. `pip install` is only needed if you want to run the tests.

---

## Usage

```bash
# scan a domain you are authorized to test
python -m reconforge.cli example.com

# custom output file and higher concurrency
python -m reconforge.cli example.com -o scan.html -c 100
```

### Options

| Flag | Default | Description |
|---|---|---|
| `domain` | *required* | Target domain (must be authorized) |
| `-o`, `--out` | `report.html` | Output HTML path |
| `-c`, `--concurrency` | `50` | Max simultaneous DNS lookups |
| `--version` | | Print version and exit |

### Example session

```
$ python -m reconforge.cli example.com

recon-forge v0.1.0 - authorized testing only
[*] enumerating subdomains for example.com
[+] 3 live host(s)
    www.example.com -> 93.184.216.34 [80, 443]
    api.example.com -> 93.184.216.35 [443, 8443]
    dev.example.com -> 93.184.216.36 [22, 80, 3306]
[+] report written to report.html
```

That `dev` box with MySQL on 3306 and SSH open is exactly the kind of finding this tool exists to surface.

---

## Project structure

| Path | Purpose |
|---|---|
| `reconforge/modules.py` | DNS resolution, port scanning, HTTP fingerprinting |
| `reconforge/report.py` | HTML report renderer |
| `reconforge/cli.py` | Command line entry point |
| `tests/test_recon.py` | pytest suite |

### Using it as a library

```python
import asyncio
from reconforge.modules import enumerate_subdomains, scan_ports
from reconforge.report import write

async def main():
    hosts = await enumerate_subdomains("example.com")
    for h in hosts:
        h.ports = await scan_ports(h.ip)
    write("out.html", "example.com", hosts)

asyncio.run(main())
```

---

## Tests

```bash
pytest -q
```

CI runs the suite against Python 3.10 and 3.12 on every push.

---

## Legal & ethical use

**Only scan systems you own or have explicit written permission to test.**

Port scanning without authorization is illegal in many jurisdictions — including under the
Computer Fraud and Abuse Act (US), the Computer Misuse Act (UK), and equivalent legislation
elsewhere. Bug bounty programs define scope precisely; stay inside it.

This tool is deliberately *loud* and makes no attempt at evasion. It is built for authorized
assessment work, not for stealth.

---

## Roadmap

- [ ] Certificate transparency log ingestion for passive subdomain discovery
- [ ] Custom wordlist support via `-w`
- [ ] JSON output alongside HTML
- [ ] Service banner grabbing beyond HTTP
- [ ] Rate limiting per target

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built by [@anonymoustest137](https://github.com/anonymoustest137) · [Portfolio](https://anonymoustest137.github.io/anonymoustest137/)

 *For educational and authorized testing purposes only.*

</div>
