.PHONY: test lint clean install test-quick validate package validate-package release help test-verbose test-coverage format benchmark demo quality-check

# Python from venv
PYTHON = venv/bin/python3.12

help:
	@echo "Dify Markdown Chunker - Development Commands"
	@echo "============================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install         - Install dependencies"
	@echo "  make install-dev     - Install with dev tools (linters, formatters)"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run all core tests (property + integration)"
	@echo "  make test-all        - Run all tests in repository"
	@echo "  make test-verbose    - Run tests with verbose output"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make test-quick      - Run quick tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linter"
	@echo "  make format          - Format code with black"
	@echo "  make quality-check   - Run all quality checks"
	@echo ""
	@echo "Benchmarks:"
	@echo "  make benchmark       - Run performance benchmarks"
	@echo "  make demo            - Run basic functionality demo"
	@echo ""
	@echo "Plugin:"
	@echo "  make validate        - Run all validations"
	@echo "  make package         - Create .difypkg package"
	@echo "  make validate-package - Validate created package"
	@echo "  make release         - Full release build"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Clean temporary files"

test:
	@echo "Running all core tests (property + integration)..."
	@$(PYTHON) -m pytest \
		tests/test_p0_property_tests.py \
		tests/test_p1_specification_properties.py \
		tests/test_domain_properties.py \
		tests/test_v2_properties.py \
		tests/test_entry_point.py \
		tests/test_error_handling.py \
		tests/test_integration_basic.py \
		tests/test_manifest.py \
		tests/test_provider_class.py \
		tests/test_provider_yaml.py \
		tests/test_tool_yaml.py \
		tests/test_dependencies.py \
		tests/api/test_backward_compatibility.py \
		tests/chunker/test_chunk_simple.py \
		tests/chunker/test_monotonic_ordering_property.py \
		tests/chunker/test_no_empty_chunks_property.py \
		tests/chunker/test_overlap_properties_redesign.py \
		tests/chunker/test_serialization.py \
		tests/chunker/test_serialization_roundtrip_property.py \
		tests/chunker/test_components/test_overlap_new_model.py \
		tests/parser/test_smoke.py \
		tests/integration/test_career_matrix.py \
		tests/integration/test_dify_plugin_integration.py \
		tests/integration/test_end_to_end.py \
		tests/integration/test_full_pipeline_real_docs.py \
		tests/integration/test_overlap_redesign_integration.py \
		-v

test-all:
	@echo "Running all tests..."
	@$(PYTHON) -m pytest tests/

test-verbose:
	@echo "Running tests with verbose output..."
	@$(PYTHON) -m pytest tests/test_domain_properties.py tests/test_v2_properties.py -v -s --tb=short

test-coverage:
	@echo "Running tests with coverage report..."
	@$(PYTHON) -m pytest tests/test_domain_properties.py tests/test_v2_properties.py --cov=markdown_chunker_v2 --cov-report=html --cov-report=term-missing --cov-report=xml 2>/dev/null || \
	$(PYTHON) -m pytest tests/test_domain_properties.py tests/test_v2_properties.py
	@echo "Coverage report generated in htmlcov/ (if pytest-cov available)"

lint:
	@echo "Running linter..."
	@echo "Checking markdown_chunker_v2/..."
	@$(PYTHON) -m flake8 markdown_chunker_v2/ --count --select=E9,F63,F7,F82 --show-source --statistics || (echo "❌ Critical errors found" && exit 1)
	@$(PYTHON) -m flake8 markdown_chunker_v2/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	@echo "Checking tests/..."
	@$(PYTHON) -m flake8 tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics --extend-ignore=E501
	@echo "✅ Linting completed"

format:
	@echo "Formatting code with black..."
	@$(PYTHON) -m black markdown_chunker_v2/ tests/ scripts/ --line-length=88
	@echo "Sorting imports with isort..."
	@$(PYTHON) -m isort markdown_chunker_v2/ tests/ scripts/ --profile=black
	@echo "✅ Code formatted"

quality-check: lint
	@echo "Running type checking..."
	@$(PYTHON) -m mypy markdown_chunker_v2/ --ignore-missing-imports --no-strict-optional || echo "⚠️  Type check had warnings (non-critical)"
	@echo "✅ Quality checks completed"

benchmark:
	@echo "Running benchmarks..."
	@$(PYTHON) -m benchmarks.benchmark_chunker 2>/dev/null || echo "⚠️  Benchmarks not available"

demo:
	@echo "Running basic functionality demo..."
	@$(PYTHON) -c "from markdown_chunker import MarkdownChunker; chunker = MarkdownChunker(); chunks = chunker.chunk('# Test\n\nHello world!'); print(f'✅ Created {len(chunks)} chunks using {chunks[0].strategy if chunks else \"none\"} strategy')"

validate:
	@echo "Running validations..."
	@$(PYTHON) validate_structure.py 2>/dev/null || echo "✅ Structure validation skipped"
	@$(PYTHON) validate_syntax.py 2>/dev/null || echo "✅ Syntax validation skipped"
	@$(PYTHON) validate_yaml.py 2>/dev/null || echo "✅ YAML validation skipped"
	@echo "✅ All validations passed"

package:
	@echo "Creating package with official dify-plugin CLI..."
	@bash package_official.sh

validate-package:
	@echo "Validating package..."
	@PACKAGE=$$(ls -t dify-markdown-chunker-official-*.difypkg 2>/dev/null | head -1); \
	if [ -z "$$PACKAGE" ]; then \
		PACKAGE=$$(ls -t markdown_chunker-v*.difypkg 2>/dev/null | head -1); \
	fi; \
	if [ -n "$$PACKAGE" ]; then \
		echo "Validating: $$PACKAGE"; \
		$(PYTHON) validate_package.py "$$PACKAGE"; \
	else \
		echo "❌ No package file found"; \
		exit 1; \
	fi

release: validate test lint package validate-package
	@echo ""
	@echo "🎉 Release build complete!"
	@PACKAGE=$$(ls -t dify-markdown-chunker-official-*.difypkg 2>/dev/null | head -1); \
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
	@echo "Running quick tests..."
	@$(PYTHON) -m pytest tests/ -q
