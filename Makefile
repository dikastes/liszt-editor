server: manage.py
	uv run manage.py runserver
makemig: manage.py
	uv run manage.py makemigrations
migrate:
	uv run manage.py migrate
import: liszt_csv/ import_manifestations.sh
	./import_manifestations.sh liszt_csv
rebuild: manage.py
	uv run manage.py rebuild_index
.PHONY: server makemig migrate import
