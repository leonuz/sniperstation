#!/usr/bin/env python3
"""Generate a mkdocs.yml for a project repo (Material theme, same-dir plugin).

Builds an EN/ES grouped nav from the repo's markdown files and writes mkdocs.yml
at the repo root. Source code and non-doc assets are excluded from the build.
"""
import os
import sys
import yaml

repo, site_name, site_url = sys.argv[1], sys.argv[2], sys.argv[3]

ROOT_ORDER = ["README", "ROADMAP", "TODO", "CHANGELOG"]
TITLES = {
    "README": "Home", "ROADMAP": "Roadmap", "TODO": "TODO",
    "CHANGELOG": "Changelog", "BOM": "BOM", "wiring": "Wiring",
    "schematic": "Schematic", "deployment": "Deployment", "security": "Security",
    "snipermqtt-deployment": "Broker Deployment",
    "sniperstation_project": "Project Overview",
    "system_overview": "System Overview", "outdoor_power": "Outdoor Power",
    "station485_wiring": "Station-485 Wiring",
    "esp8266_interior": "ESP8266 Interior",
    "indoor_unit_design": "Indoor Enclosure", "requirements": "Requirements",
    "SOURCES": "Datasheet Sources",
}
SECTIONS = {"hardware": "Hardware", "docs": "Docs"}


def base_id(path):
    n = os.path.basename(path)
    if n.endswith(".es.md"):
        return n[:-6]
    if n.endswith(".md"):
        return n[:-3]
    return n


def title(path):
    b = base_id(path)
    return TITLES.get(b, b.replace("_", " ").replace("-", " ").title())


def collect(es):
    found = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in
                       (".git", "firmware", "proxmox", "software", "scripts", "assets")]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            is_es = fn.endswith(".es.md")
            if is_es != es:
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), repo)
            found.append(rel)
    return found


def root_key(p):
    b = base_id(p)
    return (ROOT_ORDER.index(b) if b in ROOT_ORDER else len(ROOT_ORDER), b.lower())


def build_section(es):
    files = collect(es)
    root = sorted([f for f in files if os.sep not in f], key=root_key)
    subs = {}
    for f in files:
        if os.sep in f:
            subs.setdefault(f.split(os.sep)[0], []).append(f)
    section = [{title(f): f} for f in root]
    for top in sorted(subs):
        items = [{title(f): f} for f in sorted(subs[top], key=lambda x: base_id(x).lower())]
        section.append({SECTIONS.get(top, top.title()): items})
    return section


nav = [{"English": build_section(False)}, {"Español": build_section(True)}]

config = {
    "site_name": site_name,
    "site_url": site_url,
    "docs_dir": ".",
    "use_directory_urls": True,
    "nav": nav,
    "plugins": ["same-dir", "search"],
    "theme": {
        "name": "material",
        "language": "en",
        "features": ["navigation.sections", "navigation.top",
                     "navigation.footer", "content.code.copy", "search.suggest"],
        "palette": [
            {"media": "(prefers-color-scheme: light)", "scheme": "default",
             "primary": "teal", "toggle": {"icon": "material/weather-night",
                                           "name": "Switch to dark mode"}},
            {"media": "(prefers-color-scheme: dark)", "scheme": "slate",
             "primary": "teal", "toggle": {"icon": "material/weather-sunny",
                                           "name": "Switch to light mode"}},
        ],
    },
    "markdown_extensions": [
        "admonition", "tables", "toc", "attr_list", "md_in_html",
        {"pymdownx.highlight": {"anchor_linenums": True}},
        "pymdownx.superfences", "pymdownx.details",
    ],
    "exclude_docs": "\n".join([
        "firmware/", "proxmox/", "software/", "scripts/", "assets/photos/", "venv/",
        "*.py", "*.ino", "*.json", "*.yaml", "*.yml", "*.service",
        "*.env*", "*.h", "*.example", "*.mmd", "*.sh",
    ]) + "\n",
    "validation": {
        "nav": {"omitted_files": "ignore", "not_found": "warn"},
        "links": {"not_found": "warn", "absolute_links": "ignore"},
    },
}

out = os.path.join(repo, "mkdocs.yml")
with open(out, "w") as fh:
    yaml.dump(config, fh, sort_keys=False, default_flow_style=False, allow_unicode=True)
print(f"wrote {out}")
