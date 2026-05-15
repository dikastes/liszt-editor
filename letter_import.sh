#!/bin/bash
# Usage: ./import_manifestations.sh [path_prefix]
# Example: ./import_manifestations.sh ../some_other_dir/

CSV_PATH_PREFIX=${1:-liszt_csv/}

echo importing dmad entities
python manage.py import_dmad_data "${CSV_PATH_PREFIX}dmad_main_import.csv"
echo importing letters
python manage.py import_letters_from_csv "${CSV_PATH_PREFIX}liszt_letter.csv"
echo rebuilding index
python manage.py rebuild_index --noinput
