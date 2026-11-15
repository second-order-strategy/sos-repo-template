# The contract CI calls. Replace the commands if this project isn't Python;
# keep the target names (install, lint, test, coverage).
COVERAGE_MIN ?= 0

.PHONY: install lint test coverage

install:
	python -m pip install --disable-pip-version-check -r requirements-dev.txt -e .

lint:
	ruff check .
	ruff format --check .

test:
	pytest

coverage:
	mkdir -p reports
	pytest --junitxml=reports/junit.xml --cov=src --cov-report=term --cov-report=xml:reports/coverage.xml --cov-fail-under=$(COVERAGE_MIN)
