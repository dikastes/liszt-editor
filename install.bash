#!/bin/bash

if [[ ! -f .env ]]; then
  echo ".env file not found in the current directory. Please paste it manually."
  exit 1
fi


if command -v python > /dev/null; then
    PYTHON_BIN=$(command -v python)
elif command -v python3 > /dev/null; then
    PYTHON_BIN=$(command -v python3)
else
    echo "Python is not installed."
    exit 1
fi

echo "Using Python: $PYTHON_BIN"

SCRIPT_DIR=$(dirname "$(realpath "$0")")

echo "Creating virtual environment..."

$PYTHON_BIN -m venv $SCRIPT_DIR

echo "Installing npm dependencies..."

npm install --prefix $SCRIPT_DIR

(
	cd $SCRIPT_DIR/apps/edwoca
	npm install
	npx tailwindcss -i static/edwoca/tailwind.css -o static/edwoca/tailwind.dist.css

)

(
	cd $SCRIPT_DIR/apps/bib
	npm install
	npx tailwindcss -i static/bib/tailwind.css -o static/bib/tailwind.dist.css
)

echo "Installing python dependencies..."

$SCRIPT_DIR/bin/pip install -r $SCRIPT_DIR/python_requirements.txt

echo "Migrating..."

$SCRIPT_DIR/bin/python3 $SCRIPT_DIR/manage.py makemigrations
$SCRIPT_DIR/bin/python3 $SCRIPT_DIR/manage.py migrate

echo "done"
