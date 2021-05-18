install:
	@poetry install
	@poetry run pre-commit install -f

update:
	@poetry update
	@poetry run pre-commit autoupdate

test:
	@poetry run pytest -v -x -p no:warnings --cov-report term-missing --cov=./subdivisions

ci:
	@poetry run pytest --cov=./subdivisions

format:
	@poetry run black .

pre-commit:
	@poetry run pre-commit run --all
