# Docker Client Conversion Documentation

## Overview

This document describes the conversion of the Docker Client wrapper from Java to Python.

## Files Converted

### Java Source Files
1. **DockerClientFactory.java** (405 lines)
   - Main factory class for creating and caching Docker clients
   - Singleton pattern implementation
   - Provider strategy management
   
2. **DelegatingDockerClient.java** (13 lines)
   - Simple wrapper around Docker client using Lombok @Delegate
   
3. **dockerclient/DockerClientProviderStrategy.java** (partial)
   - Strategy pattern for Docker client configuration
   - Detection and initialization logic

### Python Output
- **src/testcontainers/core/docker_client.py** (~300 lines)
  - Combined all Java classes into single cohesive module
  - Simplified strategy to use docker-py's built-in configuration

## Key Conversions

### 1. Singleton Pattern
**Java:**
```java
private static DockerClientFactory instance;

public static synchronized DockerClientFactory instance() {
    if (instance == null) {
        instance = new DockerClientFactory();
    }
    return instance;
}
```

**Python:**
```python
_instance: Optional[DockerClientFactory] = None
_lock = threading.Lock()

@classmethod
def instance(cls) -> DockerClientFactory:
    if cls._instance is None:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
    return cls._instance
```

### 2. Lazy Client
**Java:**
```java
public static DockerClient lazyClient() {
    return new DockerClientDelegate() {
        @Override
        protected DockerClient getDockerClient() {
            return instance().client();
        }
    };
}
```

**Python:**
```python
class LazyDockerClient:
    def __init__(self, factory: DockerClientFactory):
        self._factory = factory
        self._client: Optional[DockerClient] = None
    
    def __getattr__(self, name: str) -> Any:
        if self._client is None:
            self._client = self._factory.client()
        return getattr(self._client, name)
```

### 3. Delegating Client
**Java (using Lombok):**
```java
@RequiredArgsConstructor
class DelegatingDockerClient implements DockerClient {
    @Delegate
    private final DockerClient dockerClient;
}
```

**Python:**
```python
class DockerClientWrapper:
    def __init__(self, client: DockerClient):
        self._client = client
    
    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
```

## Design Decisions

### 1. Simplified Configuration Strategy
The Java implementation uses a complex `ServiceLoader` pattern with multiple provider strategies. The Python version simplifies this by:
- Using `docker.from_env()` which handles most configuration automatically
- Supporting DOCKER_HOST and other standard environment variables
- Maintaining compatibility with docker-py's configuration

### 2. Direct docker-py Integration
Instead of wrapping docker-java's API, we use docker-py directly:
- Cleaner integration with Python ecosystem
- Better type hints and IDE support
- Familiar API for Python developers

### 3. Thread Safety
Both implementations maintain thread safety:
- Java: `@Synchronized` annotation
- Python: `threading.Lock()` for singleton initialization

### 4. Marker Labels
Maintained the same labeling system for container identification:
```python
{
    "org.testcontainers": "true",
    "org.testcontainers.lang": "python",  # Changed from "java"
    "org.testcontainers.version": "0.1.0"
}
```

## Features Implemented

✅ Singleton DockerClientFactory
✅ Lazy client initialization
✅ Client caching
✅ Failure caching (fail-fast on repeated errors)
✅ Docker availability checking
✅ Docker host IP detection
✅ Connection logging and diagnostics
✅ Thread-safe initialization
✅ Marker labels for container identification

## Features Simplified/Deferred

The following Java features were simplified or deferred for initial implementation:

- ❌ Multiple provider strategies (ServiceLoader pattern)
- ❌ Docker Machine detection
- ❌ Rootless Docker specific handling
- ❌ Named pipe socket support (Windows)
- ❌ Custom transport configurations
- ❌ Audit logging client wrapper

These can be added incrementally as needed.

## Testing

Comprehensive unit tests cover:
- Singleton behavior
- Lazy initialization
- Client caching
- Error handling and caching
- Docker availability checking
- IP address determination
- Marker labels generation

Run tests:
```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_docker_client.py -v
```

## Usage Example

```python
from testcontainers.core.docker_client import DockerClientFactory

# Get the singleton factory
factory = DockerClientFactory.instance()

# Check if Docker is available
if factory.is_docker_available():
    # Get a Docker client
    client = factory.client()
    
    # Use the client
    containers = client.containers.list()
    print(f"Running containers: {len(containers)}")
    
# Or use a lazy client
lazy_client = DockerClientFactory.lazy_client()
# Client is only initialized when first used
containers = lazy_client.containers.list()
```

## Dependencies

- **docker** (>=6.0.0) - Official Python Docker SDK
- Python 3.9+

## Future Enhancements

1. Add provider strategy pattern for advanced configurations
2. Support for custom Docker configurations
3. Enhanced Windows support (named pipes)
4. Connection pool management
5. Async client support
6. More detailed Docker environment detection

## Notes

- The Python version is more concise (~300 lines vs ~800+ lines in Java)
- Type hints provide better IDE support than Java generics in this context
- Python's `__getattr__` provides cleaner delegation than Java's @Delegate annotation
- Thread safety is explicit with locks rather than annotations
