# GenericContainer Conversion Mapping

## Overview
This document maps Java source files to the Python `generic_container.py` module.

## Primary File

**GenericContainer.java** → **generic_container.py**
- **Path**: `core/src/main/java/org/testcontainers/containers/GenericContainer.java`
- **Size**: 1,527 lines
- **Description**: Base class that allows a container to be launched and controlled

### Class Definition
```java
public class GenericContainer<SELF extends GenericContainer<SELF>>
    implements Container<SELF>, AutoCloseable, WaitStrategyTarget, Startable
```

**Python Translation**:
```python
from __future__ import annotations
from typing import Generic, TypeVar, Protocol
from abc import ABC

SELF = TypeVar('SELF', bound='GenericContainer')

class GenericContainer(Generic[SELF], ABC):
    """Base class that allows a container to be launched and controlled."""
    # Implements: Container, WaitStrategyTarget, Startable protocols
    # Context manager support via __enter__/__exit__
```

## Related Files to Include in generic_container.py

### 1. Container.java (Interface) → Protocol
- **Path**: `core/src/main/java/org/testcontainers/containers/Container.java`
- **Size**: 483 lines
- **Description**: Main container interface with fluent API methods
- **Conversion**: 
  - Convert to Python `Protocol` class or abstract base class
  - Defines the contract for container operations
  - Contains inner class `ExecResult` (convert to dataclass)

```python
from typing import Protocol
from dataclasses import dataclass

@dataclass
class ExecResult:
    """Results from a docker exec command."""
    exit_code: int
    stdout: str
    stderr: str

class Container(Protocol[SELF]):
    """Container protocol defining the container API."""
    def self(self) -> SELF:
        """Return a reference to this container instance."""
        ...
```

### 2. ContainerState.java (Interface) → Protocol
- **Path**: `core/src/main/java/org/testcontainers/containers/ContainerState.java`
- **Size**: 418 lines
- **Description**: Interface for querying container state
- **Conversion**: 
  - Convert to Python `Protocol` or mixin class
  - Provides methods for checking if container is running, healthy, etc.
  - Includes methods for getting logs, copying files, etc.

```python
class ContainerState(Protocol):
    """Protocol for querying container state."""
    STATE_HEALTHY = "healthy"
    
    def is_running(self) -> bool:
        """Check if container is currently running."""
        ...
    
    def is_created(self) -> bool:
        """Check if container is created."""
        ...
```

### 3. ContainerDef.java (Internal Class) → Internal Class
- **Path**: `core/src/main/java/org/testcontainers/containers/ContainerDef.java`
- **Size**: 304 lines
- **Description**: Internal class holding container definition/configuration
- **Conversion**: 
  - Convert to Python dataclass or regular class
  - Used internally by GenericContainer
  - Holds configuration like exposed ports, bindings, labels, env vars

```python
from dataclasses import dataclass, field

@dataclass
class ContainerDef:
    """Internal container definition and configuration."""
    image: RemoteDockerImage
    exposed_ports: set[ExposedPort] = field(default_factory=set)
    port_bindings: set[PortBinding] = field(default_factory=set)
    labels: dict[str, str] = field(default_factory=dict)
    env_vars: dict[str, str] = field(default_factory=dict)
    # ... more fields
```

### 4. FixedHostPortGenericContainer.java → Subclass
- **Path**: `core/src/main/java/org/testcontainers/containers/FixedHostPortGenericContainer.java`
- **Size**: 47 lines
- **Description**: Variant allowing fixed port mapping (deprecated pattern)
- **Conversion**: 
  - Can be included as a subclass in the same file
  - Or put in separate file `fixed_host_port_container.py`
  - Very simple - just extends GenericContainer with fixed port methods

```python
class FixedHostPortGenericContainer(GenericContainer[SELF]):
    """
    Variant that allows fixed port on docker host.
    
    WARNING: Normally this should not be required. Use only when absolutely necessary.
    Deprecated - risks port conflicts.
    """
    
    def with_fixed_exposed_port(
        self, 
        host_port: int, 
        container_port: int, 
        protocol: InternetProtocol = InternetProtocol.TCP
    ) -> SELF:
        """Bind a fixed port on docker host to container port."""
        ...
```

## Supporting Files (MAY Include in Same Module)

### 5. LinkableContainer.java (Trait)
- **Path**: `core/src/main/java/org/testcontainers/containers/traits/LinkableContainer.java`
- **Size**: ~10 lines (very small interface)
- **Description**: Marker interface for containers that can be linked
- **Conversion**: 
  - Simple protocol or just inherit directly
  - Links are deprecated anyway

### 6. Inner Classes and Enums

From within GenericContainer.java and related files:

- **BindMode** (enum) → Python Enum
- **SelinuxContext** (enum) → Python Enum  
- **InternetProtocol** (enum) → Python Enum
- **ExecConfig** (class) → dataclass

## Files to Convert SEPARATELY

These should go in their own Python modules:

### Wait Strategies
- All wait strategy files → `waiting/` package
- `WaitStrategy.java` → `waiting/wait_strategy.py`
- `WaitStrategyTarget.java` → protocol in wait_strategy.py

### Images
- `RemoteDockerImage.java` → `images/remote_image.py`

### Network
- `Network.java` → `network.py`

### Startup Check
- `StartupCheckStrategy.java` → `startupcheck/startup_check_strategy.py`

### Output
- `OutputFrame.java` → `output/output_frame.py`

### Lifecycle
- `Startable.java` → `lifecycle/startable.py`

## Conversion Strategy for generic_container.py

### Structure:
```python
# generic_container.py

from __future__ import annotations

# Standard library imports
from typing import TypeVar, Generic, Protocol, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from contextlib import contextmanager
import logging

# Docker SDK
import docker
from docker.models.containers import Container as DockerContainer

# Testcontainers imports
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting import WaitStrategy
from testcontainers.images.remote_image import RemoteDockerImage
# ... more imports

# Type variables
SELF = TypeVar('SELF', bound='GenericContainer')

# Supporting classes
@dataclass
class ExecResult:
    """Results from docker exec command."""
    exit_code: int
    stdout: str
    stderr: str

# Protocols/Interfaces
class ContainerState(Protocol):
    """Protocol for container state queries."""
    ...

class Container(Protocol[SELF]):
    """Main container protocol."""
    ...

# Internal classes
@dataclass
class ContainerDef:
    """Internal container definition."""
    ...

# Main class
class GenericContainer(Generic[SELF], ABC):
    """Base class for container management."""
    
    # Constants
    CONTAINER_RUNNING_TIMEOUT_SEC = 30
    INTERNAL_HOST_HOSTNAME = "host.testcontainers.internal"
    
    def __init__(self, image: str | RemoteDockerImage):
        """Initialize container with image."""
        ...
    
    def __enter__(self) -> SELF:
        """Context manager entry - start container."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop container."""
        self.stop()
    
    # All the methods from GenericContainer.java
    ...

# Subclasses
class FixedHostPortGenericContainer(GenericContainer[SELF]):
    """Variant with fixed port mapping (deprecated)."""
    ...
```

## Estimated Conversion Scope

**Total lines to convert into generic_container.py**:
- GenericContainer.java: 1,527 lines
- Container.java (interface): 483 lines
- ContainerState.java (interface): 418 lines
- ContainerDef.java: 304 lines
- FixedHostPortGenericContainer.java: 47 lines
- **Total: ~2,779 lines of Java**

**Estimated Python output**: ~2,000-2,500 lines (Python is typically more concise)

## Dependencies to Convert First

Before converting GenericContainer, you should have:

1. **Docker client wrapper** - `docker_client.py`
2. **Image handling** - `images/remote_image.py`
3. **Wait strategies** (at least base) - `waiting/wait_strategy.py`
4. **Startup checks** - `startupcheck/startup_check_strategy.py`
5. **Network** - `network.py`
6. **Lifecycle** - `lifecycle/startable.py`
7. **Utility classes** - various utilities

## Conversion Order Recommendation

1. Start with protocols/interfaces (Container, ContainerState)
2. Convert supporting dataclasses (ExecResult, ContainerDef)
3. Convert GenericContainer main class incrementally:
   - Constructor and initialization
   - Configuration methods (with_* fluent API)
   - Lifecycle methods (start, stop, etc.)
   - State query methods
   - Execution methods
4. Add FixedHostPortGenericContainer subclass
5. Write comprehensive tests

## Key Python Patterns to Use

1. **Type hints everywhere** with `from __future__ import annotations`
2. **Protocols** for interfaces (not abstract classes)
3. **Dataclasses** for simple data structures
4. **Context managers** for container lifecycle
5. **Properties** instead of getters/setters
6. **Fluent interface** with `return self` pattern
7. **Docker-py** for Docker client operations

## Testing Strategy

Convert tests alongside the code:
- `GenericContainerTest.java` → `test_generic_container.py`
- Use pytest fixtures for common setup
- Test each major feature area
- Integration tests with real Docker
