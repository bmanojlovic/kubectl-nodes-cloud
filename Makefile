.PHONY: install test clean lint format help demo watch plugin-test list-contexts

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package using uv tool install
	uv tool install --force --no-cache .

install-dev: ## Install in development mode with test dependencies
	uv venv test-env
	source test-env/bin/activate && uv pip install -e .

test: ## Run the test suite
	@if [ -d "test-env" ]; then \
		source test-env/bin/activate && python run_tests.py; \
	else \
		echo "Please run 'make install-dev' first"; \
	fi

clean: ## Clean up build artifacts and test environment
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf test-env/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: ## Run basic linting (requires flake8)
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 kubectl_node tests; \
	else \
		echo "flake8 not found. Install with: uv tool install flake8"; \
	fi

format: ## Format code (requires black)
	@if command -v black >/dev/null 2>&1; then \
		black kubectl_node tests; \
	else \
		echo "black not found. Install with: uv tool install black"; \
	fi

demo: ## Run the tool to show current cluster nodes
	kubectl-node

watch: ## Run the tool in watch mode
	kubectl-node -w

plugin-test: ## Test as kubectl plugin
	kubectl node

list-contexts: ## List available kubectl contexts
	kubectl-node --list-contexts
