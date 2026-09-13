import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reconforge.modules import Host
from reconforge.report import render


def test_host_defaults():
    h = Host("api.example.com", "10.0.0.1")
    assert h.name == "api.example.com"
    assert h.ports == []
    assert h.tech == {}


def test_report_contains_host():
    h = Host("api.example.com", "10.0.0.1", [80, 443], {"server": "nginx"})
    html = render("example.com", [h])
    assert "api.example.com" in html
    assert "10.0.0.1" in html
    assert "nginx" in html


def test_report_empty():
    html = render("example.com", [])
    assert "No live hosts found" in html
