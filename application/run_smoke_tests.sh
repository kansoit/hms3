#!/usr/bin/env bash
# Smoke tests de HMS 3.0 para los tres países, sobre SQLite (no toca SQL Server).
# Uso: ./run_smoke_tests.sh        (desde application/, con el venv activado o PYTHON=ruta)
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python}
[ -x venv/bin/python ] && [ "$PYTHON" = python ] && PYTHON=venv/bin/python
fail=0
for country in AR BR US; do
    echo "=== HMS_COUNTRY=$country ==="
    if ! env -u DB_HOST HMS_ALLOW_SQLITE=1 HMS_ENV=prod HMS_COUNTRY=$country \
        "$PYTHON" manage.py test core --noinput; then
        fail=1
    fi
done
[ "$fail" -eq 0 ] && echo "OK: smoke tests de AR, BR y US pasaron." || echo "ERROR: hay smoke tests fallidos."
exit "$fail"
