#!/bin/bash
# Usage: ./import_manifestations.sh [path_prefix]
# Example: ./import_manifestations.sh ../some_other_dir/

CSV_PATH_PREFIX=${1:-../liszt_csv/}

python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_1b_long.csv" autograph --manifestation_form fragment
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_1c_long.csv" autograph --function correctionsheet
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_1d_long.csv" autograph --manifestation_form fragment
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_2_long.csv" copy
python manage.py import_gnd_ids "${CSV_PATH_PREFIX}gnd_ids.csv"
python manage.py import_gnd_ids "${CSV_PATH_PREFIX}additional_gnd_ids.csv"
