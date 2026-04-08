#!/bin/bash

set -euo pipefail

PORT="${SCHEMA_GRAPH_PORT:-8080}"
BIND_IP="${SCHEMA_GRAPH_BIND_IP:-0.0.0.0}"

exec /usr/bin/python3 -m http.server "$PORT" --bind "$BIND_IP"
