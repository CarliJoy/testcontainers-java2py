# Testcontainers Python

> Python port of Testcontainers - a library that supports pytest tests, providing lightweight, throwaway instances of common databases, Selenium web browsers, or anything else that can run in a Docker container.

## Repository Organization

This repository contains:

- **Python Implementation** (main directory)
  - `src/testcontainers/` - Python source code
  - `tests/` - Python test suite
  - `pyproject.toml` - Python package configuration
  - See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed implementation status

- **Java Reference Implementation** (`java_origin/` directory)
  - Original Java testcontainers source code used as reference for the Python port
  - See [java_origin/README.md](java_origin/README.md) for details

## Quick Start

Install the package:

```bash
pip install testcontainers-python
```

Use a container in your tests:

```python
from testcontainers.postgres import PostgresContainer
import sqlalchemy

def test_with_postgres():
    with PostgresContainer("postgres:16") as postgres:
        engine = sqlalchemy.create_engine(postgres.get_connection_url())
        # Your test code here
```

## Documentation

- **Python Implementation**: See [PROJECT_STATUS.md](PROJECT_STATUS.md) for features, modules, and examples
- **Original Java Documentation**: https://java.testcontainers.org

## License

See [LICENSE](LICENSE).

## Copyright

Copyright (c) 2015 - 2021 Richard North and other authors.

MS SQL Server module is (c) 2017 - 2021 G DATA Software AG and other authors.

Hashicorp Vault module is (c) 2017 - 2021 Capital One Services, LLC and other authors.

See [contributors](https://github.com/testcontainers/testcontainers-java/graphs/contributors) for all contributors.
