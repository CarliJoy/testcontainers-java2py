"""
Testcontainers specialized modules for common technologies.

This package contains ready-to-use container implementations for
popular databases, message queues, search engines, and other services.
"""

from __future__ import annotations

__all__ = [
    "JdbcDatabaseContainer",
    "PostgreSQLContainer",
    "MySQLContainer",
    "MariaDBContainer",
    "MongoDBContainer",
    "RedisContainer",
    "CassandraContainer",
    "Neo4jContainer",
    "InfluxDBContainer",
    "CouchDBContainer",
    "KafkaContainer",
    "ElasticsearchContainer",
    "RabbitMQContainer",
]

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.modules.mongodb import MongoDBContainer
from testcontainers.modules.mysql import MySQLContainer
from testcontainers.modules.postgres import PostgreSQLContainer
from testcontainers.modules.mariadb import MariaDBContainer
from testcontainers.modules.redis import RedisContainer
from testcontainers.modules.cassandra import CassandraContainer
from testcontainers.modules.neo4j import Neo4jContainer
from testcontainers.modules.influxdb import InfluxDBContainer
from testcontainers.modules.couchdb import CouchDBContainer
from testcontainers.modules.kafka import KafkaContainer
from testcontainers.modules.elasticsearch import ElasticsearchContainer
from testcontainers.modules.rabbitmq import RabbitMQContainer
