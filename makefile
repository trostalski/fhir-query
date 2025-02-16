format:
	ruff format .
	isort .

lint:
	ruff check .

test:
	pytest

test-cov:
	pytest --cov=fhir_query_client
	coverage report -m
