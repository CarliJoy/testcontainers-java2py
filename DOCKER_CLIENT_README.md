# Docker Client Wrapper - Python Implementation

This directory contains the Python implementation of the Testcontainers Docker Client wrapper, converted from the Java implementation.

## Location

```
src/testcontainers/core/docker_client.py
```

## What's Included

### Classes

1. **DockerClientFactory** - Singleton factory for creating and managing Docker clients
   - Thread-safe singleton implementation
   - Client caching
   - Docker availability checking
   - Host IP detection
   
2. **DockerClientWrapper** - Simple wrapper around docker-py client
   - Delegates all operations to underlying client
   - Prevents closing of global client
   
3. **LazyDockerClient** - Lazy-loading client wrapper
   - Defers client initialization until first use
   - Useful for avoiding early Docker checks

## Quick Start

```python
from testcontainers.core.docker_client import DockerClientFactory

# Get the factory instance
factory = DockerClientFactory.instance()

# Check if Docker is available
if factory.is_docker_available():
    # Get a client
    client = factory.client()
    
    # Use it
    containers = client.containers.list()
    print(f"Running containers: {len(containers)}")
```

## Testing

Run the comprehensive test suite:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_docker_client.py -v
```

All 16 tests should pass.

## Example

See `examples/docker_client_example.py` for a complete working example:

```bash
PYTHONPATH=src python3 examples/docker_client_example.py
```

## Documentation

For detailed conversion notes, design decisions, and feature comparisons with the Java version, see:
- `DOCKER_CLIENT_CONVERSION.md` - Full conversion documentation

## Dependencies

- **docker** >= 6.0.0 - Official Python Docker SDK
- Python >= 3.9

## Features

✅ **Implemented:**
- Singleton pattern with thread safety
- Lazy client initialization
- Client and failure caching
- Docker availability checking
- Host IP detection
- Marker labels for container identification
- Comprehensive logging
- Type hints throughout

📋 **Simplified from Java:**
- Uses docker-py's built-in configuration (no custom provider strategies)
- Direct integration with Python ecosystem
- More concise implementation

## Architecture

```
DockerClientFactory (Singleton)
├── client() -> DockerClient (cached)
├── lazy_client() -> LazyDockerClient
├── is_docker_available() -> bool
└── marker_labels() -> Dict[str, str]

DockerClientWrapper
└── Delegates to docker.DockerClient

LazyDockerClient
└── Proxies to factory.client() on first use
```

## Thread Safety

The implementation is thread-safe:
- Singleton initialization uses double-checked locking with `threading.Lock()`
- Client instance is cached after first creation
- Multiple threads can safely call `instance()` and `client()`

## Error Handling

- Failures during client creation are cached
- Subsequent calls fail fast with the cached exception
- Use `is_docker_available()` to check before accessing client
- Reset factory with `DockerClientFactory.reset()` (testing only)

## Next Steps

To use this in container implementations:

```python
from testcontainers.core.docker_client import DockerClientFactory

class GenericContainer:
    def __init__(self):
        # Get lazy client - only initializes when needed
        self.docker_client = DockerClientFactory.lazy_client()
    
    def start(self):
        # Client is initialized here on first use
        container = self.docker_client.containers.run(...)
```

## Contributing

When adding features:
1. Add type hints
2. Write tests
3. Update documentation
4. Follow existing patterns

## License

Same as the main testcontainers project.
