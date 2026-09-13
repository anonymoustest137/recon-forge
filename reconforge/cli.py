"""recon-forge command line interface."""
import argparse
import asyncio

from . import __version__
from .modules import enumerate_subdomains, scan_ports, fingerprint
from .report import write as write_report


async def run(domain, out, concurrency):
    print("recon-forge v" + __version__ + " - authorized testing only")
    print("[*] enumerating subdomains for " + domain)
    hosts = await enumerate_subdomains(domain, concurrency=concurrency)
    print("[+] " + str(len(hosts)) + " live host(s)")

    for h in hosts:
        h.ports = await scan_ports(h.ip)
        if 80 in h.ports:
            h.tech = await fingerprint(h.ip, 80)
        elif 443 in h.ports:
            h.tech = await fingerprint(h.ip, 443, tls=True)
        print("    " + h.name + " -> " + str(h.ip) + " " + str(h.ports))

    write_report(out, domain, hosts)
    print("[+] report written to " + out)
    return hosts


def main():
    ap = argparse.ArgumentParser(prog="recon-forge", description="Async recon framework")
    ap.add_argument("domain", help="target domain (must be authorized)")
    ap.add_argument("-o", "--out", default="report.html", help="output HTML file")
    ap.add_argument("-c", "--concurrency", type=int, default=50)
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args()
    asyncio.run(run(args.domain, args.out, args.concurrency))


if __name__ == "__main__":
    main()
