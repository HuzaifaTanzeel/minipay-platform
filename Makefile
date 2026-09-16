.PHONY: setup-venv test-api test-ui test-ui-headed test-cli

PYTHON ?= .venv/bin/python

setup-venv:
	bash scripts/setup-venv.sh

test-api:
	$(PYTHON) -m pytest tests/api -v

test-ui:
	$(PYTHON) -m pytest -c tests/ui/pytest.ini tests/ui -v

test-ui-headed:
	$(PYTHON) -m pytest -c tests/ui/pytest.ini tests/ui -v --headed --slowmo 400

test-cli:
	$(PYTHON) -m pytest python/tests -q
