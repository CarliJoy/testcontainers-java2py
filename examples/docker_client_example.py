#!/usr/bin/env python3
"""
Example demonstrating the Docker Client wrapper usage.

This script shows how to use the DockerClientFactory to create and use Docker clients.
"""

from testcontainers.core.docker_client import DockerClientFactory


def main():
    """Demonstrate Docker client usage."""
    print("Testcontainers Docker Client Example")
    print("=" * 50)
    
    # Get the singleton factory instance
    factory = DockerClientFactory.instance()
    
    # Check if Docker is available
    print("\n1. Checking Docker availability...")
    if not factory.is_docker_available():
        print("   ❌ Docker is not available!")
        return
    print("   ✅ Docker is available!")
    
    # Get a Docker client
    print("\n2. Getting Docker client...")
    client = factory.client()
    print(f"   ✅ Client created: {type(client).__name__}")
    
    # Get Docker info
    print("\n3. Docker Information:")
    print(f"   Docker Host IP: {factory.docker_host_ip_address()}")
    print(f"   API Version: {factory.get_active_api_version()}")
    
    # Get marker labels
    print("\n4. Testcontainers Marker Labels:")
    labels = DockerClientFactory.marker_labels()
    for key, value in labels.items():
        print(f"   {key}: {value}")
    
    # List running containers
    print("\n5. Running Containers:")
    try:
        containers = client.containers.list()
        if containers:
            for container in containers:
                print(f"   - {container.name} ({container.short_id})")
        else:
            print("   No containers running")
    except Exception as e:
        print(f"   Error listing containers: {e}")
    
    # Demonstrate lazy client
    print("\n6. Lazy Client Example:")
    lazy_client = DockerClientFactory.lazy_client()
    print(f"   Created lazy client: {lazy_client}")
    print("   (Client will be initialized on first use)")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
