# Java Origin - Original testcontainers-java Source

This directory contains the original Java implementation of Testcontainers that served as the reference for the Python implementation.

## What's Included

This folder contains:

- **Java source code**: The complete original Java implementation
  - `core/` - Core Testcontainers functionality
  - `modules/` - All specialized container modules (PostgreSQL, MySQL, Kafka, Elasticsearch, etc.)
  - `test-support/` - Test utilities
  - `examples/` - Java usage examples
  
- **Build system**: Gradle build configuration
  - `build.gradle`, `settings.gradle` - Main build files
  - `gradle/`, `gradlew`, `gradlew.bat` - Gradle wrapper
  - `buildSrc/` - Custom Gradle build logic
  
- **CI/CD pipelines**: Original Java CI/CD configurations
  - `.github/workflows/` - GitHub Actions workflows for Java
  - `.circleci/` - CircleCI configuration
  - `azure-pipelines.yml` - Azure Pipelines configuration
  
- **Configuration**: Java-specific configuration files
  - `.devcontainer/` - VS Code devcontainer for Java development
  - `.idea/` - IntelliJ IDEA project settings
  - `config/` - Checkstyle and other Java tools configuration
  - `.sdkmanrc` - SDKMAN configuration
  - `mkdocs.yml` - Java documentation site configuration
  
- **Documentation**: Original Java documentation
  - `docs/` - Documentation site source files

## Purpose

This directory serves as:

1. **Reference Material**: The authoritative source for understanding the original Java API and implementation details during the Python conversion
2. **Documentation**: Examples and patterns from the original implementation
3. **Historical Record**: Preservation of the original codebase structure

## Python Implementation

The Python implementation is located in the repository root:
- `src/testcontainers/` - Python source code
- `tests/` - Python tests
- `pyproject.toml` - Python package configuration

## Original Repository

This code originated from: https://github.com/testcontainers/testcontainers-java

## License

See the [LICENSE](../LICENSE) file in the repository root. The original Java code is:
- Copyright (c) 2015 - 2021 Richard North and other authors
- MS SQL Server module is (c) 2017 - 2021 G DATA Software AG and other authors
- Hashicorp Vault module is (c) 2017 - 2021 Capital One Services, LLC and other authors
