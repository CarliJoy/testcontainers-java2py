"""
Example demonstrating GenericContainer usage.

This example shows how to use the converted testcontainers-python library
to run Docker containers in tests.
"""

from testcontainers.core import GenericContainer, BindMode
from testcontainers.waiting import LogMessageWaitStrategy, HostPortWaitStrategy
from testcontainers.images import PullPolicy
from datetime import timedelta


def example_basic_container():
    """Basic container usage with context manager."""
    print("=== Basic Container Example ===")
    
    # Simple container with auto port mapping
    with GenericContainer("nginx:latest") as container:
        container.with_exposed_ports(80)
        
        port = container.get_exposed_port(80)
        print(f"Nginx running at http://localhost:{port}")
        print(f"Container ID: {container.get_container_id()}")
        print(f"Container is running: {container.is_running()}")
    
    print("Container automatically stopped and removed\n")


def example_database_container():
    """Database container with environment variables."""
    print("=== Database Container Example ===")
    
    with GenericContainer("postgres:13") as container:
        # Configure with fluent API
        (container
            .with_exposed_ports(5432)
            .with_env("POSTGRES_PASSWORD", "testpass")
            .with_env("POSTGRES_USER", "testuser")
            .with_env("POSTGRES_DB", "testdb"))
        
        port = container.get_exposed_port(5432)
        print(f"PostgreSQL running at localhost:{port}")
        print(f"Connection string: postgresql://testuser:testpass@localhost:{port}/testdb")
        
        # Execute command in container
        result = container.exec(["psql", "-U", "testuser", "-c", "SELECT version();"])
        print(f"Exec result: {result.exit_code}")
    
    print("Database container cleaned up\n")


def example_custom_wait_strategy():
    """Container with custom wait strategy."""
    print("=== Custom Wait Strategy Example ===")
    
    container = GenericContainer("nginx:latest")
    container.with_exposed_ports(80)
    
    # Wait for log message
    wait_strategy = (
        LogMessageWaitStrategy()
        .with_regex(".*start worker process.*")
        .with_startup_timeout(timedelta(seconds=30))
    )
    container.waiting_for(wait_strategy)
    
    container.start()
    print(f"Nginx started and ready at port {container.get_exposed_port(80)}")
    
    container.stop()
    container.remove()
    print("Container cleaned up\n")


def example_volume_mounting():
    """Container with volume mounting."""
    print("=== Volume Mounting Example ===")
    
    import tempfile
    import os
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello from host!")
        
        with GenericContainer("alpine:latest") as container:
            (container
                .with_volume_mapping(tmpdir, "/data", BindMode.READ_ONLY)
                .with_command(["cat", "/data/test.txt"]))
            
            # Get logs to see the output
            stdout, stderr = container.get_logs()
            print(f"Container output: {stdout.decode('utf-8')}")
    
    print("Volume example complete\n")


def example_advanced_configuration():
    """Container with advanced configuration."""
    print("=== Advanced Configuration Example ===")
    
    with GenericContainer("redis:alpine") as container:
        (container
            .with_exposed_ports(6379)
            .with_name("test-redis")
            .with_labels(app="testapp", env="test")
            .with_command(["redis-server", "--appendonly", "yes"])
            .with_working_directory("/data"))
        
        port = container.get_exposed_port(6379)
        print(f"Redis running at localhost:{port}")
        print(f"Container name: {container._name}")
        print(f"Labels: {container._labels}")
    
    print("Advanced configuration example complete\n")


def example_image_pull_policy():
    """Container with custom image pull policy."""
    print("=== Image Pull Policy Example ===")
    
    from testcontainers.images import RemoteDockerImage
    
    # Create image with always-pull policy
    image = RemoteDockerImage("nginx:latest")
    image = image.with_pull_policy(PullPolicy.always_pull())
    
    with GenericContainer(image) as container:
        container.with_exposed_ports(80)
        
        port = container.get_exposed_port(80)
        print(f"Nginx (always pulled) at localhost:{port}")
    
    print("Image pull policy example complete\n")


def main():
    """Run all examples."""
    print("="*60)
    print("Testcontainers-Python Examples")
    print("="*60)
    print()
    
    try:
        example_basic_container()
        example_database_container()
        example_custom_wait_strategy()
        example_volume_mounting()
        example_advanced_configuration()
        example_image_pull_policy()
        
        print("="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure Docker is running and accessible.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
