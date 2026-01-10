# Contributing to Dify Markdown Chunker

Thank you for your interest in contributing to the Dify Markdown Chunker plugin!

For comprehensive development documentation, see **[Developer Guide](docs/guides/developer-guide.md)**.

---

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/dify-markdown-chunker.git`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `make install`
6. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Making Changes

1. Make your changes in your feature branch
2. Write or update tests as needed
3. Run tests: `make test`
4. Format code: `make format`
5. Run linter: `make lint`
6. Validate structure: `make validate`

### Testing

We maintain comprehensive test coverage (445 tests). Please ensure:

- All existing tests pass
- New features have corresponding tests
- Property-based tests are used for universal properties
- Integration tests cover end-to-end workflows

Run tests with:
```bash
make test              # All tests
make test-quick        # Quick tests only
make test-coverage     # With coverage report
```

### Code Style

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions focused and small
- Use meaningful variable names

Format your code:
```bash
make format
```

### Documentation

- Update README.md if adding features
- Update CHANGELOG.md with your changes
- Add docstrings to new functions/classes
- Update relevant documentation in `docs/`

## Submitting Changes

### Pull Request Process

1. Update CHANGELOG.md with your changes
2. Ensure all tests pass
3. Update documentation as needed
4. Push to your fork
5. Create a Pull Request with:
   - Clear description of changes
   - Reference to related issues
   - Test results
   - Screenshots (if UI changes)

### Pull Request Guidelines

- One feature/fix per PR
- Keep PRs focused and small
- Write clear commit messages
- Reference issues in commits (e.g., "Fixes #123")
- Respond to review feedback promptly

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Example:
```
feat: Add support for custom delimiters

- Added delimiter configuration option
- Updated parser to handle custom delimiters
- Added tests for delimiter functionality

Closes #123
```

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Breaking changes

## Testing in Dify

Before submitting, test your changes in a real Dify instance:

1. Build the plugin: `make package`
2. Install in Dify UI
3. Test with real documents
4. Verify all features work as expected

## Reporting Bugs

Use GitHub Issues to report bugs. Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, Dify version, OS)
- Error messages and logs
- Minimal reproducible example

## Suggesting Features

Use GitHub Issues for feature requests. Include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if any)
- Examples of similar features elsewhere

## Community

- Be respectful and inclusive
- Help others in issues and discussions
- Share your use cases and feedback
- Contribute to documentation

## Questions?

- Open a GitHub Issue for questions
- Check existing documentation:
  - **[Developer Guide](docs/guides/developer-guide.md)** - Comprehensive development documentation
  - **[Documentation Index](docs/README.md)** - All documentation
  - **[DEVELOPMENT.md](DEVELOPMENT.md)** - Quick development reference
- Review examples in `examples/`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉

## Test Guidelines

When contributing tests to this project:

1. **Use the migration adapter**: New tests should use `MigrationAdapter` instead of legacy modules
2. **Follow naming conventions**: 
   - `test_migration_*.py` for tests using the migration adapter
   - `test_integration_*.py` for integration tests
   - `test_*_adapted.py` for adapted legacy tests
3. **Run the full test suite**: Ensure `make test-all` passes before submitting
4. **Avoid redundant tests**: Check if similar functionality is already tested

### Test Categories

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Migration tests**: Test adapter functionality
- **Property tests**: Test universal properties with generated data