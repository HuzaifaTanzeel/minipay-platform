.PHONY: setup-venv test-api test-ui test-ui-headed test-cli k8s-up k8s-down k8s-smoke

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

k8s-up:
	bash scripts/k8s-up.sh

k8s-down:
	bash scripts/k8s-down.sh

k8s-smoke:
	bash scripts/k8s-smoke.sh
