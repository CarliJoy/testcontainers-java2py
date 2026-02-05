# Java to Python Module Comparison

This document provides a comprehensive comparison of all Python modules in `src/testcontainers/modules/` with their corresponding Java sources in `modules/`.

## Table of Contents

1. [PostgreSQL](#1-postgresql)
2. [MySQL](#2-mysql)
3. [MongoDB](#3-mongodb)
4. [Kafka](#4-kafka)
5. [Elasticsearch](#5-elasticsearch)
6. [Redis](#6-redis)
7. [RabbitMQ](#7-rabbitmq)
8. [MariaDB](#8-mariadb)
9. [Cassandra](#9-cassandra)
10. [Neo4j](#10-neo4j)
11. [LocalStack](#11-localstack)
12. [Selenium](#12-selenium)
13. [ClickHouse](#13-clickhouse)
14. [MS SQL Server](#14-ms-sql-server)
15. [CouchDB](#15-couchdb)
16. [CockroachDB](#16-cockroachdb)
17. [InfluxDB](#17-influxdb)
18. [Nginx](#18-nginx)
19. [Vault](#19-vault)
20. [Solr](#20-solr)
21. [MockServer](#21-mockserver)
22. [Toxiproxy](#22-toxiproxy)
23. [Pulsar](#23-pulsar)
24. [Oracle Free](#24-oracle-free)
25. [Redpanda](#25-redpanda)
26. [MinIO](#26-minio)
27. [Memcached](#27-memcached)
28. [ActiveMQ](#28-activemq)
29. [ChromaDB](#29-chromadb)
30. [Qdrant](#30-qdrant)
31. [Weaviate](#31-weaviate)
32. [Typesense](#32-typesense)
33. [NATS](#33-nats)

---

## 1. PostgreSQL

**Java Source:** `modules/postgresql/src/main/java/org/testcontainers/containers/PostgreSQLContainer.java`  
**Python Module:** `src/testcontainers/modules/postgres.py`

### ✅ Matching Features
- Environment variables: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Default port: 5432
- Default credentials: test/test/test
- Wait strategy: LogMessageWaitStrategy with regex `.*database system is ready to accept connections.*` (2 times)
- Driver class name: `org.postgresql.Driver`
- JDBC URL construction

### ❌ Missing in Python
- Explicit command setup: `postgres -c fsync=off`
- Startup timeout on wait strategy (60 seconds)
- Builder methods: `with_username()`, `with_password()`, `with_database_name()`
- `get_test_query_string()` method (returns "SELECT 1")
- URL parameter customization via `withUrlParam()`
- Support for alternative images (pgvector/pgvector)

### ⚠️ Different
- **Image**: Python uses `postgres:16` (hardcoded), Java uses `postgres:9.6.12` (deprecated)
- **Environment variable setup timing**: Python in constructor, Java in `configure()` method
- **Port exposure**: Python relies on parent class, Java explicitly adds port

---

## 2. MySQL

**Java Source:** `modules/mysql/src/main/java/org/testcontainers/containers/MySQLContainer.java`  
**Python Module:** `src/testcontainers/modules/mysql.py`

### ✅ Matching Features
- Default port: 3306
- Default credentials: test/test/test
- Environment variables: `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_ROOT_PASSWORD`
- Wait strategy: LogMessageWaitStrategy with regex `.*ready for connections.*` (2 times)

### ❌ Missing in Python
- **Port exposure**: Python doesn't call `add_exposed_port(3306)` in constructor
- **Conditional environment variable logic**: Java only sets `MYSQL_USER` if username != "root"
- **Empty password handling**: Java sets `MYSQL_ALLOW_EMPTY_PASSWORD=yes` when password is empty
- **Startup attempts**: Java sets `setStartupAttempts(3)`
- **Configuration override**: Java supports `withConfigurationOverride()` for my.cnf files

### ⚠️ Different
- **Image**: Python uses `mysql:8` (explicit), Java uses `mysql:5.7.34` (deprecated)
- **Environment variables**: Python sets unconditionally, Java uses conditional logic
- **Config approach**: Python builds commands with `--key=value` flags, Java uses file-based override

---

## 3. MongoDB

**Java Source:** `modules/mongodb/src/main/java/org/testcontainers/containers/MongoDBContainer.java`  
**Python Module:** `src/testcontainers/modules/mongodb.py`

### ✅ Matching Features
- Default port: 27017
- Wait strategy: LogMessageWaitStrategy with regex `.*[Ww]aiting for connections.*`
- Port exposure: Both expose 27017

### ❌ Missing in Python
- **Multiple image support**: Java supports 3 images (mongo, mongodb/mongodb-community-server, mongodb/mongodb-enterprise-server)
- **Sharding support**: Java has `withSharding()` method
- **Replica set initialization**: Java auto-initializes single-node replica sets with `rs.initiate()`
- **Replica set URL**: Java provides `getReplicaSetUrl()` for database-specific connections
- **Container execution**: Java can execute commands inside container via `execInContainer()`

### ⚠️ Different
- **Image**: Python uses `mongo:7`, Java uses `mongo:4.0.10` (deprecated)
- **Authentication**: Python sets env vars (`MONGO_INITDB_ROOT_USERNAME`, etc.), Java doesn't use env vars
- **Connection string**: Python uses standard MongoDB URI with optional `authSource`, Java expects replica set format
- **Status**: Java is marked `@Deprecated`

---

## 4. Kafka

**Java Source:** `modules/kafka/src/main/java/org/testcontainers/kafka/KafkaContainer.java`  
**Python Module:** `src/testcontainers/modules/kafka.py`

### ✅ Matching Features
- Exposed port: 9092 (PLAINTEXT_HOST)
- Shared environment variables:
  - `KAFKA_BROKER_ID` / `KAFKA_NODE_ID`: 1
  - `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`: 1
  - `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR`: 1
  - `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR`: 1
  - `KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS`: 0

### ❌ Missing in Python
- **Startup script execution**: Java uses `/tmp/testcontainers_start.sh` wrapper
- **Listener configuration**: Java has `withListener()` methods (2 variants)
- **Dynamic listener management**: Java supports runtime listener configuration via `containerIsStarting()` hook
- **Environment variable**: `KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS`: 1

### ⚠️ Different
- **Image**: Python uses `confluentinc/cp-kafka:7.5.0`, Java uses `apache/kafka` (no tag)
- **Wait strategy**: Python uses `KafkaServer id=\d+.*started`, Java uses `Transitioning from RECOVERY to RUNNING`
- **Command**: Python doesn't set custom command, Java uses startup script
- **Listener setup**: Python uses `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP` with `PLAINTEXT_HOST:PLAINTEXT`

---

## 5. Elasticsearch

**Java Source:** `modules/elasticsearch/src/main/java/org/testcontainers/elasticsearch/ElasticsearchContainer.java`  
**Python Module:** `src/testcontainers/modules/elasticsearch.py`

### ✅ Matching Features
- HTTP port: 9200
- Transport port: 9300
- Environment variable: `discovery.type=single-node`
- Configuration method: `with_password()` / `withPassword()`
- Password environment variable: `ELASTIC_PASSWORD`

### ❌ Missing in Python
- **Certificate management**: Java has `withCertPath()`, `caCertAsBytes()`, `createSslContextFromCa()`
- **Disk threshold config**: Java sets `cluster.routing.allocation.disk.threshold_enabled=false`
- **JVM memory config**: Java uses classpath resource (2GB), Python uses env var (512MB)
- **Version-aware security**: Java handles v8+ secure-by-default differently
- **Transport host getter**: Java has `getTcpHost()` (deprecated)

### ⚠️ Different
- **Image**: Python uses `elasticsearch:8.11.0`, Java uses `docker.elastic.co/elasticsearch/elasticsearch` with version detection
- **Wait strategy**: Python uses HTTP 200 on `/_cluster/health`, Java uses log message pattern `"started"`
- **JVM memory**: Python sets `ES_JAVA_OPTS=-Xms512m -Xmx512m`, Java uses file-based 2GB config
- **Security config**: Java is version-aware, Python always sets in `start()`

### 🔧 Extra in Python
- `get_http_url()` - returns full HTTP URL
- `get_password()` - getter for password
- `get_username()` - getter for username

---

## 6. Redis

**Java Source:** `modules/redis` (GenericContainer pattern in examples)  
**Python Module:** `src/testcontainers/modules/redis.py`

### ✅ Matching Features
- Default port: 6379
- Command support: Both support `withCommand()` / `with_command()`
- Wait strategy: LogMessageWaitStrategy (log-based waiting)
- Port exposure: Both expose 6379

### ⚠️ Different
- **Image**: Python uses `redis:7`, Java examples use `redis:6-alpine` or `redis:7.0.12-alpine`
- **Wait strategy pattern**: Python hardcodes regex `.*Ready to accept connections.*`, Java is configurable

### 🔧 Extra in Python
- `with_password()` method for convenient password setup
- `get_connection_url()` helper for Redis URI generation
- `get_password()` getter
- Auto-configured wait strategy (Java requires manual setup)

**Note:** Java doesn't have a dedicated Redis module, uses GenericContainer pattern. Python provides better abstraction.

---

## 7. RabbitMQ

**Java Source:** `modules/rabbitmq/src/main/java/org/testcontainers/containers/RabbitMQContainer.java`  
**Python Module:** `src/testcontainers/modules/rabbitmq.py`

### ✅ Matching Features
- Default image: `rabbitmq:3-management`
- AMQP port: 5672
- HTTP port: 15672
- Default username: `guest`
- Default password: `guest`
- Environment variables: `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`
- Wait strategy: `Server startup complete` regex

### ❌ Missing in Python
- **AMQPS port (5671)**: Java exposes it
- **HTTPS port (15671)**: Java exposes it
- **Port getter methods**: `getAmqpsPort()`, `getHttpsPort()`
- **URL getters**: `getAmqpsUrl()`, `getHttpsUrl()`
- **SSL configuration**: `withSSL()` methods with certificate/key file support
- **Config file support**: `withRabbitMQConfig()`, `withRabbitMQConfigSysctl()`, `withRabbitMQConfigErlang()`
- **Plugin management**: `withPluginsEnabled()`
- **Deprecated management methods**: `withExchange()`, `withQueue()`, `withBinding()`, `withUser()`, `withPolicy()`, `withVhost()`, `withParameter()`, `withPermission()` (18+ methods)

### ⚠️ Different
- **Method naming**: Java uses `getAdminUsername()` / `withAdminPassword()`, Python uses `get_username()` / `with_password()`
- **AMQP URL format**: Java is `amqp://host:port`, Python is `amqp://user:pass@host:port/vhost`
- **Default tag**: Java uses `3.7.25-management-alpine`, Python uses `3-management`

**Note:** Python implementation is significantly stripped down, missing SSL support and all deprecated RabbitMQ management methods.

---

## 8. MariaDB

**Java Source:** `modules/mariadb/src/main/java/org/testcontainers/containers/MariaDBContainer.java`  
**Python Module:** `src/testcontainers/modules/mariadb.py`

### ✅ Matching Features
- Default port: 3306
- Default username: `test`
- Default password: `test`
- Default database: `test`
- JDBC driver: `org.mariadb.jdbc.Driver`
- Test query: `SELECT 1`
- Environment variables: `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`
- Empty password logic: Restricted to root user only

### ❌ Missing in Python
- **Configuration override**: Java has `withConfigurationOverride()` for my.cnf files
- **Liveness check ports**: Java declares `getLivenessCheckPortNumbers()`
- **Startup attempts**: Java sets `setStartupAttempts(3)`
- **Image flexibility**: Java uses `DockerImageName` with validation

### ⚠️ Different
- **Image**: Python uses `mariadb:10.3.6` (hardcoded, deprecated in Java), Java uses `mariadb` (unversioned)
- **JDBC URL construction**: Java includes URL parameter construction
- **Case-sensitivity**: Java uses `.equalsIgnoreCase()` for root check, Python uses exact `==`

**Note:** Python implementation is functionally minimal but matches core logic. Java version is more robust with configuration flexibility.

---

## 9. Cassandra

**Java Source:** `modules/cassandra/src/main/java/org/testcontainers/containers/CassandraContainer.java`  
**Python Module:** `src/testcontainers/modules/cassandra.py`

### ✅ Matching Features
- Default image: `cassandra:3.11.2`
- CQL port: 9042
- Datacenter: `datacenter1` (default)
- Username/Password: `cassandra`/`cassandra`
- Environment variables (identical):
  - `JVM_OPTS`: `-Dcassandra.skip_wait_for_gossip_to_settle=0 -Dcassandra.initial_token=0`
  - `HEAP_NEWSIZE`: `128M`
  - `MAX_HEAP_SIZE`: `1024M`
  - `CASSANDRA_SNITCH`: `GossipingPropertyFileSnitch`
  - `CASSANDRA_ENDPOINT_SNITCH`: `GossipingPropertyFileSnitch`
  - `CASSANDRA_DC`: `datacenter1`

### ❌ Missing in Python
- **Init script support**: Java has `withInitScript(initScriptPath)`
- **Config override**: Java has `withConfigurationOverride(configLocation)`
- **JMX control**: Java has `withJmxReporting(boolean)`

### ⚠️ Different
- **Wait strategy**: Python uses explicit `LogMessageWaitStrategy().with_regex(r".*Startup complete.*")`, Java uses defaults

### 🔧 Extra in Python
- `with_datacenter(dc_name)` - No Java equivalent
- `with_cluster_name(cluster_id)` - No Java equivalent

---

## 10. Neo4j

**Java Source:** `modules/neo4j/src/main/java/org/testcontainers/containers/Neo4jContainer.java`  
**Python Module:** `src/testcontainers/modules/neo4j.py`

### ✅ Matching Features
- Default image: `neo4j:4.4`
- Bolt port: 7687
- HTTP port: 7474
- HTTPS port: 7473
- Default auth: `neo4j/password`
- Auth disabling: `without_authentication()` / `withoutAuthentication()`
- Plugin support: `with_labs_plugins()` / `withPlugins()`
- Config support: `with_neo4j_config()` / `withNeo4jConfig()`
- Wait strategy: Combined `WaitAllStrategy` with Bolt log pattern and HTTP 200 check

### ❌ Missing in Python
- **Password validation**: Java validates minimum 8 characters for Neo4j 5.3+
- **Port-adaptive wait strategy**: Java switches strategy if only Bolt/HTTP exposed
- **Enterprise support**: Java has `withEnterpriseEdition()`
- **Database copy**: Java has `withDatabase(MountableFile)` for Neo4j 3.5
- **Plugin file mounting**: Java has `withPlugins(MountableFile)`
- **Random password generator**: Java has `withRandomPassword()`

### ⚠️ Different
- **Wait timeout**: Java explicitly sets 2-minute startup timeout
- **Deprecation**: Java version is deprecated, recommends newer neo4j package

---

## 11. LocalStack

**Java Source:** `modules/localstack/src/main/java/org/testcontainers/containers/localstack/LocalStackContainer.java`  
**Python Module:** `src/testcontainers/modules/localstack.py`

### ✅ Matching Features
- Default image base: `localstack/localstack:0.11.2`
- Edge port: 4566
- Wait strategy: LogMessageWaitStrategy with regex `.*Ready\.\n`

### ❌ Missing in Python
- **Version detection**: Java detects version and determines `legacyMode`, `servicesEnvVarRequired`, `isVersion2`
- **Legacy mode support**: Java uses legacy mode (<0.11) with multiple ports, or edge port (≥0.11)
- **Hostname resolution**: Java resolves hostname using `HOSTNAME_EXTERNAL` (v<2) or `LOCALSTACK_HOST` (v2+)
- **Docker socket binding**: Java binds `/var/run/docker.sock` for nested Docker
- **Container labels**: Java passes testcontainers labels to spawned containers (Lambda, ECS, EC2, Batch)
- **Environment variable reading**: Java reads `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DEFAULT_REGION` from env

### ⚠️ Different
- **Services configuration**: Python uses simple string names, Java uses `EnabledService` interface or Service enum
- **Port exposure**: Python exposes only 4566, Java conditionally exposes all service-specific ports in legacy mode
- **Eager service loading**: Java sets `EAGER_SERVICE_LOADING=1` conditionally on version

**Note:** Python implementation is significantly simplified, missing critical features like version detection and legacy mode support.

---

## 12. Selenium

**Java Source:** `modules/selenium/src/main/java/org/testcontainers/containers/BrowserWebDriverContainer.java`  
**Python Module:** `src/testcontainers/modules/selenium.py`

### ✅ Matching Features
- Selenium port: 4444
- VNC port: 5900
- Default VNC password: `secret`
- Chrome image: `selenium/standalone-chrome`
- Firefox image: `selenium/standalone-firefox`
- Edge image: `selenium/standalone-edge`
- Wait strategy: Combined log message check for RemoteWebDriver + port wait + 60s timeout + 3 startup attempts
- Timezone: UTC
- no_proxy: `localhost`

### ❌ Missing in Python
- **VNC recording support**: Java has full `VncRecordingContainer` with modes (`SKIP`, `RECORD_ALL`, `RECORD_FAILING`)
- **Recording format control**: Java has `VncRecordingFormat` configuration
- **Debug image support**: Java supports `-debug` images for Selenium <4
- **Capabilities object**: Java has `withCapabilities()` method + deprecated `withDesiredCapabilities()`
- **Image validation**: Java validates compatibility with browser type

### ⚠️ Different
- **Image versioning**: Python uses explicit `4.16.0`, Java uses dynamic version based on classpath Selenium version
- **Shared memory**: Python uses fixed 2GB for all OS, Java uses Windows: 512MB / Linux: /dev/shm bind mount
- **Timezone config**: Java respects system property, Python always sets UTC

---

## 13. ClickHouse

**Java Source:** `modules/clickhouse/src/main/java/org/testcontainers/clickhouse/ClickHouseContainer.java`  
**Python Module:** `src/testcontainers/modules/clickhouse.py`

### ✅ Matching Features
- HTTP port: 8123
- Native port: 9000
- Default username: `test`
- Default password: `test`
- Default database: `default`
- Driver class: `com.clickhouse.jdbc.Driver`
- Environment variables: `CLICKHOUSE_DB`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`
- Wait strategy: HTTP check on `/` expecting status 200 and response `Ok.` with 60 second timeout

### ⚠️ Different
- **Image**: Python uses `clickhouse/clickhouse-server:latest`, Java uses `clickhouse/clickhouse-server` (no tag)
- **Driver fallback**: Java has dual-driver support (v2 and legacy v1), Python uses only v2
- **Additional features**: Java includes liveness check port configuration and test query string

---

## 14. MS SQL Server

**Java Source:** `modules/mssqlserver/src/main/java/org/testcontainers/containers/MSSQLServerContainer.java`  
**Python Module:** `src/testcontainers/modules/mssqlserver.py`

### ✅ Matching Features
- Default port: 1433
- Default username: `sa`
- Default password: `A_Str0ng_Required_Password`
- Password validation: 4 regex patterns (uppercase, lowercase, digit, non-alphanumeric); min 8, max 128 chars
- Environment variables: `ACCEPT_EULA`, `MSSQL_SA_PASSWORD`

### ⚠️ Different
- **Image**: Python uses `mcr.microsoft.com/mssql/server:2022-latest`, Java uses deprecated image (originally `2017-CU12`)
- **Wait strategy**: Python uses log message `.*SQL Server is now ready for client connections.*`, Java uses JDBC test query
- **License check timing**: Python checks at `start()`, Java checks at `configure()`
- **Java module location**: Deprecated location; newer location at `org.testcontainers.mssqlserver`

---

## 15. CouchDB

**Java Source:** `modules/couchbase` (Note: This is **Couchbase**, not CouchDB - different products!)  
**Python Module:** `src/testcontainers/modules/couchdb.py`

### Important Note
**These are different products:**
- Python implements **CouchDB** (a document database)
- Java implements **Couchbase** (a NoSQL database server)

### CouchDB (Python) Details
- Default image: `couchdb:3`
- Default port: 5984 (HTTP API)
- Default username: `admin`
- Default password: `password`
- Wait strategy: LogMessageWaitStrategy for `Apache CouchDB has started`
- Auth configuration: `with_authentication(username, password)`
- Connection string: `http://username:password@host:port`

**No direct Java equivalent exists for CouchDB. Java has Couchbase which is a different product.**

---

## 16. CockroachDB

**Java Source:** `modules/cockroachdb/src/main/java/org/testcontainers/containers/CockroachContainer.java`  
**Python Module:** `src/testcontainers/modules/cockroachdb.py`

### ✅ Matching Features
- DB port: 26257
- REST API port: 8080
- Default username: `root`
- Default password: Empty string
- Default database: `postgres`
- Min env vars support: v22.1.0+
- Wait strategies: HTTP health check (`/health`) + shell command for v22.1.0+

### ⚠️ Different
- **Image**: Python uses `cockroachdb/cockroach:v23.1.0`, Java uses `cockroachdb/cockroach:v19.2.11` (deprecated)
- **Insecure mode logic**: Python conditionally sets `--insecure` based on password presence, Java sets in constructor then conditionally removes in `configure()`
- **Initialization timing**: Python sets env vars during construction, Java during configuration phase
- **Deprecation status**: Java is marked `@Deprecated`, Python is current

---

## 17. InfluxDB

**Java Source:** `modules/influxdb/src/main/java/org/testcontainers/containers/InfluxDBContainer.java`  
**Python Module:** `src/testcontainers/modules/influxdb.py`

### ✅ Matching Features
- Port: 8086
- Init mode: `DOCKER_INFLUXDB_INIT_MODE=setup` for v2.x

### ❌ Missing in Python
- **InfluxDB 1.x support**: Java fully supports v1.x with separate environment variables
- **Version detection**: Java detects and configures for v1.x or v2.x automatically

### ⚠️ Different
- **Image**: Python uses `influxdb:2.7` (hardcoded v2), Java uses `influxdb:1.4.3` with version detection
- **Wait strategy**: Python uses LogMessageWaitStrategy with regex `(Listening\|ready)`, Java uses HTTP `/ping` endpoint
- **Default username**: Python uses `admin`, Java uses `test-user`
- **Default password**: Python uses `password`, Java uses `test-password`
- **Default admin token**: Python uses `test-token`, Java is optional/empty
- **Configuration methods**: Python has single `with_authentication()`, Java has separate methods

**Note:** Python assumes InfluxDB 2.x only. Java supports both 1.x and 2.x.

---

## 18. Nginx

**Java Source:** `modules/nginx/src/main/java/org/testcontainers/containers/NginxContainer.java`  
**Python Module:** `src/testcontainers/modules/nginx.py`

### ✅ Matching Features
- Default image: `nginx:1.9.4`
- Port: 80
- Command: `["nginx", "-g", "daemon off;"]` / `setCommand("nginx", "-g", "daemon off;")`
- Custom content support: `with_custom_content()` / `withCustomContent()` (mounts to `/usr/share/nginx/html`)

### ⚠️ Different
- **URL construction**: Python returns string, Java returns URL object
- **Deprecation**: Java is marked `@Deprecated`, recommends `org.testcontainers.nginx.NginxContainer`
- **Interface support**: Java implements `LinkableContainer`, Python doesn't

---

## 19. Vault

**Java Source:** `modules/vault/src/main/java/org/testcontainers/vault/VaultContainer.java`  
**Python Module:** `src/testcontainers/modules/vault.py`

### ✅ Matching Features
- Port: 8200
- Default VNC password: `secret`

### ❌ Missing in Python
- **Secrets support**: Java has `withSecretInVault()` (deprecated) and `withInitCommand()`

### ⚠️ Different
- **Image**: Python uses `hashicorp/vault:latest`, Java uses `hashicorp/vault:1.1.3`
- **Dev mode**: Python explicitly runs `vault server -dev`, Java relies on environment variables
- **Token env vars**: Java sets both `VAULT_DEV_ROOT_TOKEN_ID` and `VAULT_TOKEN`, Python only sets first
- **Capabilities**: Java adds `IPC_LOCK`, Python disables mlock with `SKIP_SETCAP=true`
- **Listening address**: Python sets `VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200`, Java sets `VAULT_ADDR=http://0.0.0.0:8200`
- **Health check**: Python accepts [200, 429, 472, 473], Java accepts only 200

### 🔧 Extra in Python
- `get_token()` - Token getter method

---

## 20. Solr

**Java Source:** `modules/solr/src/main/java/org/testcontainers/containers/SolrContainer.java`  
**Python Module:** `src/testcontainers/modules/solr.py`

### ✅ Matching Features
- Solr port: 8983

### ⚠️ Different
- **Image**: Python uses `solr:latest`, Java uses `solr` (no tag)
- **Wait strategy**: Python uses HTTP check on `/solr/admin/info/system`, Java uses log pattern `Server Started` (60s timeout)
- **Solr mode**: Python always starts in cloud mode (`-c` flag), Java starts in standalone by default
- **Zookeeper handling**: Python expects external Zookeeper (sets `ZK_HOST`), Java supports embedded Zookeeper (`-DzkRun`)
- **Port exposure**: Python only exposes 8983, Java exposes both 8983 and 9983 (Zookeeper)
- **Collection creation**: Python in `start()`, Java in `containerIsStarted()` with version-specific handling

**Recommendation:** Python should align with Java's log-based wait strategy and expose Zookeeper port.

---

## 21. MockServer

**Java Source:** `modules/mockserver/src/main/java/org/testcontainers/containers/MockServerContainer.java`  
**Python Module:** `src/testcontainers/modules/mockserver.py`

### ✅ Matching Features
- Port: 1080
- Command: `-serverPort 1080`
- Wait strategy: Log message pattern `.*started on port: 1080.*`

### ⚠️ Different
- **Image**: Python uses `mockserver/mockserver:5.15.0`, Java uses deprecated `jamesdbloom/mockserver:mockserver-5.5.4`
- **Deprecation**: Java is marked `@Deprecated`, recommends `org.testcontainers.mockserver` package

### 🔧 Extra in Python
- `get_url()` helper method for endpoint generation

---

## 22. Toxiproxy

**Java Source:** `modules/toxiproxy/src/main/java/org/testcontainers/containers/ToxiproxyContainer.java`  
**Python Module:** `src/testcontainers/modules/toxiproxy.py`

### ✅ Matching Features
- Control port: 8474
- Proxy port range: 8666-8697 (32 ports)
- Wait strategy: HTTP check on `/version` endpoint

### ❌ Missing in Python
- **Built-in proxy creation**: Java has deprecated `getProxy()` methods with automatic port allocation

### ⚠️ Different
- **Image**: Python uses `ghcr.io/shopify/toxiproxy:2.5.0`, Java uses `shopify/toxiproxy:2.1.0`
- **Proxy management**: Python relies on external `toxiproxy-python` library, Java had built-in proxy helpers (now deprecated)
- **Deprecation**: Java is deprecated, recommends `org.testcontainers.toxiproxy.ToxiproxyContainer`

---

## 23. Pulsar

**Java Source:** `modules/pulsar/src/main/java/org/testcontainers/containers/PulsarContainer.java`  
**Python Module:** `src/testcontainers/modules/pulsar.py`

### ✅ Matching Features
- Broker port: 6650
- HTTP port: 8080
- Base command: `bin/pulsar standalone`

### ❌ Missing in Python
- **Transaction support**: Java has `withTransactions()` method
- **Functions worker**: Java has `withFunctionsWorker()` method

### ⚠️ Different
- **Image**: Python uses `apachepulsar/pulsar:latest`, Java uses `apachepulsar/pulsar:3.0.0`
- **Wait strategy**: Python uses single HTTP check on `/admin/v2/clusters`, Java uses composite strategy adapting to enabled features
- **Startup command**: Java uses complex bash command with `apply-config-from-env.py` and conditional flags
- **Deprecation**: Java is marked `@Deprecated`

---

## 24. Oracle Free

**Java Source:** `modules/oracle-free/src/main/java/org/testcontainers/oracle/OracleContainer.java`  
**Python Module:** `src/testcontainers/modules/oracle_free.py`

### ✅ Matching Features
- Default image: `gvenzl/oracle-free:slim`
- Port: 1521
- Default username: `test`
- Default password: `test`
- Default database name: `freepdb1`
- Default SID: `free`
- Wait strategy: LogMessageWaitStrategy with `.*DATABASE IS READY TO USE!.*`
- Environment variables: `ORACLE_PASSWORD`, `APP_USER`, `APP_USER_PASSWORD`, `ORACLE_DATABASE`

### ⚠️ Different
- **Startup timeout**: Python uses default, Java explicitly sets 60 seconds
- **Connect timeout**: Python uses default, Java explicitly sets 60 seconds

**Note:** Python implementation matches oracle-free Java version exactly. Oracle XE (different Java module) uses different image/database/SID.

---

## 25. Redpanda

**Java Source:** `modules/redpanda/src/main/java/org/testcontainers/redpanda/RedpandaContainer.java`  
**Python Module:** `src/testcontainers/modules/redpanda.py`

### ✅ Matching Features
- Kafka broker port: 9092
- Admin API port: 9644
- Schema Registry port: 8081
- REST Proxy port: 8082
- Wait strategy: LogMessageWaitStrategy with `.*Successfully started Redpanda!.*`
- Command: `redpanda start --mode=dev-container --smp=1 --memory=1G`
- Configuration methods: Authorization, SASL, Schema Registry auth, superuser, listeners

### ⚠️ Different
- **Image**: Python hardcodes `redpandadata/redpanda:v23.3.1`, Java accepts custom image with version validation (>= v22.2.1)
- **Method naming**: Python uses `with_` prefix, Java uses `enable`/`with` prefix
- **Configuration generation**: Java uses FreeMarker templates, Python uses inline generation

---

## 26. MinIO

**Java Source:** `modules/minio/src/main/java/org/testcontainers/containers/MinioContainer.java`  
**Python Module:** `src/testcontainers/modules/minio.py`

### ✅ Matching Features
- API port: 9000
- Console port: 9001
- Default access key: `minioadmin`
- Default secret key: `minioadmin`
- Wait strategy: HTTP check on `/minio/health/live`

### ⚠️ Different
- **Image**: Python uses `minio/minio:latest`, Java uses `minio/minio` (no tag)
- **Wait timeout**: Java explicitly sets 60 seconds, Python uses default
- **Credentials setup**: Java uses `configure()` override (lazy init), Python sets in `__init__`
- **Method naming**: Java uses camelCase, Python uses snake_case

**Note:** Neither implementation explicitly handles region configuration.

---

## 27. Memcached

**Java Source:** None (No Java equivalent exists)  
**Python Module:** `src/testcontainers/modules/memcached.py`

### 🔧 Python-Only Module
- Default image: `memcached:latest`
- Port: 11211
- Wait strategy: `HostPortWaitStrategy` - waits for port availability
- Configuration methods: `get_connection_url()`, `get_port()`

**Note:** This is a Python-only module without a corresponding Java reference implementation.

---

## 28. ActiveMQ

**Java Source:** `modules/activemq/src/main/java/org/testcontainers/activemq/ActiveMQContainer.java` and `ArtemisContainer.java`  
**Python Module:** `src/testcontainers/modules/activemq.py`

### ✅ Matching Features
- OpenWire/TCP port: 61616
- Console port: 8161
- Default credentials: `admin`/`admin`

### ❌ Missing in Python
- **Additional protocol ports**: STOMP (61613), AMQP (5672), MQTT (1883), WebSocket (61614)

### ⚠️ Different
- **Image**: Python uses `apache/activemq-classic:latest`, Java uses `apache/activemq-classic` or `apache/activemq-artemis`
- **Wait strategy**: Python uses HTTP GET `/admin` (expects 200/401), Java uses log message patterns
- **Default credentials**: Java ActiveMQ has no defaults, Java Artemis has `artemis`/`artemis`

**Note:** Python only exposes 2 ports (OpenWire + Console). Java exposes 6+ protocol ports.

---

## 29. ChromaDB

**Java Source:** `modules/chromadb/src/main/java/org/testcontainers/chromadb/ChromaDBContainer.java`  
**Python Module:** `src/testcontainers/modules/chromadb.py`

### ✅ Matching Features
- Port: 8000
- Wait strategy: HTTP GET on heartbeat endpoint

### ⚠️ Different
- **Image**: Python uses `chromadb/chroma:latest`, Java uses `chromadb/chroma` (supports multiple versions)
- **Wait endpoint**: Python checks `/api/v1/heartbeat`, Java checks `/api/v1/heartbeat` or `/api/v2/heartbeat` (version-aware)

### 🔧 Extra in Python
- **Token authentication**: Python has `with_auth_token()` via `CHROMA_SERVER_AUTHN_CREDENTIALS` env var

---

## 30. Qdrant

**Java Source:** `modules/qdrant/src/main/java/org/testcontainers/qdrant/QdrantContainer.java`  
**Python Module:** `src/testcontainers/modules/qdrant.py`

### ✅ Matching Features - Full Feature Parity
- Default image: `qdrant/qdrant`
- REST port: 6333
- gRPC port: 6334
- API key configuration: `with_api_key()` / `withApiKey()` → `QDRANT__SERVICE__API_KEY`
- Config file support: `with_config_file()` / `withConfigFile()`
- Wait strategy: HTTP GET `/readyz` on port 6333

### ⚠️ Different
- **Config file handling**: Python uses filepath, Java uses Transferable object model

---

## 31. Weaviate

**Java Source:** `modules/weaviate/src/main/java/org/testcontainers/weaviate/WeaviateContainer.java`  
**Python Module:** `src/testcontainers/modules/weaviate.py`

### ✅ Matching Features - Full Feature Parity
- Default image: `cr.weaviate.io/semitechnologies/weaviate`
- HTTP port: 8080
- gRPC port: 50051
- Anonymous access: Enabled by default (`AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true`)
- Wait strategy: HTTP GET `/v1/.well-known/ready` on port 8080
- Environment variable configuration: `with_env()` / `withEnv()`

---

## 32. Typesense

**Java Source:** `modules/typesense/src/main/java/org/testcontainers/typesense/TypesenseContainer.java`  
**Python Module:** `src/testcontainers/modules/typesense.py`

### ✅ Matching Features
- Port: 8108
- Default API key: `testcontainers`
- API key configuration: `with_api_key()` / `withApiKey()` → `TYPESENSE_API_KEY`
- Wait strategy: HTTP GET `/health` (expects 200, response contains `"ok":true`)

### ⚠️ Different
- **Image**: Python uses `typesense/typesense:27.0`, Java uses `typesense/typesense` (no version)
- **Configuration timing**: Python sets API key in `start()`, Java uses `configure()` lifecycle hook

---

## 33. NATS

**Java Source:** None (No Java equivalent exists)  
**Python Module:** `src/testcontainers/modules/nats.py`

### 🔧 Python-Only Module
This module has no corresponding Java implementation.

---

## Summary Statistics

| Status | Count | Modules |
|--------|-------|---------|
| **Full Parity** | 2 | Qdrant, Weaviate |
| **Close Match** | 20 | PostgreSQL, MySQL, MariaDB, ClickHouse, Oracle Free, Redis, Cassandra, Neo4j, MockServer, Nginx, Vault, CockroachDB, MS SQL Server, MinIO, Redpanda, Typesense, ChromaDB, Toxiproxy, Selenium, Pulsar |
| **Significant Gaps** | 8 | Kafka, Elasticsearch, RabbitMQ, MongoDB, LocalStack, InfluxDB, Solr, ActiveMQ |
| **Python-Only** | 2 | Memcached, NATS |
| **Different Product** | 1 | CouchDB (Java has Couchbase) |

---

## Common Patterns of Differences

### 1. **Image Versioning**
- **Python**: Often hardcodes versions (e.g., `postgres:16`, `mysql:8`)
- **Java**: Uses `DockerImageName` with flexible version support

### 2. **Wait Strategies**
- **Python**: Tends to use HTTP-based wait strategies
- **Java**: Often uses log message-based wait strategies
- **Impact**: HTTP checks may be more reliable but require endpoint availability

### 3. **Configuration Methods**
- **Python**: Prefers single methods with multiple parameters (e.g., `with_authentication(user, pass, db)`)
- **Java**: Uses builder pattern with individual setters (e.g., `withUsername()`, `withPassword()`)

### 4. **Lifecycle Hooks**
- **Python**: Sets configuration in `__init__` or `start()`
- **Java**: Uses `configure()` and `containerIsStarting()` hooks

### 5. **Missing Advanced Features in Python**
- SSL/TLS configuration (RabbitMQ, Elasticsearch)
- Version detection (InfluxDB, LocalStack, Elasticsearch)
- Legacy mode support (LocalStack, Kafka)
- VNC recording (Selenium)
- Init scripts (Cassandra, Vault)
- Transaction support (Pulsar)

---

## Priority Fixes Needed

### High Priority (Functional Gaps)
1. **MySQL**: Missing `add_exposed_port(3306)` and conditional env var logic
2. **Kafka**: Missing listener configuration methods
3. **Elasticsearch**: Missing certificate management
4. **RabbitMQ**: Missing SSL support and AMQPS/HTTPS ports
5. **LocalStack**: Missing version detection and legacy mode
6. **MongoDB**: Missing replica set initialization and sharding

### Medium Priority (Configuration Flexibility)
1. **PostgreSQL**: Add builder methods and command setup
2. **InfluxDB**: Add InfluxDB 1.x support
3. **Solr**: Align wait strategy and expose Zookeeper port
4. **Selenium**: Add VNC recording support
5. **Neo4j**: Add password validation and enterprise support

### Low Priority (Nice to Have)
1. **Redis**: Already has better abstraction than Java
2. **Cassandra**: Add init script support
3. **Vault**: Add secrets pre-loading
4. **Pulsar**: Add transaction and functions worker support

---

## Conclusion

The Python implementation provides good coverage of core functionality across all major modules. However, there are notable gaps in:

1. **Advanced configuration options** (SSL, certificates, init scripts)
2. **Version detection** and **legacy mode support**
3. **Builder pattern methods** for flexible configuration
4. **Complex features** like replica sets, sharding, transactions

Most modules match or closely match their Java counterparts in basic functionality. The Python-specific improvements (like Redis abstraction) show good engineering judgment. Priority should be given to fixing functional gaps in high-usage modules like MySQL, Kafka, and Elasticsearch.
