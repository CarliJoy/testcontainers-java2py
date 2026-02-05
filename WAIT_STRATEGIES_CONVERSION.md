# Wait Strategies Conversion Documentation

## Overview

This document describes the conversion of wait strategies from Java to Python. Wait strategies determine when a container is considered ready to use.

## Files Converted

### Java Files (10 files total)

| Java File | Lines | Description |
|-----------|-------|-------------|
| WaitStrategy.java | 9 | Base interface |
| WaitStrategyTarget.java | 21 | Target interface |
| AbstractWaitStrategy.java | 96 | Base implementation |
| DockerHealthcheckWaitStrategy.java | 28 | Healthcheck-based wait |
| LogMessageWaitStrategy.java | 61 | Log message-based wait |
| HostPortWaitStrategy.java | ~150 | Port-based wait |
| **Total** | **~365** | |

### Python Output (4 files)

| Python File | Lines | Description |
|-------------|-------|-------------|
| wait_strategy.py | ~130 | Base classes and protocols |
| healthcheck.py | ~50 | Healthcheck wait strategy |
| log.py | ~110 | Log message wait strategy |
| port.py | ~120 | Host port wait strategy |
| **Total** | **~410** | |

## Key Conversions

### 1. Interface → Protocol

**Java:**
```java
public interface WaitStrategy {
    void waitUntilReady(WaitStrategyTarget waitStrategyTarget);
    WaitStrategy withStartupTimeout(Duration startupTimeout);
}
```

**Python:**
```python
class WaitStrategy(Protocol):
    def wait_until_ready(self, wait_strategy_target: WaitStrategyTarget) -> None:
        ...
    
    def with_startup_timeout(self, startup_timeout: timedelta) -> WaitStrategy:
        ...
```

### 2. Abstract Base Class

**Java:**
```java
public abstract class AbstractWaitStrategy implements WaitStrategy {
    @NonNull
    protected Duration startupTimeout = Duration.ofSeconds(60);
    
    protected abstract void waitUntilReady();
}
```

**Python:**
```python
class AbstractWaitStrategy(ABC):
    def __init__(self):
        self._startup_timeout = timedelta(seconds=60)
    
    @abstractmethod
    def _wait_until_ready(self) -> None:
        pass
```

### 3. Concrete Implementations

#### DockerHealthcheckWaitStrategy

**Java:**
```java
public class DockerHealthcheckWaitStrategy extends AbstractWaitStrategy {
    @Override
    protected void waitUntilReady() {
        Unreliables.retryUntilTrue(
            (int) startupTimeout.getSeconds(),
            TimeUnit.SECONDS,
            waitStrategyTarget::isHealthy
        );
    }
}
```

**Python:**
```python
class DockerHealthcheckWaitStrategy(AbstractWaitStrategy):
    def _wait_until_ready(self) -> None:
        timeout_seconds = self._startup_timeout.total_seconds()
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if self._wait_strategy_target.is_healthy():
                return
            time.sleep(1)
        
        raise TimeoutError("Timed out waiting for container to become healthy")
```

#### LogMessageWaitStrategy

**Java:**
```java
public class LogMessageWaitStrategy extends AbstractWaitStrategy {
    private String regEx;
    private int times = 1;
    
    public LogMessageWaitStrategy withRegEx(String regEx) {
        this.regEx = regEx;
        return this;
    }
}
```

**Python:**
```python
class LogMessageWaitStrategy(AbstractWaitStrategy):
    def __init__(self):
        super().__init__()
        self._regex: str | None = None
        self._times: int = 1
    
    def with_regex(self, regex: str) -> LogMessageWaitStrategy:
        self._regex = regex
        return self
```

## Design Decisions

### 1. Simplified Retry Logic

**Java** uses the `Unreliables` library from `ducttape`:
```java
Unreliables.retryUntilTrue(timeout, TimeUnit.SECONDS, condition)
```

**Python** uses simple time-based loops:
```python
start_time = time.time()
while time.time() - start_time < timeout_seconds:
    if condition():
        return
    time.sleep(interval)
raise TimeoutError()
```

This is simpler and doesn't require additional dependencies.

### 2. Rate Limiting Removed

The Java implementation includes rate limiting:
```java
private static final RateLimiter DOCKER_CLIENT_RATE_LIMITER = ...
```

Python implementation omits this initially for simplicity. It can be added later if needed.

### 3. Executor Service Removed

Java uses `ExecutorService` for concurrent checks. Python implementation uses simpler sequential checks with appropriate sleep intervals.

### 4. Protocol-Based Design

Using Python Protocols allows structural typing without requiring explicit inheritance, making the code more flexible and Pythonic.

## Features Implemented

✅ **WaitStrategy Protocol** - Interface for all wait strategies
✅ **WaitStrategyTarget Protocol** - Container target interface
✅ **AbstractWaitStrategy** - Base implementation with timeout support
✅ **DockerHealthcheckWaitStrategy** - Wait for Docker healthcheck
✅ **LogMessageWaitStrategy** - Wait for log message pattern
✅ **HostPortWaitStrategy** - Wait for ports to be available
✅ **Fluent API** - Method chaining with `with_*` methods
✅ **Timeout Support** - Configurable startup timeouts
✅ **Full Type Hints** - Complete type annotations

## Features Simplified/Deferred

These Java features were simplified or deferred:

- ❌ Rate limiting (RateLimiter) - Can be added if needed
- ❌ ExecutorService for concurrent checks - Using sequential checks
- ❌ HttpWaitStrategy - More complex, can be added later
- ❌ WaitAllStrategy - Composite strategy, can be added later
- ❌ ShellStrategy - Uses exec, can be added later

## Testing

### Test Coverage

**16 new tests covering:**
- AbstractWaitStrategy base functionality
- DockerHealthcheckWaitStrategy (3 tests)
  - Success when healthy
  - Timeout behavior
  - Eventually succeeds
- LogMessageWaitStrategy (5 tests)
  - Message found
  - Timeout
  - Regex required
  - Multiple occurrences
  - Multiline matching
- HostPortWaitStrategy (5 tests)
  - No ports to check
  - Port checking
  - Fluent API
  - Timeout
  - Success

**Total: 47 tests passing (31 existing + 16 new)**

## Usage Examples

### Healthcheck Wait Strategy

```python
from testcontainers.waiting import DockerHealthcheckWaitStrategy
from datetime import timedelta

strategy = DockerHealthcheckWaitStrategy()
strategy = strategy.with_startup_timeout(timedelta(seconds=30))
strategy.wait_until_ready(container)
```

### Log Message Wait Strategy

```python
from testcontainers.waiting import LogMessageWaitStrategy

strategy = LogMessageWaitStrategy()
strategy = strategy.with_regex(".*Server started.*")
strategy = strategy.with_times(1)
strategy.wait_until_ready(container)
```

### Host Port Wait Strategy

```python
from testcontainers.waiting import HostPortWaitStrategy

# Wait for specific ports
strategy = HostPortWaitStrategy()
strategy = strategy.with_ports(8080, 8081)
strategy.wait_until_ready(container)

# Or wait for all exposed ports (default)
strategy = HostPortWaitStrategy()
strategy.wait_until_ready(container)
```

## Integration with GenericContainer

Wait strategies will be used in GenericContainer like this:

```python
class GenericContainer:
    def __init__(self, image):
        self._wait_strategy = HostPortWaitStrategy()
    
    def waiting_for(self, wait_strategy: WaitStrategy):
        """Set the wait strategy."""
        self._wait_strategy = wait_strategy
        return self
    
    def start(self):
        # ... start container ...
        self._wait_strategy.wait_until_ready(self)
```

## Next Steps

With wait strategies complete, we can now:

1. **Convert Image Handling** - RemoteDockerImage, ImagePullPolicy
2. **Implement GenericContainer** - Main container class using wait strategies
3. **Add More Wait Strategies** - Http, Shell, WaitAll as needed

## Statistics

| Metric | Java | Python | Change |
|--------|------|--------|--------|
| Lines of Code | ~365 | ~410 | +12% |
| Files | 10 | 4 | -60% |
| Tests | 0 (in separate file) | 16 | New |
| Features | Full | Core | Simplified |

Python is slightly more verbose due to explicit type hints and docstrings, but the code is clearer and more maintainable.
