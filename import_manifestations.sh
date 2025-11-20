#!/bin/bash
# Usage: ./import_manifestations.sh [path_prefix]
# Example: ./import_manifestations.sh ../some_other_dir/

CSV_PATH_PREFIX=${1:-../liszt_csv/}

echo importing 1b fragments
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_1b_long.csv" -st autograph -mf fragment
echo importing 1c correction sheets
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_1c_long.csv" -st autograph -f correctionsheet
echo importing 1d autographs
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_1d_long.csv" -st autograph
echo importing 2 copies
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_2_long.csv" -st copy
echo importing 3 prints
python manage.py import_manifestations_from_csv "${CSV_PATH_PREFIX}liszt_3_long.csv" -st correctedprint -n
echo importing gnd ids
python manage.py import_gnd_ids "${CSV_PATH_PREFIX}gnd_ids.csv"
echo importing additional gnd ids
python manage.py import_gnd_ids "${CSV_PATH_PREFIX}additional_gnd_ids.csv"
echo importing letters
python manage.py import_letters_from-csv "${CSV_PATH_PREFIX}liszt_letter.csv"
echo importing works and expressions
python manage.py import_works_from_csv "${CSV_PATH_PREFIX}liszt_work.csv"
