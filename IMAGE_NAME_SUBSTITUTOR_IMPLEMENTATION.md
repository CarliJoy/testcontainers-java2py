# ImageNameSubstitutor Implementation Guide

This document describes the implementation of ImageNameSubstitutor in testcontainers-python.

## Overview

ImageNameSubstitutor allows automatic transformation of Docker image names before use. This is essential for enterprise environments that need to:

- Use private registry mirrors (avoid Docker Hub rate limits)
- Enforce corporate compliance policies
- Substitute specific image versions
- Audit and log all images used

## Architecture

### Protocol-Based Design

We use Python's `Protocol` for the interface, allowing structural typing:

```python
class ImageNameSubstitutor(Protocol):
    def substitute(self, image_name: str) -> str: ...
    def describe(self) -> str: ...
```

### Implementations

1. **NoOpImageNameSubstitutor** - Default, returns images unchanged
2. **PrefixingImageNameSubstitutor** - Adds registry prefix to Docker Hub images
3. **ConfigurableImageNameSubstitutor** - Maps specific images via configuration
4. **ChainImageNameSubstitutor** - Combines multiple substitutors

## Configuration

### Priority Order

1. **Programmatic** (highest) - `set_global_substitutor()`
2. **Environment Variables** - `TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX`
3. **TOML File** - `testcontainers.toml`
4. **Default** (lowest) - NoOp

### Environment Variables

```bash
export TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX=registry.corp.com/mirror
```

### TOML Configuration

Create `testcontainers.toml` in project root or `~/.testcontainers/`:

```toml
[hub]
image_name_prefix = "registry.corp.com/mirror"

[image_mappings]
"postgres:13" = "registry.corp.com/custom/postgres:13-patched"
"mysql:8.0" = "registry.corp.com/approved/mysql:8.0"
```

### Programmatic

```python
from testcontainers.images.substitutor import (
    PrefixingImageNameSubstitutor,
    set_global_substitutor
)

set_global_substitutor(PrefixingImageNameSubstitutor("myregistry.com"))
```

## Integration Points

The substitutor is integrated at two key points:

### 1. RemoteDockerImage

When pulling an image:

```python
from testcontainers.images.substitutor import get_image_name_substitutor

class RemoteDockerImage:
    def __init__(self, image_name: str, ...):
        substitutor = get_image_name_substitutor()
        self.image_name = substitutor.substitute(image_name)
```

### 2. GenericContainer

When initializing a container:

```python
from testcontainers.images.substitutor import get_image_name_substitutor

class GenericContainer:
    def __init__(self, image: str, ...):
        substitutor = get_image_name_substitutor()
        self.image = substitutor.substitute(image)
```

## Usage Examples

### Basic Usage (Automatic)

Just set the environment variable:

```bash
export TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX=registry.corp.com
```

Then use containers normally:

```python
from testcontainers.core import GenericContainer

# Image is automatically transformed:
# postgres:13 -> registry.corp.com/postgres:13
with GenericContainer("postgres:13") as container:
    container.with_exposed_ports(5432)
    # Use container...
```

### Custom Substitutor

Create a custom substitutor:

```python
from testcontainers.images.substitutor import ImageNameSubstitutor, set_global_substitutor

class VersionLockingSubstitutor:
    """Lock all images to specific versions."""
    
    VERSION_MAP = {
        "postgres": "postgres:13.8",
        "mysql": "mysql:8.0.31",
        "redis": "redis:7.0.5",
    }
    
    def substitute(self, image_name: str) -> str:
        # Extract base name
        base = image_name.split(":")[0]
        if base in self.VERSION_MAP:
            return self.VERSION_MAP[base]
        return image_name
    
    def describe(self) -> str:
        return "VersionLockingSubstitutor"

# Use it
set_global_substitutor(VersionLockingSubstitutor())
```

### Complex Chain

Combine multiple substitutors:

```python
from testcontainers.images.substitutor import (
    PrefixingImageNameSubstitutor,
    ConfigurableImageNameSubstitutor,
    ChainImageNameSubstitutor,
    set_global_substitutor,
)

# 1. Add registry prefix
prefix_sub = PrefixingImageNameSubstitutor("registry.corp.com")

# 2. Apply specific mappings
mappings = {
    "registry.corp.com/postgres:13": "registry.corp.com/custom/postgres:13-patched"
}
config_sub = ConfigurableImageNameSubstitutor(mappings)

# 3. Chain them together
chain = ChainImageNameSubstitutor(prefix_sub, config_sub)

set_global_substitutor(chain)

# Result: postgres:13 -> registry.corp.com/postgres:13 -> registry.corp.com/custom/postgres:13-patched
```

## Testing

The implementation includes comprehensive tests:

```python
# Test prefix substitutor
def test_adds_prefix():
    sub = PrefixingImageNameSubstitutor("registry.io")
    assert sub.substitute("postgres:13") == "registry.io/postgres:13"

# Test configuration loading
def test_loads_from_env(monkeypatch):
    monkeypatch.setenv("TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX", "registry.io")
    TestcontainersConfig.reset()
    
    sub = get_image_name_substitutor()
    assert sub.substitute("postgres:13") == "registry.io/postgres:13"
```

## Differences from Java Implementation

### Simplified Areas

1. **No ServiceLoader** - Uses Python entry points (can be added)
2. **Simpler Configuration** - TOML instead of Properties files
3. **Direct Integration** - No intermediate DockerImageName class
4. **Protocol-Based** - Structural typing instead of inheritance

### Enhanced Areas

1. **Type Safety** - Full type hints throughout
2. **Pythonic API** - Context managers, property access
3. **Better Logging** - Structured logging with levels
4. **TOML Support** - Modern configuration format

### Preserved Features

1. **Prefix Substitution** - Same Docker Hub prefix logic
2. **Configurable Mappings** - Exact image mappings
3. **Chaining** - Combine multiple substitutors
4. **Global Instance** - Singleton pattern maintained

## Configuration Module

The `config.py` module handles all configuration:

```python
from testcontainers.config import get_config

config = get_config()

# Get hub prefix
prefix = config.get_hub_image_name_prefix()

# Get image mapping
mapped = config.get_image_mapping("postgres:13")

# Get all mappings
all_mappings = config.get_all_image_mappings()
```

### Config Loading Order

1. Check for `./testcontainers.toml` (project-specific)
2. Check for `~/.testcontainers/testcontainers.toml` (user-wide)
3. Load environment variables (override TOML)
4. Use defaults

## Future Enhancements

Potential improvements for future versions:

1. **Entry Points** - Discover custom substitutors via setuptools entry points
2. **Image Name Parsing** - More sophisticated image name parsing
3. **Registry Authentication** - Auto-configure credentials per registry
4. **Caching** - Cache substitution results for performance
5. **Auditing** - Log all substitutions for security audit
6. **Wildcards** - Support wildcard patterns in mappings

## Dependencies

Required for TOML support:

- Python 3.11+: Built-in `tomllib`
- Python 3.9-3.10: `tomli` package

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "tomli >= 2.0.0 ; python_version < '3.11'",
]
```

## See Also

- `IMAGE_NAME_SUBSTITUTOR_EXPLAINED.md` - Detailed explanation of the Java implementation
- `testcontainers.toml.example` - Example configuration file
- `tests/unit/test_substitutor.py` - Comprehensive test suite
