# The contract CI calls. Replace the commands if this project isn't Python;
# keep the target names (install, lint, test, coverage).

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
	@floor=$${COVERAGE_MIN:-$$(python scripts/check_manifest.py sos-project.yml --coverage-min)} || exit 1; \
	pytest --junitxml=reports/junit.xml --cov=src --cov=scripts --cov-report=term --cov-report=xml:reports/coverage.xml --cov-fail-under="$$floor"
