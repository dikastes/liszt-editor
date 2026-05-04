#!/bin/bash

if ! command -v docker compose > /dev/null; then
	echo "please install docker"
fi

docker compose up -d
uv run celery -A liszteditor worker --loglevel=info
