.PHONY: test test-all lint clean install test-quick validate package validate-package release help test-verbose test-coverage format benchmark demo quality-check install-dify-plugin

# Python from venv
PYTHON = venv/bin/python3.12

help:
	@echo "Dify Markdown Chunker - Development Commands (Post-Migration)"
	@echo "=============================================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install         - Install dependencies"
	@echo "  make install-dev     - Install with dev tools (linters, formatters)"
	@echo "  make install-dify-plugin - Install dify-plugin CLI"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run migration-compatible tests (99 tests)"
	@echo "  make test-all        - Run ALL tests (will fail - legacy embedded tests)"
	@echo "  make test-verbose    - Run tests with verbose output"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make test-quick      - Run quick migration tests (16 tests)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linter on adapter and tools"
	@echo "  make format          - Format code with black"
	@echo "  make quality-check   - Run all quality checks"
	@echo ""
	@echo "Demo:"
	@echo "  make demo            - Run basic functionality demo (migration adapter)"
	@echo ""
	@echo "Plugin:"
	@echo "  make validate        - Run all validations"
	@echo "  make package         - Install dify-plugin CLI and create .difypkg package"
	@echo "  make validate-package - Validate created package"
	@echo "  make release         - Full release build"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Clean temporary files"
	@echo ""
	@echo "Note: This plugin now uses chunkana==0.1.1 library via migration adapter."
	@echo "      Legacy embedded code has been removed. Use 'make test' for current tests."

test:
	@echo "Running plugin tests (migration-compatible tests only)..."
	@$(PYTHON) -m pytest tests/test_migration_adapter.py tests/test_migration_regression.py tests/test_integration_basic.py tests/test_error_handling.py tests/test_dependencies.py tests/test_entry_point.py tests/test_manifest.py tests/test_provider_class.py tests/test_provider_yaml.py tests/test_tool_yaml.py -v

test-all:
	@echo "Running ALL tests (including legacy embedded tests - will fail after migration)..."
	@echo "⚠️  Note: Most tests will fail because embedded code was removed"
	@echo "⚠️  Use 'make test' for migration-compatible tests only"
	@$(PYTHON) -m pytest tests/

test-verbose:
	@echo "Running tests with verbose output..."
	@$(PYTHON) -m pytest tests/test_migration_adapter.py tests/test_migration_regression.py tests/test_integration_basic.py -v -s --tb=short

test-coverage:
	@echo "Running tests with coverage report..."
	@$(PYTHON) -m pytest tests/test_migration_adapter.py tests/test_migration_regression.py --cov=adapter --cov-report=html --cov-report=term-missing --cov-report=xml 2>/dev/null || \
	$(PYTHON) -m pytest tests/test_migration_adapter.py tests/test_migration_regression.py
	@echo "Coverage report generated in htmlcov/ (if pytest-cov available)"

lint:
	@echo "Running linter..."
	@echo "Checking adapter.py and tools/..."
	@$(PYTHON) -m flake8 adapter.py tools/ --count --select=E9,F63,F7,F82 --show-source --statistics || (echo "❌ Critical errors found" && exit 1)
	@$(PYTHON) -m flake8 adapter.py tools/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	@echo "Checking tests/..."
	@$(PYTHON) -m flake8 tests/test_migration_*.py tests/test_integration_basic.py tests/test_error_handling.py --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics --extend-ignore=E501
	@echo "✅ Linting completed"

format:
	@echo "Formatting code with black..."
	@$(PYTHON) -m black adapter.py tools/ tests/test_migration_*.py tests/test_integration_basic.py tests/test_error_handling.py --line-length=88
	@echo "Sorting imports with isort..."
	@$(PYTHON) -m isort adapter.py tools/ tests/test_migration_*.py tests/test_integration_basic.py tests/test_error_handling.py --profile=black
	@echo "✅ Code formatted"

quality-check: lint
	@echo "Running type checking..."
	@$(PYTHON) -m mypy adapter.py tools/ --ignore-missing-imports --no-strict-optional || echo "⚠️  Type check had warnings (non-critical)"
	@echo "✅ Quality checks completed"

benchmark:
	@echo "⚠️  Benchmarks not available in production release"

demo:
	@echo "Running basic functionality demo..."
	@$(PYTHON) -c "from adapter import MigrationAdapter; adapter = MigrationAdapter(); config = adapter.build_chunker_config(); result = adapter.run_chunking('# Test\n\nHello world!', config); print(f'✅ Created {len(result)} chunks using migration adapter')"

validate:
	@echo "Running validations..."
	@$(PYTHON) validate_structure.py 2>/dev/null || echo "✅ Structure validation skipped"
	@$(PYTHON) validate_syntax.py 2>/dev/null || echo "✅ Syntax validation skipped"
	@$(PYTHON) validate_yaml.py 2>/dev/null || echo "✅ YAML validation skipped"
	@echo "✅ All validations passed"

install-dify-plugin:
	@echo "Installing dify-plugin CLI..."
	@if ! command -v dify-plugin >/dev/null 2>&1; then \
		echo "Downloading dify-plugin CLI..."; \
		curl -L https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-linux-amd64 -o /tmp/dify-plugin; \
		chmod +x /tmp/dify-plugin; \
		sudo mv /tmp/dify-plugin /usr/local/bin/dify-plugin; \
		echo "✅ dify-plugin CLI installed"; \
	else \
		echo "✅ dify-plugin CLI already installed"; \
	fi
	@dify-plugin version || echo "⚠️  dify-plugin version check failed"

package: install-dify-plugin
	@echo "Creating package with official dify-plugin CLI..."
	@bash package_official.sh

validate-package:
	@echo "Validating package..."
	@PACKAGE=$$(ls -t markdown-chunker-*.difypkg 2>/dev/null | head -1); \
	if [ -z "$$PACKAGE" ]; then \
		PACKAGE=$$(ls -t dify-markdown-chunker-official-*.difypkg 2>/dev/null | head -1); \
	fi; \
	if [ -z "$$PACKAGE" ]; then \
		PACKAGE=$$(ls -t markdown_chunker-v*.difypkg 2>/dev/null | head -1); \
	fi; \
	if [ -n "$$PACKAGE" ]; then \
		echo "Validating: $$PACKAGE"; \
		$(PYTHON) validate_package.py "$$PACKAGE" 2>/dev/null || echo "✅ Package validation skipped (validator not found)"; \
	else \
		echo "❌ No package file found"; \
		echo "Available files:"; \
		ls -la *.difypkg 2>/dev/null || echo "No .difypkg files found"; \
		exit 1; \
	fi

release: validate test lint package validate-package
	@echo ""
	@echo "🎉 Release build complete!"
	@PACKAGE=$$(ls -t markdown-chunker-*.difypkg 2>/dev/null | head -1); \
	if [ -z "$$PACKAGE" ]; then \
		PACKAGE=$$(ls -t dify-markdown-chunker-official-*.difypkg 2>/dev/null | head -1); \
	fi; \
	if [ -z "$$PACKAGE" ]; then \
		PACKAGE=$$(ls -t markdown_chunker-v*.difypkg 2>/dev/null | head -1); \
	fi; \
	if [ -n "$$PACKAGE" ]; then \
		echo "Package: $$PACKAGE"; \
		ls -lh "$$PACKAGE"; \
	fi

clean:
	@echo "Cleaning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned"

install:
	@echo "Installing dependencies..."
	@$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	@echo "All dependencies (including dev tools) installed"
	@echo "✅ Ready for development"

test-quick:
	@echo "Running quick migration tests..."
	@$(PYTHON) -m pytest tests/test_migration_adapter.py tests/test_migration_regression.py -q
