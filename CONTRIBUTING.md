# Contributing to Temporal Graph RAG

We appreciate your interest in contributing to Temporal Graph RAG! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## How to Contribute

There are many ways to contribute to Temporal Graph RAG:

- 🐛 **Report bugs** - Use the [issue tracker](https://github.com/Schechter-Edward/temporal-graph-rag/issues) to report bugs
- 💡 **Request features** - Suggest new features or improvements
- 📝 **Improve documentation** - Help us maintain and improve our documentation
- 🐍 **Write code** - Contribute to the codebase
- 🧪 **Write tests** - Help improve our test coverage
- 📖 **Answer questions** - Help answer questions on issues and discussions

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Docker (for running Neo4j and Qdrant locally)
- Poetry (recommended) or pip

### Local Development

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/temporal-graph-rag.git
   cd temporal-graph-rag
   ```

2. **Install dependencies:**

   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -e .
   ```

3. **Set up pre-commit hooks:**

   ```bash
   pre-commit install
   ```

4. **Start development services:**

   ```bash
   # Start Neo4j and Qdrant using Docker Compose
   docker-compose up -d
   
   # Or start individual services
   docker run -d --name neo4j -p 7687:7687 -p 7474:7474 neo4j:5
   docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
   ```

5. **Run tests to verify setup:**

   ```bash
   # Run all tests
   pytest
   
   # Run specific test modules
   pytest tests/test_temporal_algebra.py
   pytest tests/test_engine.py
   ```

## Code Style

We use several tools to maintain code quality and consistency:

### Pre-commit Hooks

Our pre-commit configuration automatically handles:

- Code formatting with `black`
- Import sorting with `isort`
- Type checking with `ruff`
- Security checks with `bandit`

### Code Style Guidelines

- **Formatting**: Use `black` for code formatting
- **Import Sorting**: Use `isort` for import organization
- **Linting**: Follow `ruff` suggestions for code quality
- **Type Hints**: Always use type hints for function signatures
- **Docstrings**: Use Google-style docstrings for public functions and classes

### Example Code Style

```python
from typing import List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TemporalQuery:
    """Represents a temporal query with time constraints.
    
    Args:
        query: The main query text
        start_time: Optional start time for temporal filtering
        end_time: Optional end time for temporal filtering
        operator: Temporal operator (AND, OR, NOT)
    """
    
    query: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    operator: str = "AND"
    
    def validate(self) -> bool:
        """Validate the temporal query parameters.
        
        Returns:
            True if query is valid, False otherwise
        """
        if self.start_time and self.end_time:
            return self.start_time <= self.end_time
        return True
```

## Testing

### Test Structure

Our tests are organized as follows:

- `tests/test_temporal_algebra.py` - Tests for temporal reasoning logic
- `tests/test_engine.py` - Tests for the main engine functionality
- `tests/integration/` - Integration tests (when available)

### Writing Tests

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **Performance Tests**: Benchmark critical operations

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/temporal_graph_rag

# Run specific test file
pytest tests/test_temporal_algebra.py

# Run specific test
pytest tests/test_temporal_algebra.py::test_interval_intersection

# Run with verbose output
pytest -v

# Run with performance profiling
pytest --profile-svg
```

### Test Data

For testing, we use:

- Mock data for unit tests
- Docker containers for integration tests
- Real datasets for performance benchmarks

## Documentation

### Documentation Standards

- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Include type hints for all public functions
- Add examples for complex functions
- Update README.md for major changes

### Documentation Structure

- `README.md` - Project overview and quick start
- `docs/` - Detailed documentation (when available)
- Code comments - Implementation details

## Submitting Changes

### Before Submitting

1. **Run the test suite:**

   ```bash
   pytest
   ```

2. **Check code quality:**

   ```bash
   ruff check src/
   black --check src/
   isort --check-only src/
   ```

3. **Update documentation:**
   - Update relevant docstrings
   - Update README.md if needed
   - Add changelog entries for significant changes

### Creating Pull Requests

1. **Create a new branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow our code style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Commit your changes:**

   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push to your fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request:**
   - Use our [PR template](.github/pull_request_template.md)
   - Reference related issues
   - Describe the changes and motivation

### PR Guidelines

- **Title**: Use conventional commits format (feat:, fix:, docs:, etc.)
- **Description**: Explain what the PR does and why
- **Tests**: Include tests for new functionality
- **Breaking Changes**: Clearly mark and document any breaking changes
- **Review**: Address all review comments before merging

## Issue Reporting

### Before Reporting

1. **Check existing issues** - Your issue might already be reported
2. **Check the documentation** - Your question might be answered
3. **Try the latest version** - Your issue might be fixed

### Creating Issues

Use our issue templates:

- [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) - For reporting bugs
- [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) - For suggesting new features

### Issue Guidelines

- **Clear title** - Summarize the issue in 5-10 words
- **Detailed description** - Include steps to reproduce, expected vs actual behavior
- **Environment** - Include Python version, OS, and dependency versions
- **Code examples** - Include minimal reproducible examples when possible
- **Labels** - Use appropriate labels (we'll add them if needed)

## Development Workflow

### Feature Development

1. **Plan**: Create an issue to discuss the feature
2. **Design**: Consider the impact on existing architecture
3. **Implement**: Write code following our guidelines
4. **Test**: Add comprehensive tests
5. **Document**: Update documentation
6. **Review**: Submit PR for review

### Bug Fixes

1. **Reproduce**: Create a minimal reproduction case
2. **Investigate**: Identify the root cause
3. **Fix**: Implement the fix
4. **Test**: Add regression tests
5. **Verify**: Ensure no new issues are introduced

## Performance Considerations

When contributing performance-critical code:

1. **Benchmark**: Use our benchmarking tools
2. **Profile**: Identify bottlenecks
3. **Optimize**: Focus on algorithmic improvements first
4. **Test**: Ensure correctness is maintained

## Security

- Report security vulnerabilities privately
- Follow secure coding practices
- Review dependencies for known vulnerabilities

## Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs and feature requests
- **Documentation**: Check our docs first
- **Community**: Join our community channels

## Recognition

We recognize and appreciate all contributors:

- Contributors are listed in the README
- Significant contributors may be added as maintainers
- Contributors are acknowledged in release notes

## Questions?

If you have questions about contributing, please:

1. Check this document first
2. Search existing issues and discussions
3. Create a new issue or discussion
4. Reach out to maintainers

Thank you for contributing to Temporal Graph RAG! 🎉
