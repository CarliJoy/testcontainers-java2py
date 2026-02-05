# Core Library Enhancement Plan - Testcontainers Python

## Project Overview

**Testcontainers** is a library that supports tests by providing lightweight, throwaway instances of common databases, Selenium web browsers, or anything else that can run in a Docker container.

**Source (Java Implementation):**
- 755 Java source files
- ~68,000 lines of Java code
- Core library + 63 specialized modules
- Gradle-based build system
- Java 17 toolchain, targeting Java 8

**Target:**
- Enhance existing testcontainers-python project (https://testcontainers-python.readthedocs.io/)
- Port core library features and patterns from Java implementation
- Focus on core library first, modules later
- Use `uv` for package management
- Follow Python standards (PEP 8, PEP 484, etc.)

## High-Level Enhancement Steps

### 1. **Assessment and Gap Analysis**
   - Clone and analyze testcontainers-python repository
   - Compare Java core library features with Python implementation
   - Identify missing features and patterns in Python version
   - Map Java core classes to Python equivalents
   - Document feature gaps and enhancement opportunities
   - Prioritize features based on impact and complexity

### 2. **Development Environment Setup**
   - Install `uv` package manager (https://docs.astral.sh/uv/)
   - Set up local development environment with uv
   - Configure code quality tools:
     - `ruff` for linting and formatting (replaces black + flake8)
     - `mypy` for static type checking
     - `pytest` for testing
   - Set up pre-commit hooks for code quality
   - Review Python packaging standards (PEP 517, PEP 621)

### 3. **Core Library Enhancement - Phase 1**

   **Focus Areas (Priority Order):**
   
   1. **GenericContainer Enhancements**
      - Review Java GenericContainer implementation
      - Add missing configuration options
      - Improve builder pattern support
      - Enhanced port mapping capabilities
      - Better environment variable handling
      - Volume mounting improvements
   
   2. **Wait Strategies**
      - Port advanced wait strategies from Java
      - HTTP wait strategy enhancements
      - Log wait strategy improvements
      - Custom wait strategy support
      - Composable wait strategies
   
   3. **Network Management**
      - Network creation and configuration
      - Container network aliases
      - Network mode options
      - Inter-container networking
   
   4. **Lifecycle Management**
      - Startup hooks and callbacks
      - Container reuse patterns
      - Cleanup and resource management
      - Graceful shutdown handling
   
   5. **Image Handling**
      - Image pulling strategies
      - Registry authentication
      - Image from Dockerfile support
      - Image substitution patterns
   
   6. **Docker Client Integration**
      - Connection configuration
      - TLS support improvements
      - Docker context support
      - Better error handling and diagnostics

### 4. **Implementation Best Practices**

   **Python Standards:**
   - Follow PEP 8 style guide
   - Use PEP 484 type hints throughout
   - Apply PEP 257 for docstrings
   - Use dataclasses (PEP 557) where appropriate
   - Follow PEP 621 for project metadata
   
   **Code Quality:**
   - Type hints on all public APIs
   - Comprehensive docstrings (Google or NumPy style)
   - Unit tests for all new features (aim for >90% coverage)
   - Integration tests for key workflows
   - Use context managers for resource management
   
   **Dependencies:**
   - Minimize external dependencies
   - Use standard library where possible
   - docker-py for Docker client interaction
   - pytest for testing framework
   - Keep dependency tree shallow and well-maintained

### 5. **Testing Strategy**
   
   **Test Organization:**
   - Unit tests for individual components
   - Integration tests for Docker interactions
   - Example-based tests demonstrating usage patterns
   - Test on multiple Python versions (3.9, 3.10, 3.11, 3.12, 3.13+)
   
   **Test Coverage:**
   - Aim for >90% code coverage for core library
   - Test edge cases and error conditions
   - Performance benchmarks for critical paths
   - Compatibility tests with various Docker versions
   
   **Test Tools:**
   - pytest as primary testing framework
   - pytest-cov for coverage reporting
   - pytest-timeout for hanging tests
   - pytest-xdist for parallel test execution

### 6. **Documentation Updates**
   
   **For Each Enhanced Feature:**
   - Clear docstrings with examples
   - Type hints for IDE support
   - Migration notes from Java patterns
   - Usage examples comparing with Java
   
   **Documentation Structure:**
   - API reference with type information
   - How-to guides for common patterns
   - Examples ported from Java
   - Feature comparison matrix (Java vs Python)

### 7. **API Design Principles**
   
   **Pythonic Patterns:**
   - Context managers (`with` statement) for container lifecycle
   - Fluent interfaces with method chaining
   - Sensible defaults, explicit configuration when needed
   - Duck typing with protocol classes where appropriate
   - Generator expressions for lazy evaluation
   
   **Modern Python Features:**
   - Type hints with `typing` module
   - Dataclasses for configuration objects
   - Async/await support (optional, for advanced users)
   - Pattern matching (Python 3.10+) where beneficial
   - `pathlib` for file operations
   
   **Backward Compatibility:**
   - Maintain existing testcontainers-python API
   - Add new features as opt-in enhancements
   - Deprecation warnings for breaking changes
   - Clear migration path documentation

### 8. **Code Organization**
   
   **Module Structure:**
   ```
   testcontainers/
   ├── core/              # Core container abstractions
   ├── core/waiting.py    # Wait strategies
   ├── core/network.py    # Network management
   ├── core/image.py      # Image handling
   ├── core/config.py     # Configuration
   └── core/docker_client.py  # Docker client wrapper
   ```
   
   **Separation of Concerns:**
   - Clear interfaces between components
   - Dependency injection for testability
   - Minimize coupling between modules
   - Well-defined public APIs with private implementation

## Key Technical Considerations

### Language Feature Mapping

| Java Feature | Python Equivalent |
|-------------|------------------|
| Classes & Inheritance | Classes & Inheritance (similar) |
| Interfaces | Abstract Base Classes (abc.ABC) |
| Generics | Type hints (typing.Generic) |
| Annotations | Decorators |
| Try-with-resources | Context managers (with statement) |
| Streams API | List comprehensions, generators |
| Optional<T> | Optional type hints (typing.Optional) |
| CompletableFuture | asyncio.Future |
| Builder pattern | Fluent interfaces or factory functions |

### Architectural Decisions

1. **Docker Client Library:**
   - Use docker-py (official Python Docker SDK)
   - Wrapper layer for testcontainers-specific functionality

2. **Testing Framework Integration:**
   - Primary: pytest with fixtures
   - Optional: unittest compatibility layer

3. **Configuration:**
   - Use environment variables (consistent with Java)
   - Python configuration files (.ini, .toml, or .yaml)

4. **Async Support:**
   - Consider asyncio for concurrent container operations
   - Provide both sync and async APIs if beneficial

5. **Type Safety:**
   - Use mypy for static type checking
   - Comprehensive type hints in public APIs

## Risks and Mitigation

| Risk | Mitigation Strategy |
|------|-------------------|
| Feature incompatibility | Document differences, provide migration guide |
| Performance differences | Benchmark critical paths, optimize as needed |
| Library ecosystem gaps | Identify and select appropriate Python libraries early |
| Community adoption | Engage early, provide excellent documentation |
| Maintenance burden | Automated testing, clear contribution guidelines |
| Existing Python project overlap | Evaluate collaboration or differentiation strategy |

## Feature Enhancement Roadmap

### Phase 1: Core Container Enhancements (Weeks 1-4)
- [ ] Analyze Java GenericContainer vs Python implementation
- [ ] Port missing container configuration options
- [ ] Enhance port mapping and exposure
- [ ] Improve environment variable handling
- [ ] Add volume mounting improvements
- [ ] Comprehensive tests for enhancements

### Phase 2: Wait Strategies (Weeks 5-6)
- [ ] Port advanced wait strategies from Java
- [ ] HTTP/HTTPS wait with custom matchers
- [ ] Log-based wait strategies
- [ ] HealthCheck wait strategy
- [ ] Composable wait strategies
- [ ] Examples and documentation

### Phase 3: Network & Lifecycle (Weeks 7-9)
- [ ] Network creation and configuration
- [ ] Container reuse patterns
- [ ] Startup/shutdown hooks
- [ ] Resource cleanup improvements
- [ ] Integration tests

### Phase 4: Image & Docker Client (Weeks 10-12)
- [ ] Image pulling strategies
- [ ] Registry authentication
- [ ] Build from Dockerfile support
- [ ] Docker client configuration enhancements
- [ ] Error handling improvements

## Success Metrics

**Core Library Enhancements:**
- [ ] Feature parity assessment document created
- [ ] >90% test coverage for new code
- [ ] Type hints on all public APIs
- [ ] Documentation with examples for each feature
- [ ] Performance benchmarks show no regression
- [ ] All new features have integration tests

**Code Quality:**
- [ ] Passes `ruff` linting with no errors
- [ ] Passes `mypy` type checking in strict mode
- [ ] Pre-commit hooks configured and passing
- [ ] Code reviews completed for all changes

## Development Workflow with `uv`

**Initial Setup:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone testcontainers-python
git clone https://github.com/testcontainers/testcontainers-python.git

# Create virtual environment and install dependencies
cd testcontainers-python
uv venv
source .venv/bin/activate  # Linux/macOS
# On Windows: .venv\Scripts\activate.bat (cmd) or .venv\Scripts\Activate.ps1 (PowerShell)
uv pip install -e ".[dev]"
```

**Development Cycle:**
```bash
# Install/update dependencies
uv pip install -r requirements.txt

# Run tests
pytest

# Run type checking
mypy testcontainers

# Run linting
ruff check .
ruff format .

# Run specific test
pytest tests/test_core.py -v
```

## Recommended Approach

**Iterative Enhancement Strategy:**

1. **Week 1-2**: Environment setup + gap analysis
   - Set up development environment with uv
   - Clone and thoroughly analyze testcontainers-python
   - Create detailed feature comparison spreadsheet
   - Identify quick wins vs. complex enhancements

2. **Week 3-4**: First core enhancements
   - Start with highest-impact, lowest-complexity features
   - Ensure each enhancement has tests and docs
   - Get feedback from maintainers early

3. **Week 5+**: Continue iterative enhancements
   - One feature area at a time
   - Test thoroughly before moving to next area
   - Regular check-ins with project maintainers
   - Continuous documentation updates

4. **Throughout**: Follow Python best practices
   - Write idiomatic Python code
   - Comprehensive type hints
   - Clear, concise documentation
   - Test-driven development approach

## Next Steps

1. **Immediate Actions:**
   - [ ] Install `uv` and set up development environment
   - [ ] Clone testcontainers-python repository
   - [ ] Familiarize with existing codebase structure
   - [ ] Set up development tools (ruff, mypy, pytest)

2. **First Week Goals:**
   - [ ] Create feature comparison matrix (Java vs Python)
   - [ ] Identify top 10 missing features in Python
   - [ ] Prioritize features by impact/effort ratio
   - [ ] Create detailed plan for first enhancement

3. **Ongoing:**
   - [ ] Regular commits with clear messages
   - [ ] Write tests before implementing features
   - [ ] Update documentation as you go
   - [ ] Engage with testcontainers-python maintainers
