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
    "MongoDBContainer",
    "RedisContainer",
]

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.modules.mongodb import MongoDBContainer
from testcontainers.modules.mysql import MySQLContainer
from testcontainers.modules.postgres import PostgreSQLContainer
from testcontainers.modules.redis import RedisContainer
