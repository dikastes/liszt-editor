#!/usr/bin/env bash

# Migrations & Static – jetzt sind ENV Variablen da
if [ -f "manage.py" ]; then
  python manage.py makemigrations --noinput || true
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi

exec "$@"

