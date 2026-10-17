#!/bin/sh
# Container entrypoint: (re)load data then serve. DATA_DIRS = space-separated dataset folders.
set -e
python -m copilot.loader ${DATA_DIRS:-/data/sample-data}
exec python -m uvicorn copilot.server:app --host 0.0.0.0 --port ${PORT:-8000}
