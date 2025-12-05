PY=python3
PIP=$(PY) -m pip
PACKAGE=deep_research_from_scratch

.PHONY: help install install-dev lint format test build clean

help: ## Show available make targets
	@echo "Usage: make <target>"
	@echo ""
	@echo "Common targets:"
	@echo "  install       - Install package in editable mode"
	@echo "  install-dev   - Install package editable with dev extras (mypy, ruff)"
	@echo "  lint          - Run ruff linter (requires ruff)"
	@echo "  format        - Run ruff format (requires ruff)"
	@echo "  test          - Run test suite with pytest (requires pytest)"
	@echo "  build         - Build wheel/sdist using 'python -m build'"
	@echo "  clean         - Remove build artifacts and caches"

install: ## Install package in editable mode
	$(PIP) install -e .

install-dev: ## Install package in editable mode with development extras
	$(PIP) install -e ".[dev]"

lint: ## Run ruff linting
	@command -v ruff >/dev/null 2>&1 || (echo "ruff not found; run 'make install-dev' or 'pip install ruff'"; exit 1)
	$(PY) -m ruff check .

format: ## Run ruff formatter
	@command -v ruff >/dev/null 2>&1 || (echo "ruff not found; run 'make install-dev' or 'pip install ruff'"; exit 1)
	$(PY) -m ruff format .

test: ## Run tests with pytest
	@command -v pytest >/dev/null 2>&1 || (echo "pytest not found; install it (pip install pytest) or add it to dev extras"; exit 1)
	pytest -q

build: ## Build source and wheel distributions (requires build package)
	@command -v python >/dev/null 2>&1
	$(PY) -m build

clean: ## Remove build artifacts and caches
	-rm -rf build dist *.egg-info
	-find . -type d -name '__pycache__' -exec rm -rf {} +
	-find . -type f -name '*.pyc' -delete
