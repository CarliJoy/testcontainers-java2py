# Agent Instructions for testcontainers-python

## Project Overview

This is a **Python implementation of Testcontainers** - a library that provides lightweight, throwaway instances of common databases, Selenium web browsers, or anything else that can run in a Docker container for testing purposes.

This project is a Python port of the original Java testcontainers library, achieving 100% Java feature parity with 48/48 core features implemented.

### Key Project Stats
- **Language**: Python 3.9+
- **Lines of Code**: ~14,500
- **Modules**: 58+ specialized container modules
- **Tests**: 510+ tests (100% pass rate)
- **Status**: Production-ready

## Project Structure

```
testcontainers-java2py/
├── src/testcontainers/          # Main Python package
│   ├── core/                    # Core container classes
│   │   ├── generic_container.py # Base container class
│   │   ├── docker_client.py     # Docker client wrapper
│   │   ├── resource_reaper.py   # Ryuk cleanup implementation
│   │   └── ...
│   ├── modules/                 # Specialized container modules
│   │   ├── postgres.py          # PostgreSQL container
│   │   ├── mysql.py             # MySQL container
│   │   ├── mongodb.py           # MongoDB container
│   │   └── ...                  # 58+ modules
│   ├── waiting/                 # Wait strategies
│   │   ├── port.py              # Port wait strategy
│   │   ├── http.py              # HTTP wait strategy
│   │   ├── log.py               # Log message wait strategy
│   │   └── exec.py              # Command execution wait strategy
│   ├── images/                  # Image handling
│   ├── compose/                 # Docker Compose support
│   └── pytest/                  # pytest plugin
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── pyproject.toml               # Python project config
└── PROJECT_STATUS.md            # Comprehensive status doc
```

## Python & Typing Requirements

### Strict Typing Policy

**CRITICAL**: This project enforces strict typing throughout the codebase.

#### Type Hints Requirements
- **Use typing everywhere**: All functions, methods, and variables must have type hints
- **Avoid `Any` type**: Try to use specific types instead of `Any`
  - ❌ Bad: `def process(data: Any) -> Any:`
  - ✅ Good: `def process(data: dict[str, str]) -> list[str]:`
- **Use `from __future__ import annotations`** at the top of every module for forward references
- **Prefer built-in types** (Python 3.9+): Use `list`, `dict`, `tuple` instead of `List`, `Dict`, `Tuple` from typing
- **Use `Optional[T]`** explicitly instead of `T | None` for Python 3.9 compatibility

#### mypy Configuration
The project uses strict mypy checking (see `pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
```

#### Example of Correct Typing
```python
from __future__ import annotations

from typing import Optional, Sequence
from docker.models.containers import Container as DockerContainer

class PostgreSQLContainer:
    def __init__(
        self,
        image: str = "postgres:9.6.12",
        username: str = "test",
        password: str = "test",
        dbname: str = "test",
    ) -> None:
        ...
    
    def with_exposed_ports(self, *ports: int) -> PostgreSQLContainer:
        """Expose ports from the container."""
        return self
    
    def get_connection_url(self) -> str:
        """Get the JDBC connection URL."""
        return f"postgresql://{self.get_host()}:{self.get_port()}/{self.dbname}"
```

## Testing with pytest

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_container.py

# Run with coverage
pytest --cov=testcontainers --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_container.py::TestExecResult::test_create_exec_result
```

### Test Configuration
Tests are configured in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### Test Structure
- Tests live in `tests/` directory
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Test files must start with `test_`
- Test classes must start with `Test`
- Test functions must start with `test_`

### Writing Tests
```python
"""Tests for container functionality."""

from __future__ import annotations

import pytest

from testcontainers.core.generic_container import GenericContainer


class TestGenericContainer:
    """Tests for GenericContainer class."""

    def test_create_container(self) -> None:
        """Test creating a basic container."""
        container = GenericContainer("alpine:latest")
        assert container.image == "alpine:latest"

    def test_with_exposed_ports(self) -> None:
        """Test exposing ports."""
        container = GenericContainer("nginx:latest")
        container.with_exposed_ports(80, 443)
        assert 80 in container.ports
        assert 443 in container.ports
```

## Code Quality Tools

### Linting and Formatting

```bash
# Run ruff linter
ruff check src/ tests/

# Run ruff auto-fix
ruff check --fix src/ tests/

# Format with ruff
ruff format src/ tests/

# Type checking with mypy
mypy src/
```

### Ruff Configuration
```toml
[tool.ruff]
line-length = 100
target-version = "py39"
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "T20"]
```

## Development Guidelines

### Code Style
1. **Line length**: Maximum 100 characters
2. **Imports**: Use absolute imports, organize with `ruff`
3. **Docstrings**: Use Google-style docstrings for classes and public methods
4. **Comments**: Minimal comments; let code be self-documenting
5. **Error handling**: Use specific exception types, not bare `except:`

### Module Development Pattern
When creating new container modules:

1. **Inherit from appropriate base class**:
   - Databases: Inherit from `JdbcDatabaseContainer`
   - Others: Inherit from `GenericContainer`

2. **Include Java source reference**:
```python
"""
PostgreSQL container implementation.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/postgresql/src/main/java/org/testcontainers/containers/PostgreSQLContainer.java
"""
```

3. **Follow naming conventions**:
   - Class names: `PostgreSQLContainer`, `MySQLContainer` (match Java)
   - File names: `postgres.py`, `mysql.py` (lowercase with underscores)
   - Constants: `POSTGRESQL_PORT`, `DEFAULT_IMAGE` (uppercase)

4. **Implement fluent API**:
```python
def with_username(self, username: str) -> PostgreSQLContainer:
    """Set the database username."""
    self.username = username
    return self
```

5. **Add comprehensive docstrings**:
```python
class PostgreSQLContainer(JdbcDatabaseContainer):
    """
    PostgreSQL database container.

    This container starts a PostgreSQL database instance with configurable
    credentials and database name.

    Java source:
    https://github.com/testcontainers/...

    Example:
        >>> with PostgreSQLContainer() as postgres:
        ...     url = postgres.get_jdbc_url()
        ...     # Connect to PostgreSQL
    """
```

### Common Patterns

#### Context Manager Usage
```python
# Preferred: Use context manager
with PostgreSQLContainer() as postgres:
    connection = psycopg2.connect(postgres.get_connection_url())
    # Use connection
# Container is automatically cleaned up

# Alternative: Manual lifecycle
postgres = PostgreSQLContainer()
postgres.start()
try:
    # Use container
    pass
finally:
    postgres.stop()
```

#### Wait Strategies
```python
from testcontainers.waiting import HttpWaitStrategy, LogMessageWaitStrategy

container = GenericContainer("myapp:latest")
container.with_exposed_ports(8080)
container.waiting_for(
    HttpWaitStrategy("/health", status_codes=[200])
    .with_timeout(timedelta(seconds=30))
)
```

## Dependencies

### Core Dependencies
- `docker>=6.0.0,<8.0.0` - Docker client library
- `pyyaml>=6.0.0` - Docker Compose support
- `tomli>=2.0.0` - TOML config (Python <3.11)
- `typing-extensions>=4.0.0` - Type hints (Python <3.11)

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `mypy>=1.0.0` - Type checking
- `ruff>=0.1.0` - Linting and formatting

## Important Notes

### Java Parity
This project maintains 100% feature parity with testcontainers-java:
- All 48 core features implemented
- 58+ specialized container modules
- Ryuk/ResourceReaper for automatic cleanup
- All wait strategies
- Database init scripts
- Docker Compose support

### Docker Requirements
- Docker daemon must be running
- Tests require Docker to execute
- Some tests use Docker-in-Docker

### Environment Variables
Testcontainers respects several environment variables:
- `TESTCONTAINERS_RYUK_DISABLED` - Disable Ryuk cleanup
- `DOCKER_HOST` - Docker daemon socket
- `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE` - Override socket path

## Common Tasks

### Add a New Container Module

1. Create file in `src/testcontainers/modules/`:
```python
from __future__ import annotations

from testcontainers.core import GenericContainer

class MyServiceContainer(GenericContainer):
    """MyService container implementation."""
    
    DEFAULT_IMAGE = "myservice:latest"
    DEFAULT_PORT = 8080
    
    def __init__(self, image: str = DEFAULT_IMAGE) -> None:
        super().__init__(image)
        self.with_exposed_ports(self.DEFAULT_PORT)
```

2. Add tests in `tests/unit/test_myservice.py`:
```python
from testcontainers.modules.myservice import MyServiceContainer

def test_myservice_container() -> None:
    with MyServiceContainer() as service:
        assert service.get_exposed_port(8080) > 0
```

3. Run tests:
```bash
pytest tests/unit/test_myservice.py
```

### Update Dependencies

```bash
# Install/update development dependencies
pip install -e ".[dev]"

# Or with uv (faster)
uv sync --all-groups
```

## Resources

- **Main Documentation**: [PROJECT_STATUS.md](../../PROJECT_STATUS.md)
- **Java Testcontainers**: https://java.testcontainers.org
- **Java Source**: https://github.com/testcontainers/testcontainers-java
- **Contributing Guide**: [CONTRIBUTING.md](../../CONTRIBUTING.md)

## When Making Changes

1. ✅ **Always** add type hints to all new code
2. ✅ **Always** avoid using `Any` type when possible
3. ✅ **Always** run tests with pytest
4. ✅ **Always** run mypy to check types
5. ✅ **Always** run ruff to check style
6. ✅ **Always** format with ruff
7. ✅ **Always** add docstrings to public APIs
8. ✅ **Always** include Java source references for modules
9. ✅ **Always** maintain feature parity with Java implementation
10. ✅ **Always** write tests for new functionality

---

**Last Updated**: 2026-02-09
**Python Version**: 3.9+
**Project Status**: Production Ready (100% Java Parity)
