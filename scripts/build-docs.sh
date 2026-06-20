#!/usr/bin/env bash
# Build the MkDocs site for this repo and deploy it to the snipermqtt LXC,
# served by nginx under https://snipermqtt.uzc/station/ (basic auth).
#
# Requirements (one-time, in a local venv):
#   python3 -m venv ~/.docs-venv
#   ~/.docs-venv/bin/pip install "mkdocs-material==9.5.50" mkdocs-same-dir
#
# Usage: bash scripts/build-docs.sh        (regenerates mkdocs.yml, builds, deploys)
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${DOCS_VENV:-$HOME/.docs-venv}"
HOST="${DOCS_HOST:-192.168.0.79}"
TARGET="${DOCS_TARGET:-station}"
SITE_URL="https://snipermqtt.uzc/${TARGET}/"

# Regenerate mkdocs.yml from the current doc tree
"$VENV/bin/python" "$REPO/scripts/gen_mkdocs.py" "$REPO" "SniperStation Docs" "$SITE_URL"

# Build to a temp dir
OUT="$(mktemp -d)"
DISABLE_MKDOCS_2_WARNING=true "$VENV/bin/mkdocs" build -f "$REPO/mkdocs.yml" -d "$OUT"

# Deploy (clean target, then extract)
ssh root@"$HOST" "mkdir -p /var/www/sniperdocs/$TARGET"
tar -C "$OUT" -cf - . | ssh root@"$HOST" "rm -rf /var/www/sniperdocs/$TARGET/* && tar -C /var/www/sniperdocs/$TARGET -xf - && chmod 755 /var/www/sniperdocs/$TARGET && chmod -R a+rX /var/www/sniperdocs/$TARGET"
rm -rf "$OUT"
echo "Deployed -> $SITE_URL"
