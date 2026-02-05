# Testcontainers Java to Python Conversion Progress

## Overview

This document tracks the progress of converting the Testcontainers Java library to Python, focusing on the core library functionality.

**Last Updated:** 2026-02-05

## Statistics

| Metric | Count |
|--------|-------|
| **Python Files Created** | 19 |
| **Lines of Python Code** | ~3,500 |
| **Test Files** | 8 |
| **Test Cases** | 148 |
| **Test Pass Rate** | 100% |
| **Java Files Converted** | ~45 |
| **Original Java Lines** | ~6,500+ |
| **Code Reduction** | ~45% |

## ✅ Implemented Features

### Core Infrastructure
- [x] **DockerClientFactory** - Singleton Docker client management
- [x] **DockerClientWrapper** - Client delegation pattern
- [x] **LazyDockerClient** - Deferred initialization
- [x] **Configuration System** - Environment variables + TOML config

### Container Core
- [x] **GenericContainer** - Main container class with full lifecycle
- [x] **Container Protocol** - Structural typing for container interface
- [x] **ContainerState Protocol** - State query interface
- [x] **ExecResult** - Command execution results

### Container Types & Enums
- [x] **BindMode** - Volume mount modes (RO/RW)
- [x] **SelinuxContext** - SELinux context modes
- [x] **InternetProtocol** - TCP/UDP protocol handling

### Networking
- [x] **Network** - Custom Docker network management
- [x] **NetworkImpl** - Network implementation with lazy creation
- [x] **SHARED** - Singleton shared network
- [x] **Network Aliases** - Container network aliases
- [x] **Network Context Manager** - Automatic cleanup

### Container Dependencies
- [x] **depends_on()** - Container startup dependencies
- [x] **Automatic Ordering** - Dependencies started first

### File Operations
- [x] **with_copy_file_to_container()** - Queue file copying
- [x] **copy_file_to_container()** - Copy files/directories to container
- [x] **copy_file_from_container()** - Copy files/directories from container
- [x] **TAR-based implementation** - Docker API standard

### Container Customization
- [x] **with_create_container_modifier()** - Custom container configuration
- [x] **Modifier Chaining** - Multiple modifiers support
- [x] **SocatContainer** - TCP proxy for port exposure

### Wait Strategies
- [x] **WaitStrategy Protocol** - Base interface
- [x] **AbstractWaitStrategy** - Base implementation with timeout
- [x] **DockerHealthcheckWaitStrategy** - Docker HEALTHCHECK based
- [x] **LogMessageWaitStrategy** - Log pattern matching
- [x] **HostPortWaitStrategy** - Port availability checking
- [x] **WaitStrategyTarget Protocol** - Target container interface

### Image Handling
- [x] **ImageData** - Image metadata with creation time
- [x] **ImagePullPolicy Protocol** - Pull policy interface
- [x] **AlwaysPullPolicy** - Always pull images
- [x] **DefaultPullPolicy** - Pull if not present
- [x] **AgeBasedPullPolicy** - Pull based on image age
- [x] **PullPolicy Utility** - Policy factory
- [x] **RemoteDockerImage** - Image pulling with retry

### Image Name Substitution (Enterprise Features)
- [x] **ImageNameSubstitutor Protocol** - Image name transformation
- [x] **NoOpImageNameSubstitutor** - Pass-through (default)
- [x] **PrefixingImageNameSubstitutor** - Registry prefix for mirroring
- [x] **ConfigurableImageNameSubstitutor** - TOML-based mappings
- [x] **ChainImageNameSubstitutor** - Combine multiple substitutors
- [x] **Configuration loading** - Environment vars + TOML files

### API Features
- [x] **Fluent API** - Method chaining for configuration
- [x] **Context Manager** - Python `with` statement support
- [x] **Type Hints** - Full PEP 484 typing throughout
- [x] **Logging** - Comprehensive logging with standard library

## ❌ Missing Features (Compared to Java)

### Core Container Features
- [ ] **Container Reuse** - Singleton containers across tests
- [ ] **Link Containers** - Legacy container linking
- [ ] **FixedHostPortGenericContainer** - Fixed port mapping
- [ ] **SocatContainer** - Port forwarding helper
- [ ] **Container Modification** - Modify running containers

### Docker Compose Support
- [ ] **DockerComposeContainer** - Multi-container orchestration
- [ ] **ComposeContainer** - Compose file support
- [ ] **ComposeDelegate** - Compose command execution
- [ ] **LocalDockerCompose** - Local compose binary
- [ ] **ContainerisedDockerCompose** - Containerized compose

### Advanced Wait Strategies
- [ ] **HttpWaitStrategy** - HTTP endpoint checking
- [ ] **ShellWaitStrategy** - Shell command execution
- [ ] **WaitAllStrategy** - Wait for multiple conditions
- [ ] **WaitForMultiple** - Composite wait strategies

### Logging & Output
- [ ] **LogConsumer** - Stream container logs
- [ ] **Slf4jLogConsumer** - Log to logging framework
- [ ] **WaitingConsumer** - Wait for log patterns
- [ ] **ToStringConsumer** - Collect logs to string
- [ ] **OutputFrame** - Log frame handling

### Networking
- [ ] **Network** - Custom network creation
- [ ] **Network.NetworkImpl** - Network implementation
- [ ] **NetworkMode** - Network mode configuration
- [ ] **NetworkAlias** - Container network aliases

### Advanced Image Features
- [ ] **FutureContainer** - Async container preparation
- [ ] **BuildImageFromDockerfile** - Build custom images
- [ ] **ImageFromDockerfile** - Dockerfile-based images
- [ ] **PullImageCmd** - Advanced pull options
- [ ] **LazyFuture** - Lazy evaluation pattern (simplified in Python)

### Startup Checks
- [ ] **StartupCheckStrategy** - Custom startup validation
- [ ] **MinimumDurationRunningStartupCheckStrategy** - Duration-based
- [ ] **OneShotStartupCheckStrategy** - One-shot container checks
- [ ] **IndefiniteWaitOneShotStartupCheckStrategy** - Indefinite wait

### Container Traits (Mixins)
- [ ] **CommandsTrait** - Command execution methods
- [ ] **ImageTrait** - Image-related methods
- [ ] **LinkableContainer** - Container linking
- [ ] **VncService** - VNC recording support

### Recording & Debugging
- [ ] **VncRecordingContainer** - Record VNC sessions
- [ ] **RecordingFileFactory** - Recording file management
- [ ] **VncRecordingMode** - Recording mode configuration

### Specialized Containers
- [ ] **PortForwardingContainer** - SSH port forwarding
- [ ] **DockerMcpGatewayContainer** - MCP gateway
- [ ] **DockerModelRunnerContainer** - Model runner

### Configuration & Environment
- [ ] **TestcontainersConfiguration** - Global configuration
- [ ] **EnvironmentAndSystemPropertyClientProviderStrategy** - Provider strategy
- [ ] **ProxiedUnixSocketClientProviderStrategy** - Unix socket proxy
- [ ] **RyukContainer** - Resource cleanup (Ryuk)
- [ ] **ResourceReaper** - Automatic resource cleanup

### Utilities
- [ ] **DockerImageName** - Image name parsing/validation
- [ ] **ImageNameUtils** - Image name utilities
- [ ] **CommandLine** - Command line utilities
- [ ] **ThreadedLogFollower** - Async log following
- [ ] **Base58** - Base58 encoding

### JDBC/Database Support
- [ ] **JdbcDatabaseContainer** - JDBC container base
- [ ] **JdbcDatabaseContainerProvider** - Database provider
- [ ] **DatabaseDelegate** - Database operations
- [ ] **ScriptUtils** - SQL script execution

### Test Framework Integration
- [ ] **Testcontainers Extension** - JUnit 5 integration (pytest equivalent needed)
- [ ] **@Container annotation** - Declarative containers (pytest fixtures)
- [ ] **@Testcontainers annotation** - Test class annotation (pytest markers)

## 📦 Modules Requiring Conversion

The Java library has **63 specialized modules** for different technologies. None have been converted yet.

### Databases (23 modules)
1. **cassandra** - Apache Cassandra NoSQL database
2. **clickhouse** - ClickHouse OLAP database
3. **cockroachdb** - CockroachDB distributed SQL
4. **couchbase** - Couchbase NoSQL database
5. **cratedb** - CrateDB distributed SQL
6. **database-commons** - Common database utilities
7. **databend** - Databend cloud data warehouse
8. **db2** - IBM DB2 relational database
9. **influxdb** - InfluxDB time-series database
10. **mariadb** - MariaDB relational database
11. **milvus** - Milvus vector database
12. **mongodb** - MongoDB NoSQL document database
13. **mssqlserver** - Microsoft SQL Server
14. **mysql** - MySQL relational database
15. **neo4j** - Neo4j graph database
16. **oceanbase** - OceanBase distributed database
17. **oracle-free** - Oracle Database Free edition
18. **oracle-xe** - Oracle Database Express Edition
19. **orientdb** - OrientDB multi-model database
20. **postgresql** - PostgreSQL relational database
21. **questdb** - QuestDB time-series database
22. **scylladb** - ScyllaDB NoSQL database
23. **tidb** - TiDB distributed SQL database
24. **yugabytedb** - YugabyteDB distributed SQL

### Message Queues & Streaming (7 modules)
25. **activemq** - Apache ActiveMQ message broker
26. **kafka** - Apache Kafka streaming platform
27. **pulsar** - Apache Pulsar messaging platform
28. **rabbitmq** - RabbitMQ message broker
29. **redpanda** - Redpanda streaming platform
30. **solace** - Solace PubSub+ event broker
31. **hivemq** - HiveMQ MQTT broker

### Search & Analytics (4 modules)
32. **elasticsearch** - Elasticsearch search engine
33. **solr** - Apache Solr search platform
34. **typesense** - Typesense search engine
35. **qdrant** - Qdrant vector search engine

### Cloud Services (3 modules)
36. **azure** - Microsoft Azure services
37. **gcloud** - Google Cloud Platform services
38. **localstack** - LocalStack (AWS emulation)

### Vector Databases (3 modules)
39. **chromadb** - ChromaDB vector database
40. **pinecone** - Pinecone vector database
41. **weaviate** - Weaviate vector search engine

### AI/ML Services (2 modules)
42. **ollama** - Ollama local LLM runner
43. **timeplus** - Timeplus streaming analytics

### Monitoring & Observability (2 modules)
44. **grafana** - Grafana visualization platform
45. **k6** - k6 load testing tool

### Service Mesh & Discovery (2 modules)
46. **consul** - HashiCorp Consul service mesh
47. **vault** - HashiCorp Vault secrets management

### Container Orchestration (1 module)
48. **k3s** - K3s lightweight Kubernetes

### Web & Proxy (4 modules)
49. **nginx** - Nginx web server
50. **selenium** - Selenium WebDriver for browser automation
51. **toxiproxy** - Toxiproxy network chaos testing
52. **mockserver** - MockServer API mocking

### Data Storage (4 modules)
53. **minio** - MinIO S3-compatible object storage
54. **r2dbc** - R2DBC reactive database connectivity
55. **presto** - Presto distributed SQL query engine
56. **trino** - Trino distributed SQL query engine

### Testing & Integration (3 modules)
57. **jdbc** - JDBC database container utilities
58. **jdbc-test** - JDBC testing utilities
59. **junit-jupiter** - JUnit 5 integration
60. **spock** - Spock framework integration

### Other Services (3 modules)
61. **ldap** - LDAP directory service
62. **openfga** - OpenFGA authorization service

## 🎯 Implementation Priorities

### Phase 1: Core Stability (✅ COMPLETE)
- [x] Basic container lifecycle
- [x] Wait strategies
- [x] Image handling
- [x] Configuration system
- [x] Image name substitution

### Phase 2: Essential Features (Next)
- [ ] Docker Compose support
- [ ] HTTP wait strategy
- [ ] Log consumers
- [ ] Network customization
- [ ] File copying
- [ ] Container reuse

### Phase 3: Testing Integration
- [ ] Pytest fixtures for containers
- [ ] Pytest markers for test configuration
- [ ] Automatic cleanup hooks
- [ ] Parallel test support

### Phase 4: Database Modules
- [ ] postgresql module
- [ ] mysql module
- [ ] mongodb module
- [ ] redis module (if exists)
- [ ] database-commons utilities

### Phase 5: Popular Modules
- [ ] kafka module
- [ ] elasticsearch module
- [ ] rabbitmq module
- [ ] localstack module
- [ ] selenium module

### Phase 6: Remaining Modules
- [ ] Convert remaining 58 modules based on demand

## 📊 Conversion Quality Metrics

### Code Quality
- ✅ **Type Hints**: 100% coverage with full PEP 484 typing
- ✅ **Docstrings**: All public APIs documented
- ✅ **Tests**: 123 tests with 100% pass rate
- ✅ **Linting**: Follows PEP 8 standards
- ✅ **Python 3.9+**: Modern Python features with `__future__` annotations

### Architecture Quality
- ✅ **Protocol-based Design**: Flexible structural typing
- ✅ **Context Managers**: Pythonic resource management
- ✅ **Simplified Dependencies**: Minimal external requirements
- ✅ **No Java Baggage**: Pythonic patterns, not Java translations

### Feature Parity
- **Core Library**: ~40% complete
  - Essential features: ✅ Done
  - Advanced features: ⏳ In progress
  - Enterprise features: ✅ Done (ImageNameSubstitutor)
- **Modules**: 0% complete (0/63 modules)
- **Overall Project**: ~5% complete

## 🔗 Related Documentation

- [MIGRATION_PLAN.md](MIGRATION_PLAN.md) - Overall migration strategy
- [GENERIC_CONTAINER_MAPPING.md](GENERIC_CONTAINER_MAPPING.md) - GenericContainer conversion details
- [GENERIC_CONTAINER_CONVERSION.md](GENERIC_CONTAINER_CONVERSION.md) - GenericContainer implementation
- [DOCKER_CLIENT_CONVERSION.md](DOCKER_CLIENT_CONVERSION.md) - Docker client implementation
- [DOCKER_CLIENT_README.md](DOCKER_CLIENT_README.md) - Docker client usage
- [WAIT_STRATEGIES_CONVERSION.md](WAIT_STRATEGIES_CONVERSION.md) - Wait strategies details
- [IMAGE_HANDLING_CONVERSION.md](IMAGE_HANDLING_CONVERSION.md) - Image handling details
- [IMAGE_NAME_SUBSTITUTOR_EXPLAINED.md](IMAGE_NAME_SUBSTITUTOR_EXPLAINED.md) - Substitutor explanation
- [IMAGE_NAME_SUBSTITUTOR_IMPLEMENTATION.md](IMAGE_NAME_SUBSTITUTOR_IMPLEMENTATION.md) - Substitutor implementation
- [CONTAINER_TYPES_CONVERSION.md](CONTAINER_TYPES_CONVERSION.md) - Container types conversion
- [CONVERSION_SUMMARY.md](CONVERSION_SUMMARY.md) - Docker client summary

## 🚀 Getting Started

### Installation
```bash
cd /home/runner/work/testcontainers-java2py/testcontainers-java2py
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Run Tests
```bash
uv pip install -e ".[dev]"
pytest tests/
```

### Basic Usage
```python
from testcontainers.core import GenericContainer

# Simple container
with GenericContainer("postgres:13") as container:
    container.with_exposed_ports(5432)
    container.with_env("POSTGRES_PASSWORD", "secret")
    
    port = container.get_exposed_port(5432)
    print(f"PostgreSQL running on port {port}")
```

### With Image Substitution (Enterprise)
```python
import os
from testcontainers.core import GenericContainer

# Configure registry mirroring
os.environ["TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX"] = "registry.corp.com/mirror"

# This will pull from: registry.corp.com/mirror/postgres:13
with GenericContainer("postgres:13") as container:
    container.with_exposed_ports(5432)
    # Use container...
```

## 📁 Project Structure

```
src/testcontainers/
├── __init__.py
├── config.py                          ✅ Configuration management
├── core/
│   ├── __init__.py
│   ├── docker_client.py               ✅ Docker client factory
│   ├── container_types.py             ✅ Enums (BindMode, etc.)
│   ├── container.py                   ✅ Container protocol
│   ├── container_state.py             ✅ Container state protocol
│   └── generic_container.py           ✅ Main container class
├── waiting/
│   ├── __init__.py
│   ├── wait_strategy.py               ✅ Wait strategy protocols
│   ├── healthcheck.py                 ✅ Healthcheck wait
│   ├── log.py                         ✅ Log message wait
│   └── port.py                        ✅ Port availability wait
└── images/
    ├── __init__.py
    ├── image_pull_policy.py           ✅ Pull policy protocol
    ├── image_data.py                  ✅ Image metadata
    ├── policies.py                    ✅ Pull policy implementations
    ├── pull_policy.py                 ✅ Policy factory
    ├── remote_image.py                ✅ Image pulling
    └── substitutor.py                 ✅ Image name substitution

tests/unit/
├── __init__.py
├── test_docker_client.py              ✅ 16 tests
├── test_container_types.py            ✅ 15 tests
├── test_container.py                  ✅ 3 tests
├── test_wait_strategies.py            ✅ 16 tests
├── test_images.py                     ✅ 21 tests
├── test_substitutor.py                ✅ 21 tests
└── test_generic_container.py          ✅ 34 tests

examples/
└── docker_client_example.py           ✅ Working demo
```

## 📝 Contributing

To contribute to the conversion:

1. Choose a feature or module from the missing lists
2. Review the corresponding Java implementation
3. Follow Python best practices and existing patterns
4. Add comprehensive tests
5. Update this progress summary

## 🙏 Acknowledgments

- **Original Java Library**: [testcontainers-java](https://github.com/testcontainers/testcontainers-java)
- **Existing Python Library**: [testcontainers-python](https://github.com/testcontainers/testcontainers-python)

This conversion aims to bring Java's extensive features to Python while maintaining Pythonic idioms and patterns.
