"""HTML report generation for recon-forge."""
from html import escape

CSS = (
    "body{background:#0d1117;color:#c9d1d9;"
    "font-family:ui-monospace,SFMono-Regular,monospace;padding:40px}"
    "h1{color:#00ff9c;letter-spacing:-.02em}"
    "p.meta{color:#546678;font-size:13px}"
    "table{border-collapse:collapse;width:100%;margin-top:22px}"
    "th,td{border:1px solid #1e2a3a;padding:10px 12px;text-align:left;font-size:13px}"
    "th{background:#161f2c;color:#00d9ff;font-size:11px;letter-spacing:.1em}"
    "tr:hover{background:#0f1620}"
)


def render(domain, hosts):
    """Return a self-contained HTML report as a string."""
    rows = []
    for h in hosts:
        ports = ", ".join(str(p) for p in h.ports) or "-"
        tech = ", ".join(str(k) + "=" + str(v) for k, v in h.tech.items()) or "-"
        rows.append(
            "<tr><td>" + escape(h.name) + "</td>"
            "<td>" + escape(h.ip or "-") + "</td>"
            "<td>" + escape(ports) + "</td>"
            "<td>" + escape(tech) + "</td></tr>"
        )
    body = "".join(rows) or '<tr><td colspan="4">No live hosts found.</td></tr>'

    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>recon-forge - " + escape(domain) + "</title>"
        "<style>" + CSS + "</style></head><body>"
        "<h1>recon-forge report</h1>"
        "<p class='meta'>target: " + escape(domain) +
        " &middot; live hosts: " + str(len(hosts)) + "</p>"
        "<table><tr><th>Host</th><th>IP</th><th>Open Ports</th><th>Tech</th></tr>"
        + body + "</table></body></html>"
    )


def write(path, domain, hosts):
    """Write the report to disk and return the path."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(render(domain, hosts))
    return path
