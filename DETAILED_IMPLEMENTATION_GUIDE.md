# Detailed Implementation Guide: Java to Python Feature Parity

This document provides exhaustive, actionable guidance for implementing all missing features from testcontainers-java in the Python version.

## Table of Contents
1. [Critical Infrastructure Gaps](#critical-infrastructure-gaps)
2. [GenericContainer Missing Features](#genericcontainer-missing-features)
3. [Docker Client & Factory](#docker-client--factory)
4. [Wait Strategies](#wait-strategies)
5. [Specialized Module Details](#specialized-module-details)
6. [Implementation Roadmap](#implementation-roadmap)

---

## Critical Infrastructure Gaps

### 1. Ryuk Container (ResourceReaper)
**Priority: CRITICAL** | **Effort: 3-5 days** | **Complexity: HIGH**

**Java Source:** `core/src/main/java/org/testcontainers/utility/ResourceReaper.java`

**What it does:**
- Automatically cleans up containers when test process dies
- Runs a privileged "ryuk" container that monitors Docker socket
- Removes containers with specific labels when client disconnects
- Prevents orphaned containers from accumulating

**Implementation Steps:**

1. **Create `src/testcontainers/core/resource_reaper.py`:**
```python
from __future__ import annotations

class ResourceReaper:
    """
    Manages lifecycle cleanup using Ryuk container.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/utility/ResourceReaper.java
    """
    
    RYUK_IMAGE = "testcontainers/ryuk:0.5.1"
    RYUK_PORT = 8080
    
    _instance: ResourceReaper | None = None
    _ryuk_container_id: str | None = None
    _connection_socket: socket.socket | None = None
    
    @classmethod
    def instance(cls) -> ResourceReaper:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start(self) -> None:
        """Start Ryuk container."""
        # 1. Pull ryuk image
        # 2. Create container with:
        #    - Bind /var/run/docker.sock
        #    - Publish port 8080
        #    - Label: org.testcontainers.ryuk=true
        # 3. Start container
        # 4. Connect to port 8080
        # 5. Send ACK message
        pass
    
    def register_container(self, container_id: str) -> None:
        """Register container for cleanup."""
        # Send "label=org.testcontainers.session-id=<session>\n" to socket
        pass
    
    def register_network(self, network_id: str) -> None:
        """Register network for cleanup."""
        pass
```

2. **Modify `src/testcontainers/core/docker_client.py`:**
   - Add `_start_ryuk_if_needed()` method
   - Call during first container creation
   - Check config: `reuse.enabled=false` (don't use Ryuk with reuse)

3. **Modify `src/testcontainers/core/generic_container.py`:**
   - After container creation, call `ResourceReaper.instance().register_container(self.container_id)`
   - Add session ID label to all containers

4. **Add configuration:**
   - `ryuk.disabled` in testcontainers.toml
   - `TESTCONTAINERS_RYUK_DISABLED` environment variable

5. **Tests needed:**
   - Test Ryuk starts on first container
   - Test containers are labeled correctly
   - Test cleanup happens when process dies
   - Test Ryuk disabled when configured

**Files to modify:**
- Create: `src/testcontainers/core/resource_reaper.py` (~200 lines)
- Modify: `src/testcontainers/core/docker_client.py` (+50 lines)
- Modify: `src/testcontainers/core/generic_container.py` (+20 lines)
- Modify: `src/testcontainers/config.py` (+15 lines)
- Create: `tests/unit/test_resource_reaper.py` (~150 lines)

---

### 2. Startup Retry Logic
**Priority: HIGH** | **Effort: 1-2 days** | **Complexity: MEDIUM**

**Java Source:** `core/src/main/java/org/testcontainers/containers/GenericContainer.java` lines 396-450

**What it does:**
- Retries container start on failure
- Configurable retry count (default 1 retry)
- Logs failure reasons between retries
- Different wait strategy on retry

**Implementation Steps:**

1. **Modify `src/testcontainers/core/generic_container.py`:**

Add to `__init__`:
```python
self._startup_attempts: int = 0
self._startup_check_strategy: StartupCheckStrategy | None = None
```

Add method:
```python
def with_startup_attempts(self, attempts: int) -> Self:
    """
    Set maximum startup attempts.
    
    Args:
        attempts: Number of times to attempt starting (default 1).
        
    Java source: GenericContainer.withStartupAttempts()
    """
    self._startup_attempts = attempts
    return self

def _try_start(self) -> None:
    """Attempt to start container with retry logic."""
    last_exception = None
    attempts = self._startup_attempts or 1
    
    for attempt in range(attempts):
        try:
            logger.info(f"Starting container (attempt {attempt + 1}/{attempts})")
            self._do_start()
            return
        except Exception as e:
            logger.warning(f"Container start failed (attempt {attempt + 1}): {e}")
            last_exception = e
            if attempt < attempts - 1:
                # Cleanup failed container
                self._cleanup_failed_start()
    
    raise ContainerStartException(
        f"Container failed to start after {attempts} attempts"
    ) from last_exception

def _cleanup_failed_start(self) -> None:
    """Cleanup after failed start attempt."""
    if self.container_id:
        try:
            self.get_docker_client().remove_container(
                self.container_id, force=True
            )
        except Exception as e:
            logger.debug(f"Failed to cleanup container: {e}")
```

2. **Modify `start()` method:**
   - Replace direct start logic with `_try_start()`
   - Move actual start to `_do_start()`

3. **Tests needed:**
   - Test retry on container failure
   - Test max attempts respected
   - Test cleanup between attempts
   - Test exception after all attempts fail

**Files to modify:**
- Modify: `src/testcontainers/core/generic_container.py` (+80 lines)
- Create: `tests/unit/test_startup_retry.py` (~100 lines)

---

### 3. Resource Limits (CPU, Memory, Swap)
**Priority: HIGH** | **Effort: 1 day** | **Complexity: LOW**

**Java Source:** `core/src/main/java/org/testcontainers/containers/GenericContainer.java` lines 175-200

**What it does:**
- Set CPU shares/quota/period
- Set memory limits
- Set memory swap limits
- Set memory swappiness

**Implementation Steps:**

1. **Add to `GenericContainer.__init__`:**
```python
self._memory_limit: int | None = None  # bytes
self._memory_swap_limit: int | None = None  # bytes
self._memory_swappiness: int | None = None  # 0-100
self._cpu_shares: int | None = None  # relative weight
self._cpu_quota: int | None = None  # microseconds
self._cpu_period: int | None = None  # microseconds
self._cpuset_cpus: str | None = None  # "0-3" or "0,1"
self._cpuset_mems: str | None = None  # "0-1"
```

2. **Add configuration methods:**
```python
def with_memory_limit(self, memory: int) -> Self:
    """
    Set memory limit in bytes.
    
    Args:
        memory: Memory limit in bytes (e.g., 512 * 1024 * 1024 for 512MB)
        
    Java source: GenericContainer.withMemoryLimit()
    """
    self._memory_limit = memory
    return self

def with_cpu_shares(self, cpu_shares: int) -> Self:
    """
    Set CPU shares (relative weight).
    
    Args:
        cpu_shares: CPU shares (default 1024)
        
    Java source: GenericContainer.withCpuShares()
    """
    self._cpu_shares = cpu_shares
    return self

def with_cpu_quota(self, cpu_quota: int) -> Self:
    """
    Set CPU quota in microseconds.
    
    Args:
        cpu_quota: CPU quota per period in microseconds
        
    Java source: GenericContainer.withCpuQuota()
    """
    self._cpu_quota = cpu_quota
    return self

def with_cpu_period(self, cpu_period: int) -> Self:
    """
    Set CPU period in microseconds.
    
    Args:
        cpu_period: CPU period in microseconds (default 100000)
        
    Java source: GenericContainer.withCpuPeriod()
    """
    self._cpu_period = cpu_period
    return self
```

3. **Modify `_create_container()`:**
```python
host_config = {
    # ... existing config ...
}

if self._memory_limit:
    host_config["memory"] = self._memory_limit
if self._memory_swap_limit:
    host_config["memswap_limit"] = self._memory_swap_limit
if self._cpu_shares:
    host_config["cpu_shares"] = self._cpu_shares
if self._cpu_quota:
    host_config["cpu_quota"] = self._cpu_quota
if self._cpu_period:
    host_config["cpu_period"] = self._cpu_period
if self._cpuset_cpus:
    host_config["cpuset_cpus"] = self._cpuset_cpus
```

**Files to modify:**
- Modify: `src/testcontainers/core/generic_container.py` (+100 lines)
- Create: `tests/unit/test_resource_limits.py` (~80 lines)

---

### 4. ExecWaitStrategy
**Priority: MEDIUM** | **Effort: 1 day** | **Complexity: MEDIUM**

**Java Source:** `core/src/main/java/org/testcontainers/containers/wait/strategy/AbstractWaitStrategy.java`

**What it does:**
- Execute command inside container
- Wait until command succeeds (exit code 0)
- Different from ShellStrategy (which runs in shell)

**Implementation Steps:**

1. **Create `src/testcontainers/waiting/exec.py`:**
```python
from __future__ import annotations

from typing import TYPE_CHECKING

from .wait_strategy import AbstractWaitStrategy

if TYPE_CHECKING:
    from ..core.generic_container import GenericContainer


class ExecWaitStrategy(AbstractWaitStrategy):
    """
    Wait strategy that executes a command in the container.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/AbstractWaitStrategy.java
    """
    
    def __init__(self, command: list[str]) -> None:
        """
        Initialize with command to execute.
        
        Args:
            command: Command parts (e.g., ["sh", "-c", "test -f /ready"])
        """
        super().__init__()
        self._command = command
    
    def wait_until_ready(self, container: GenericContainer) -> None:
        """Wait until command executes successfully."""
        import time
        
        deadline = time.time() + self._startup_timeout.total_seconds()
        
        while time.time() < deadline:
            try:
                result = container.exec_run(self._command)
                if result.exit_code == 0:
                    return
            except Exception as e:
                logger.debug(f"Exec check failed: {e}")
            
            time.sleep(self._poll_interval.total_seconds())
        
        raise TimeoutError(
            f"Container not ready after {self._startup_timeout}: "
            f"command {self._command} never succeeded"
        )
```

2. **Add to `__init__.py`:**
```python
from .exec import ExecWaitStrategy

__all__ = [
    # ... existing ...
    "ExecWaitStrategy",
]
```

**Files to create:**
- Create: `src/testcontainers/waiting/exec.py` (~80 lines)
- Modify: `src/testcontainers/waiting/__init__.py` (+2 lines)
- Create: `tests/unit/test_exec_wait_strategy.py` (~60 lines)

---

## GenericContainer Missing Features

### Method-by-Method Comparison

#### Container Lifecycle

| Java Method | Python Equivalent | Status | Priority |
|------------|-------------------|--------|----------|
| `withStartupAttempts(int)` | Missing | ❌ | HIGH |
| `withStartupCheckStrategy(StartupCheckStrategy)` | Missing | ❌ | MEDIUM |
| `withMinimumRunningDuration(Duration)` | Missing | ❌ | LOW |
| `withPrivilegedMode()` | Missing | ❌ | MEDIUM |
| `withExtraHost(String, String)` | Missing | ❌ | LOW |
| `withFileSystemBind(String, String)` | `with_volume_mapping` | ✅ | - |
| `withTmpFs(Map<String, String>)` | Missing | ❌ | LOW |

#### Implementation: `withPrivilegedMode()`

**Effort: 30 minutes** | **Complexity: LOW**

```python
def with_privileged_mode(self) -> Self:
    """
    Run container in privileged mode.
    
    Java source: GenericContainer.withPrivilegedMode()
    """
    self._privileged_mode = True
    return self
```

Modify `_create_container()`:
```python
host_config["privileged"] = self._privileged_mode
```

#### Implementation: `withExtraHost()`

**Effort: 30 minutes** | **Complexity: LOW**

```python
def with_extra_host(self, hostname: str, ip_address: str) -> Self:
    """
    Add extra host entry to /etc/hosts.
    
    Args:
        hostname: Hostname to add
        ip_address: IP address to map to
        
    Java source: GenericContainer.withExtraHost()
    """
    if not self._extra_hosts:
        self._extra_hosts = {}
    self._extra_hosts[hostname] = ip_address
    return self
```

---

## Docker Client & Factory

### Missing Features from DockerClientFactory

**Java Source:** `core/src/main/java/org/testcontainers/DockerClientFactory.java`

1. **Disk Space Checking** (lines 200-250)
   - Check available disk space before starting
   - Configurable minimum (default 2GB)
   - Log warning if insufficient

2. **Version Compatibility Checking** (lines 300-350)
   - Check Docker version >= minimum (1.6.0)
   - Check API version compatibility
   - Fail fast with helpful message

3. **Diagnostics** (lines 400-450)
   - `checkAndConfigure()` method
   - System info logging
   - Docker info logging

4. **Image Caching** (lines 500-550)
   - Cache pulled images in session
   - Avoid re-pulling same image

### Implementation: Disk Space Checking

**Effort: 2 hours** | **Complexity: LOW**

```python
def _check_disk_space(self) -> None:
    """
    Check available disk space.
    
    Java source: DockerClientFactory.checkDiskSpace()
    """
    try:
        info = self._client.info()
        # Docker stores data in data-root
        data_root = info.get("DockerRootDir", "/var/lib/docker")
        
        import shutil
        stat = shutil.disk_usage(data_root)
        available_gb = stat.free / (1024 ** 3)
        
        if available_gb < 2.0:
            logger.warning(
                f"Low disk space: {available_gb:.2f}GB available "
                f"at {data_root}. Recommended minimum: 2GB"
            )
    except Exception as e:
        logger.debug(f"Could not check disk space: {e}")
```

---

## Wait Strategies

### Missing Wait Strategies

| Strategy | Java Class | Python Status | Priority |
|----------|-----------|---------------|----------|
| ExecWaitStrategy | AbstractWaitStrategy | ❌ Missing | MEDIUM |
| StartupCheckStrategy | StartupCheckStrategy | ❌ Missing | MEDIUM |
| HostPortWaitStrategy with TLS | HostPortWaitStrategy | ⚠️ Partial | LOW |

### Implementation: TLS Support in HostPortWaitStrategy

**Effort: 1 hour** | **Complexity: LOW**

Add to `src/testcontainers/waiting/port.py`:

```python
def with_tls(self) -> Self:
    """
    Enable TLS when checking port.
    
    Java source: HostPortWaitStrategy.withTls()
    """
    self._use_tls = True
    return self

def _check_port(self, host: str, port: int) -> bool:
    """Check if port is accessible."""
    import socket
    import ssl
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        
        if self._use_tls:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock)
        
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False
```

---

## Specialized Module Details

### PostgreSQL Missing Features

**Java Source:** `modules/postgresql/src/main/java/org/testcontainers/containers/PostgreSQLContainer.java`

#### Missing Methods:

1. **`withDatabaseName(String)`** - ✅ Implemented as `with_database_name()`
2. **`withInitScript(String)`** - ❌ Missing
3. **`withTmpFs(Map<String, String>)`** - ❌ Missing

#### Implementation: `withInitScript()`

**Effort: 2 hours** | **Complexity: MEDIUM**

```python
def with_init_script(self, script_path: str) -> Self:
    """
    Execute SQL script on container startup.
    
    Args:
        script_path: Path to SQL script file (classpath or filesystem)
        
    Java source: PostgreSQLContainer.withInitScript()
    """
    self._init_script_path = script_path
    return self

def _configure(self) -> None:
    """Configure container before start."""
    super()._configure()
    
    if self._init_script_path:
        # Copy script to container
        script_content = Path(self._init_script_path).read_text()
        self.with_copy_file_to_container(
            self._init_script_path,
            "/docker-entrypoint-initdb.d/init.sql"
        )
```

### MySQL Missing Features

**Java Source:** `modules/mysql/src/main/java/org/testcontainers/containers/MySQLContainer.java`

#### Missing Methods:

1. **`withConfigurationOverride(String)`** - ❌ Missing
2. **`withInitScript(String)`** - ❌ Missing
3. **`withUrlParam(String, String)`** - ❌ Missing

#### Implementation: `withConfigurationOverride()`

**Effort: 1 hour** | **Complexity: LOW**

```python
def with_configuration_override(self, config_path: str) -> Self:
    """
    Override MySQL configuration with custom config file.
    
    Args:
        config_path: Path to my.cnf configuration file
        
    Java source: MySQLContainer.withConfigurationOverride()
    """
    self.with_copy_file_to_container(
        config_path,
        "/etc/mysql/conf.d/custom.cnf"
    )
    return self
```

---

## Implementation Roadmap

### Phase 1: Critical Infrastructure (Week 1-2)
**Goal: Production-ready cleanup and reliability**

- [ ] Day 1-3: Implement Ryuk (ResourceReaper)
  - [ ] Create resource_reaper.py
  - [ ] Integrate with DockerClientFactory
  - [ ] Add configuration options
  - [ ] Write tests
  
- [ ] Day 4-5: Implement Startup Retry Logic
  - [ ] Add retry mechanism to GenericContainer
  - [ ] Add cleanup between attempts
  - [ ] Write tests

- [ ] Day 6-7: Add Resource Limits
  - [ ] CPU/memory configuration methods
  - [ ] Integration with container creation
  - [ ] Write tests

**Deliverable:** Core infrastructure matches Java reliability

### Phase 2: Wait Strategies & Execution (Week 3)
**Goal: Complete wait strategy parity**

- [ ] Day 1-2: Implement ExecWaitStrategy
  - [ ] Create exec.py
  - [ ] Add to wait strategy exports
  - [ ] Write tests

- [ ] Day 3: Add TLS support to HostPortWaitStrategy
  - [ ] Modify port.py
  - [ ] Write tests

- [ ] Day 4-5: Implement StartupCheckStrategy
  - [ ] Create startup_check.py
  - [ ] Integrate with GenericContainer
  - [ ] Write tests

**Deliverable:** All wait strategies available

### Phase 3: Container Features (Week 4)
**Goal: Feature-complete GenericContainer**

- [ ] Day 1: Add privileged mode, extra hosts
- [ ] Day 2: Add tmpfs support
- [ ] Day 3: Add GPU support (if needed)
- [ ] Day 4-5: Comprehensive testing

**Deliverable:** GenericContainer feature-complete

### Phase 4: Database Init Scripts (Week 5)
**Goal: All database modules support init scripts**

- [ ] Day 1: PostgreSQL init script
- [ ] Day 2: MySQL init script & config override
- [ ] Day 3: MongoDB init script
- [ ] Day 4: Testing all database init features
- [ ] Day 5: Documentation

**Deliverable:** Database modules production-ready

### Phase 5: Polish & Documentation (Week 6)
**Goal: Production quality**

- [ ] Code review all changes
- [ ] Update all documentation
- [ ] Add migration guide
- [ ] Performance testing
- [ ] Security review

---

## Testing Requirements

### Unit Tests Needed

Each feature requires:
1. **Happy path test** - Feature works as expected
2. **Error handling test** - Graceful failure
3. **Configuration test** - Options respected
4. **Integration test** - Works with real Docker

### Test Coverage Goals

- Core infrastructure: 90%+
- GenericContainer: 85%+
- Specialized modules: 80%+
- Wait strategies: 85%+

### Integration Tests

Critical paths requiring integration tests:
1. Ryuk cleanup on process death
2. Startup retry with real container failures
3. Init scripts with real databases
4. Resource limits with actual memory pressure

---

## Estimated Total Effort

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1 | 10-14 days | None |
| Phase 2 | 5-7 days | None (can parallel with Phase 1) |
| Phase 3 | 5 days | Phase 1 complete |
| Phase 4 | 5 days | Phase 3 complete |
| Phase 5 | 5 days | All phases complete |

**Total: 30-36 days** (1.5-2 months for one developer)

With 2 developers working in parallel:
- **Total: 20-24 days** (1 month)

---

## Priority Order

If time is limited, implement in this order:

1. **Ryuk** - Critical for production use
2. **Startup retry** - Critical for reliability
3. **Resource limits** - Important for performance
4. **Init scripts** - High user demand
5. **ExecWaitStrategy** - Common use case
6. **Privileged mode** - Specific use cases
7. **Remaining features** - Nice to have

---

## Summary

This guide provides:
- ✅ Complete feature gap analysis
- ✅ Step-by-step implementation instructions
- ✅ Code examples for each feature
- ✅ Effort and complexity estimates
- ✅ Testing requirements
- ✅ Realistic timeline

**Next Step:** Choose a phase and start implementing!
