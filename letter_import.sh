#!/bin/bash
# Usage: ./import_manifestations.sh [path_prefix]
# Example: ./import_manifestations.sh ../some_other_dir/

CSV_PATH_PREFIX=${1:-liszt_csv/}

echo importing dmad entities
uv run manage.py import_dmad_data "${CSV_PATH_PREFIX}dmad_main_import.csv"
echo importing letters
uv run manage.py import_letters_from_csv "${CSV_PATH_PREFIX}liszt_letter.csv"
echo rebuilding index
uv run manage.py rebuild_index --noinput
