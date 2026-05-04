#!/bin/bash
docker compose up -d
uv run celery -A liszteditor worker --loglevel=info
