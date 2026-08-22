.PHONY: install run migrate migrate-fake check-ownership

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python manage.py runserver 0.0.0.0:8000

migrate:
	.venv/bin/python manage.py migrate

# First claim of existing Go commerce tables
migrate-fake:
	.venv/bin/python manage.py migrate --fake-initial

check-ownership:
	bash scripts/check_migration_ownership.sh django .
