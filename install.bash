#!/bin/bash

# === PARSE FLAGS ===
VERBOSE=false
for arg in "$@"; do
  if [[ "$arg" == "-V" ]]; then
    VERBOSE=true
  fi
done

# === COLORS ===
red()    { echo -e "\e[31m$1\e[0m"; }
green()  { echo -e "\e[32m$1\e[0m"; }
yellow() { echo -e "\e[33m$1\e[0m"; }
blue()   { echo -e "\e[34m$1\e[0m"; }

# === COMMAND WRAPPER ===
run() {
  if [ "$VERBOSE" = true ]; then
    eval "$@"
  else
    eval "$@" > /dev/null 2>&1
  fi
}

# === START ===

yellow "Tip: Run this script with -V to enable verbose output."

if [[ ! -f .env ]]; then
  red ".env file not found in the current directory. Please paste it manually."
  exit 1
fi

if command -v python > /dev/null; then
    PYTHON_BIN=$(command -v python)
elif command -v python3 > /dev/null; then
    PYTHON_BIN=$(command -v python3)
else
    red "Python is not installed."
    exit 1
fi

blue "Using Python: $PYTHON_BIN"

SCRIPT_DIR=$(dirname "$(realpath "$0")")

yellow "Creating virtual environment..."
run "$PYTHON_BIN -m venv $SCRIPT_DIR"

yellow "Installing npm dependencies..."
run "npm install --prefix $SCRIPT_DIR"

(
	cd "$SCRIPT_DIR/apps/edwoca"
	yellow "[edwoca] Installing npm packages..."
	run "npm install"
	yellow "[edwoca] Compiling Tailwind CSS..."
	run "npx tailwindcss -i static/edwoca/tailwind.css -o static/edwoca/tailwind.dist.css"
)

(
	cd "$SCRIPT_DIR/apps/bib"
	yellow "[bib] Installing npm packages..."
	run "npm install"
	yellow "[bib] Compiling Tailwind CSS..."
	run "npx tailwindcss -i static/bib/tailwind.css -o static/bib/tailwind.dist.css"
)

(

	cd "$SCRIPT_DIR/apps/dmad_on_django"
	yellow "[dmad_on_django] Installing npm packages..."
	run "npm install"
	yellow "[dmad_on_django] Compiling Tailwind CSS..."
	run "npx tailwindcss -i static/dmad_on_django/tailwind.css -o static/dmad_on_django/tailwind.dist.css"
)

yellow "Installing python dependencies..."
run "$SCRIPT_DIR/bin/pip install -r $SCRIPT_DIR/python_requirements.txt"

yellow "Running migrations..."
run "$SCRIPT_DIR/bin/python3 $SCRIPT_DIR/manage.py makemigrations"
run "$SCRIPT_DIR/bin/python3 $SCRIPT_DIR/manage.py migrate"

green "✔ Setup complete!"

