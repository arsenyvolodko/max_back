#!/bin/sh
set -e

# Apply database migrations
python manage.py migrate --noinput

# Collect static files (admin, drf-spectacular UI, etc.)
python manage.py collectstatic --noinput || true

exec "$@"
