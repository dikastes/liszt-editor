# syntax=docker/dockerfile:1.6
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Systemabhängigkeiten
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev curl ca-certificates git nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements zuerst kopieren (Cache nutzen)
COPY python_requirements.txt /app/python_requirements.txt
RUN python -m pip install --upgrade pip && \
    if [ -f /app/python_requirements.txt ]; then \
      pip install -r /app/python_requirements.txt; \
    else \
      echo "No requirements.txt found"; \
    fi

# Code kopieren
COPY . /app

# pylobid holen/aktualisieren
RUN if [ -d "/app/pylobid/.git" ]; then \
      git -C /app/pylobid remote set-url origin https://github.com/Nathmel123/pylobid.git && \
      git -C /app/pylobid pull; \
    else \
      git clone https://github.com/Nathmel123/pylobid /app/pylobid; \
    fi \
 && pip install -e /app/pylobid

# Tailwind/DaisyUI je App
RUN for APP in edwoca bib dmad_on_django liszt_util; do \
      if [ -f "/app/apps/$APP/package.json" ]; then \
        cd "/app/apps/$APP" && npm ci || npm install && \
        if [ -f "static/$APP/tailwind.css" ]; then \
          npx tailwindcss -i static/$APP/tailwind.css -o static/$APP/tailwind.dist.css; \
        fi; \
      fi; \
    done

# Migrations + Collectstatic
RUN python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput

EXPOSE 8000
