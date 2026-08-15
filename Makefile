.PHONY: run test test-pg migrate seed lint fmt clean-artifacts

run:
	python manage.py runserver

migrate:
	python manage.py makemigrations && python manage.py migrate

seed:
	python manage.py seed_outlets

test:
	pytest -q

test-pg:
	USE_POSTGRES=1 pytest -q

lint:
	ruff check .

fmt:
	ruff format .

clean-artifacts:
	rm -f db.sqlite3
	rm -rf .pytest_cache .ruff_cache
