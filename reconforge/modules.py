"""Recon modules: DNS brute force, port scanning, HTTP fingerprinting."""
from __future__ import annotations
import asyncio, socket, ssl
from dataclasses import dataclass, field

DEFAULT_PORTS = [21,22,25,53,80,110,143,443,445,3306,3389,5432,6379,8000,8080,8443,9200]
DEFAULT_WORDS = ["www","mail","dev","staging","api","admin","test","vpn","git","portal","cdn","app"]


@dataclass
class Host:
    name: str
    ip: str | None = None
    ports: list[int] = field(default_factory=list)
    tech: dict = field(default_factory=dict)


async def resolve(name: str) -> str | None:
    loop = asyncio.get_running_loop()
    try:
        info = await loop.getaddrinfo(name, None, family=socket.AF_INET)
        return info[0][4][0]
    except (socket.gaierror, OSError):
        return None


async def enumerate_subdomains(domain: str, words=None, concurrency: int = 50) -> list[Host]:
    words = words or DEFAULT_WORDS
    sem = asyncio.Semaphore(concurrency)

    async def probe(w: str) -> Host | None:
        fqdn = f"{w}.{domain}"
        async with sem:
            ip = await resolve(fqdn)
        return Host(fqdn, ip) if ip else None

    results = await asyncio.gather(*(probe(w) for w in words))
    return [h for h in results if h]


async def scan_port(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        fut = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(fut, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, OSError):
        return False


async def scan_ports(host: str, ports=None, concurrency: int = 200) -> list[int]:
    ports = ports or DEFAULT_PORTS
    sem = asyncio.Semaphore(concurrency)

    async def one(p):
        async with sem:
            return p if await scan_port(host, p) else None

    res = await asyncio.gather(*(one(p) for p in ports))
    return sorted(p for p in res if p)


async def fingerprint(host: str, port: int = 80, tls: bool = False) -> dict:
    """Grab HTTP response headers for basic tech fingerprinting."""
    try:
        ctx = ssl.create_default_context() if tls else None
        ctx and setattr(ctx, "check_hostname", False)
        if ctx:
            ctx.verify_mode = ssl.CERT_NONE
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=ctx), timeout=4)
        writer.write(f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
        await writer.drain()
        raw = await asyncio.wait_for(reader.read(2048), timeout=4)
        writer.close()
        headers = {}
        for line in raw.decode(errors="ignore").split("\r\n")[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                headers[k.lower()] = v
        return {k: headers[k] for k in ("server", "x-powered-by") if k in headers}
    except Exception:
        return {}
