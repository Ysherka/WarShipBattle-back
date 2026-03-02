#!/bin/sh
set -e
exec fastapi run --host 0.0.0.0 --port "${PORT:-8000}" "$@"