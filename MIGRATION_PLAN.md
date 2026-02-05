# Java-to-Python Direct Conversion Plan - Testcontainers

## Project Overview

**Testcontainers** is a library that supports tests by providing lightweight, throwaway instances of common databases, Selenium web browsers, or anything else that can run in a Docker container.

**Source (Java Implementation):**
- 755 Java source files
- ~68,000 lines of Java code
- Core library + 63 specialized modules
- Gradle-based build system
- Java 17 toolchain (compiles to Java 8 bytecode for compatibility)
- Note: Source uses Java 8 features; newer Java features not required for conversion

**Approach:**
- **Direct conversion** of Java code to Python (no comparison with existing implementations)
- Start with core library, then convert modules
- Use `uv` for package management
- Follow Python standards (PEP 8, PEP 484, etc.)
- Automated conversion where possible, manual refinement where needed

## Direct Conversion Steps

### 1. **Development Environment Setup**
   - Install `uv` package manager (https://docs.astral.sh/uv/)
   - Set up Python project structure with `uv init`
   - Configure code quality tools:
     - `ruff` for linting and formatting
     - `mypy` for static type checking
     - `pytest` for testing
   - Set up pre-commit hooks for code quality
   - Create pyproject.toml with project metadata (PEP 621)

### 2. **Conversion Tooling Setup**
   - Evaluate Java-to-Python conversion tools:
     - Consider tools like `j2py`, `java2python`, or manual conversion
     - Set up custom conversion scripts for common patterns
   - Create conversion mapping document:
     - Java → Python type mappings
     - Common idiom translations
     - Library equivalents (docker-java → docker-py)
   - Prepare test infrastructure to validate conversions

### 3. **Core Library Conversion - Phase 1**

   **Conversion Priority Order:**
   
   1. **Base Classes and Interfaces**
      - `GenericContainer.java` → `generic_container.py`
      - `Container.java` → `container.py` (interface/protocol)
      - `ContainerState.java` → `container_state.py`
      - Common base abstractions
   
   2. **Wait Strategies**
      - `WaitStrategy.java` → `wait_strategy.py` (base)
      - `HttpWaitStrategy.java` → `http_wait_strategy.py`
      - `LogMessageWaitStrategy.java` → `log_wait_strategy.py`
      - `HealthCheckWaitStrategy.java` → `health_check_wait_strategy.py`
      - Other wait strategy implementations
   
   3. **Docker Client Wrapper**
      - `DockerClientFactory.java` → `docker_client_factory.py`
      - `DockerClient` interactions → docker-py SDK calls
      - Connection configuration classes
      - Authentication handling
   
   4. **Network Support**
      - `Network.java` → `network.py`
      - Network configuration classes
      - Network lifecycle management
   
   5. **Image Handling**
      - `RemoteDockerImage.java` → `remote_docker_image.py`
      - `ImageFromDockerfile.java` → `image_from_dockerfile.py`
      - Image pulling and caching logic
   
   6. **Lifecycle and Utilities**
      - Lifecycle hooks and callbacks
      - Resource cleanup mechanisms
      - Utility classes and helpers

### 4. **Conversion Process for Each File**

   **Step-by-Step Conversion:**
   
   1. **Analyze Java Source**
      - Understand class purpose and responsibilities
      - Identify dependencies and imports
      - Note Java-specific patterns (annotations, generics, etc.)
   
   2. **Initial Conversion**
      - Use conversion tool or manual translation
      - Convert class structure (class → class, interface → Protocol/ABC)
      - Translate method signatures with type hints
      - Convert basic logic (for loops, conditionals, etc.)
   
   3. **Pythonic Refinement**
      - Replace Java idioms with Python equivalents
      - Use list comprehensions, generators, context managers
      - Apply dataclasses for simple data structures
      - Implement `__enter__`/`__exit__` for resources
   
   4. **Dependency Translation**
      - Java Docker client → docker-py SDK
      - Java logging → Python logging module
      - Java collections → Python built-ins (list, dict, set)
      - Java Optional → None or typing.Optional
   
   5. **Testing**
      - Convert Java tests to pytest
      - Add Python-specific test cases
      - Ensure behavior matches Java version
      - Achieve >90% coverage

### 5. **Implementation Standards**

   **Python Code Quality:**
   - Follow PEP 8 style guide (enforced by ruff)
   - Use PEP 484 type hints throughout
   - Apply PEP 257 for docstrings (Google style)
   - Use dataclasses (PEP 557) for data structures
   - Follow PEP 621 for project metadata
   
   **Code Patterns:**
   - Context managers (`with` statement) for container lifecycle
   - Type hints on all public APIs
   - Comprehensive docstrings with examples
   - Use standard library where possible
   - Minimal external dependencies
   
   **Testing:**
   - Convert Java tests to pytest
   - Aim for >90% code coverage
   - Test on Python 3.9, 3.10, 3.11, 3.12+
   - Integration tests with real Docker
   - Performance benchmarks

### 6. **Documentation**
   
   **During Conversion:**
   - Convert JavaDoc to Python docstrings
   - Translate inline comments
   - Update examples from Java to Python syntax
   - Document conversion decisions and gotchas
   
   **Documentation Files:**
   - README.md with quickstart guide
   - API reference (auto-generated from docstrings)
   - Examples directory with Python equivalents of Java examples
   - CONVERSION_NOTES.md documenting Java→Python mappings

### 7. **Project Structure**

   **Python Package Layout:**
   ```
   testcontainers_python/          # Or use 'testcontainers' as package name
   ├── pyproject.toml              # Project metadata (PEP 621)
   ├── README.md
   ├── CONVERSION_NOTES.md         # Java→Python mapping notes
   ├── src/
   │   └── testcontainers/         # Main package (underscores only)
   │       ├── __init__.py
   │       ├── core/
   │       │   ├── __init__.py
   │       │   ├── generic_container.py
   │       │   ├── container.py        # Protocol/ABC
   │       │   ├── container_state.py
   │       │   └── docker_client.py
   │       ├── waiting/
   │       │   ├── __init__.py
   │       │   ├── wait_strategy.py    # Base class
   │       │   ├── http.py
   │       │   ├── log.py
   │       │   └── healthcheck.py
   │       ├── images/
   │       │   ├── __init__.py
   │       │   ├── remote_image.py
   │       │   └── dockerfile_image.py
   │       └── network.py
   ├── tests/
   │   ├── unit/
   │   └── integration/
   └── examples/
       └── (ported from Java examples/)
   ```

### 8. **Conversion Helpers**

   **Create Conversion Utilities:**
   - Script to extract Java class structure
   - Template generator for Python equivalents
   - Automated type mapping (String → str, etc.)
   - Import statement converter
   - Test case converter

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

## Conversion Roadmap

### Phase 1: Setup & Base Infrastructure (Week 1)
- [ ] Set up Python project with `uv init`
- [ ] Create pyproject.toml with dependencies
- [ ] Set up ruff, mypy, pytest configuration
- [ ] Create project structure (src/, tests/, examples/)
- [ ] Document Java→Python type mappings
- [ ] Create conversion helper scripts

### Phase 2: Core Container Classes (Weeks 2-4)
- [ ] Convert Container interface/protocol
- [ ] Convert GenericContainer base class
- [ ] Convert ContainerState
- [ ] Convert DockerClientFactory
- [ ] Port core container lifecycle methods
- [ ] Write tests for core functionality

### Phase 3: Wait Strategies (Weeks 5-6)
- [ ] Convert WaitStrategy base class
- [ ] Convert HttpWaitStrategy
- [ ] Convert LogMessageWaitStrategy
- [ ] Convert HealthCheckWaitStrategy
- [ ] Convert other wait strategies
- [ ] Write comprehensive wait strategy tests

### Phase 4: Images & Network (Weeks 7-8)
- [ ] Convert RemoteDockerImage
- [ ] Convert ImageFromDockerfile
- [ ] Convert Network classes
- [ ] Port image pulling and caching logic
- [ ] Write image and network tests

### Phase 5: Testing & Examples (Weeks 9-10)
- [ ] Convert Java test suite to pytest
- [ ] Port example applications from examples/
- [ ] Integration testing with real containers
- [ ] Performance benchmarking
- [ ] Documentation review

### Phase 6: Modules (Weeks 11+)
- [ ] Convert module classes (PostgreSQL, MySQL, etc.)
- [ ] One module at a time, based on priority
- [ ] Each module: convert code, tests, examples

## Success Metrics

**Conversion Completeness:**
- [ ] All core library classes converted to Python
- [ ] All wait strategies ported
- [ ] Image and network support fully converted
- [ ] At least 10 most-used modules converted
- [ ] Test suite converted and passing

**Code Quality:**
- [ ] >90% test coverage for converted code
- [ ] Type hints on all public APIs
- [ ] Passes `ruff` linting with no errors
- [ ] Passes `mypy` type checking in strict mode
- [ ] All tests passing on Python 3.9, 3.10, 3.11, 3.12+

**Documentation:**
- [ ] README with quickstart examples
- [ ] API documentation generated from docstrings
- [ ] Examples ported from Java
- [ ] CONVERSION_NOTES.md documenting mappings

## Development Workflow with `uv`

**Initial Project Setup:**
```bash
# Install uv (see https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create new Python project
# Note: Use underscores or simple names for package/import names
# (hyphens are only allowed in distribution names, not import names)
# 'testcontainers' (no hyphens/underscores) is valid, 'testcontainers_python' is valid
mkdir testcontainers_python
cd testcontainers_python
uv init --lib  # Creates project structure

# The actual import package name is configured in pyproject.toml
# Edit pyproject.toml to set name = "testcontainers" if you want simpler imports

# Create virtual environment
uv venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows (cmd):
.venv/Scripts/activate.bat
# Windows (PowerShell):
.venv/Scripts/Activate.ps1

# Install dependencies
uv pip install docker pytest pytest-cov mypy ruff
uv pip install -e .
```

**Conversion Workflow:**
```bash
# 1. Pick a Java file to convert
# Example: core/src/main/java/org/testcontainers/containers/GenericContainer.java

# 2. Create Python equivalent structure
# src/testcontainers/core/generic_container.py

# 3. Convert the code (manual or with tools)
# - Translate class definition
# - Convert methods with type hints
# - Replace Java patterns with Python equivalents

# 4. Write/convert tests
# tests/unit/test_generic_container.py

# 5. Run tests
pytest tests/unit/test_generic_container.py -v

# 6. Check types and linting
mypy src/testcontainers
ruff check src/ tests/
ruff format src/ tests/

# 7. Commit when tests pass
git add src/testcontainers/core/generic_container.py tests/unit/test_generic_container.py
git commit -m "Convert GenericContainer from Java to Python"
```

**Continuous Testing:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=testcontainers --cov-report=html

# Run type checking
mypy src/testcontainers

# Run linting
ruff check .

# Format code
ruff format .
```

## Recommended Approach

**Direct Conversion Strategy:**

1. **Week 1**: Project setup
   - Set up Python project with `uv`
   - Create project structure
   - Configure tooling (ruff, mypy, pytest)
   - Document conversion mappings

2. **Weeks 2-4**: Convert core classes
   - Start with simplest classes (utilities, constants)
   - Then base interfaces/protocols
   - Then GenericContainer and main classes
   - Test each class as you convert it

3. **Weeks 5-6**: Convert wait strategies
   - Base wait strategy class first
   - Then concrete implementations
   - Comprehensive testing

4. **Weeks 7-8**: Convert images & networking
   - Image classes
   - Network support
   - Docker client wrapper

5. **Weeks 9-10**: Tests and examples
   - Convert test suite
   - Port examples
   - Integration testing

6. **Weeks 11+**: Module conversion
   - One module at a time
   - Focus on most popular modules first

**Throughout:**
- Convert one file at a time
- Write/convert tests immediately
- Run tests continuously
- Document tricky conversions
- Keep code Pythonic

## Next Steps

1. **Immediate Actions (Day 1):**
   - [ ] Install `uv`
   - [ ] Create new Python project structure
   - [ ] Set up pyproject.toml with dependencies
   - [ ] Configure ruff, mypy, pytest
   - [ ] Create CONVERSION_NOTES.md for tracking mappings

2. **First Week:**
   - [ ] Document Java→Python type mappings
   - [ ] Create conversion helper scripts (optional)
   - [ ] Convert first simple utility class
   - [ ] Set up test infrastructure
   - [ ] Establish conversion workflow

3. **Week 2 Onwards:**
   - [ ] Convert one Java file at a time
   - [ ] Write tests for each converted file
   - [ ] Keep CONVERSION_NOTES.md updated
   - [ ] Regular commits after each successful conversion
   - [ ] Build up core library systematically

## Conversion Tips

**Common Java→Python Patterns:**
- `public class Foo` → `class Foo:`
- `String` → `str`
- `int`, `Integer` → `int`
- `boolean` → `bool`
- `List<T>` → `list[T]` (use `from __future__ import annotations` for Python 3.9, or use `List[T]` from typing)
- `Map<K, V>` → `dict[K, V]` (use `from __future__ import annotations` for Python 3.9, or use `Dict[K, V]` from typing)
- `Optional<T>` → `Optional[T]` from typing module
- `T | None` → Available in Python 3.10+ (or with `from __future__ import annotations` in 3.9)
- `void method()` → `def method() -> None:`
- `@Override` → no equivalent (just document in docstring)
- `implements Interface` → `(Protocol)` or `(ABC)`
- `new Foo()` → `Foo()`
- `try-with-resources` → `with` statement
- `@Getter/@Setter` (Lombok) → `@property` or dataclass

**Typing Strategy:**
- Add `from __future__ import annotations` at the top of each file for forward-compatible annotations
- This allows using modern syntax (`list[str]`, `dict[str, int]`) even in Python 3.9
- Use `Optional[T]` from typing module for optional types (or `T | None` syntax with the __future__ import)

**Docker Client:**
- `DockerClient` (Java) → `docker.DockerClient` (docker-py)
- Most methods have similar names in docker-py

**Testing:**
- JUnit → pytest
- `@Test` → `def test_...()`
- `assertEquals` → `assert x == y`
- `assertTrue` → `assert condition`
- `@BeforeEach` → pytest fixtures
