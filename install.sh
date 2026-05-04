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
    echo -e "\e[90m> $*\e[0m"
    eval "$@"
  else
    eval "$@" > /dev/null 2>&1
  fi
  if [ $? -ne 0 ]; then
    red "✘ Command failed: $*"
    exit 1
  fi
}

# === START ===

yellow "Tip: Run this script with -V to enable verbose output."

# === CHECK ENV FILE ===
if [[ ! -f .env ]]; then
  red ".env file not found in the current directory. Please paste it manually."
  exit 1
fi

# === CHECK PYTHON ===
if ! command -v uv > /dev/null; then
	red "Please install uv"
fi

# === BASE DIR ===
SCRIPT_DIR=$(dirname "$(realpath "$0")")

blue "Script directory: $SCRIPT_DIR"

uv venv --clear

# === INSTALL NPM & BUILD TAILWIND IN APPS ===
for APP in edwoca bib dmad_on_django liszt_util; do
  (
    cd "$SCRIPT_DIR/apps/$APP" || { red "App directory not found: $APP"; exit 1; }
    yellow "[$APP] Installing npm packages..."
    run "npm install"
    yellow "[$APP] Compiling Tailwind CSS..."
    run "npx tailwindcss -i static/$APP/tailwind.css -o static/$APP/tailwind.dist.css"
  )
done

# === INSTALL PYTHON DEPENDENCIES ===
yellow "Installing python dependencies..."

uv sync --locked

# === DJANGO MIGRATIONS ===
yellow "Running Django migrations..."

run uv run manage.py makemigrations
run uv run manage.py migrate

green "✔ Setup complete!"
yellow "Run the project with uv run manage.py runserver"
