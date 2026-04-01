#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

git fetch origin main --quiet

# 매일 생성되는 결과물(index.html)은 최신 반영 전에 되돌린다.
if ! git diff --quiet -- index.html; then
    git restore index.html
fi

LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse origin/main)"
if [ "$LOCAL" != "$REMOTE" ]; then
    git merge --ff-only "$REMOTE"
fi

python3 generate_schema_graph.py
