# ImageNameSubstitutor - Explained

## What is ImageNameSubstitutor?

**ImageNameSubstitutor** is a mechanism in Testcontainers that allows automatic transformation of Docker image names before they are used. This is a powerful feature for enterprise environments and CI/CD pipelines.

## Why Does It Exist?

### Primary Use Cases

1. **Private Registry Mirroring**: Redirect images from Docker Hub to a private registry to:
   - Avoid Docker Hub rate limiting (100 pulls per 6 hours for anonymous users)
   - Comply with corporate policies requiring all images to come from approved registries
   - Improve reliability by controlling your own image availability

2. **Image Name Transformation**: Apply complex rules for image name substitution based on:
   - Developer location or identity
   - Environment (dev, test, production)
   - Security policies

3. **Audit and Compliance**: Log all images used during testing for security auditing

4. **Testing with Forks**: Substitute public images with forked/patched versions

## How It Works

### Architecture

```
Original Image Name → ImageNameSubstitutor → Modified Image Name → Docker Pull
     "postgres:13"   →    [Substitution]    → "registry.corp/postgres:13"
```

### Implementation Pattern

The Java implementation uses:

1. **Abstract Base Class**: `ImageNameSubstitutor` implements `Function<DockerImageName, DockerImageName>`
2. **Singleton Pattern**: One global instance via `ImageNameSubstitutor.instance()`
3. **Chain of Responsibility**: Multiple substitutors can be chained
4. **Service Loader Pattern**: Implementations can be discovered automatically
5. **Configuration-based**: Can be configured via properties files or environment variables

## Built-in Implementations

### 1. DefaultImageNameSubstitutor (Composite)

Chains together:
- **ConfigurationFileImageNameSubstitutor**: Looks up specific image replacements in config
- **PrefixingImageNameSubstitutor**: Adds a prefix to Docker Hub images

### 2. PrefixingImageNameSubstitutor

The most common implementation - adds a registry prefix to Docker Hub images.

**Configuration:**
```properties
# In testcontainers.properties or via environment variable
hub.image.name.prefix=registry.mycompany.com/mirror/
```

**Example:**
```
Input:  mysql:8.0.36
Output: registry.mycompany.com/mirror/mysql:8.0.36

Input:  postgres:13
Output: registry.mycompany.com/mirror/postgres:13

Input:  myregistry.com/custom:1.0  (already has registry)
Output: myregistry.com/custom:1.0  (unchanged)
```

**Rules:**
- Only applies to Docker Hub images (no registry specified)
- Does NOT apply if image explicitly specifies `docker.io` or `registry.hub.docker.com`
- Prefix can include both registry and repository path

### 3. ConfigurationFileImageNameSubstitutor

Maps specific images to replacements via configuration.

**Configuration:**
```properties
# In testcontainers.properties
postgres.image=registry.mycompany.com/custom-postgres:13
mysql.image=registry.mycompany.com/custom-mysql:8.0
```

**Note:** This approach is deprecated and discouraged. Use custom substitutors instead.

### 4. NoopImageNameSubstitutor

Returns the original image name unchanged. Used for testing or explicit opt-out.

## Configuration Methods

### 1. Via Configuration File

Create `testcontainers.properties` in:
- Test resources: `src/test/resources/testcontainers.properties`
- User home: `~/.testcontainers.properties`
- Classpath root

```properties
# Use a prefix
hub.image.name.prefix=registry.mycompany.com/mirror/

# Or use a custom substitutor
image.substitutor=com.mycompany.MyCustomSubstitutor
```

### 2. Via Environment Variable

```bash
export TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX=registry.mycompany.com/mirror/
# Or
export TESTCONTAINERS_IMAGE_SUBSTITUTOR=com.mycompany.MyCustomSubstitutor
```

### 3. Via ServiceLoader

Create `META-INF/services/org.testcontainers.utility.ImageNameSubstitutor`:
```
com.mycompany.MyCustomSubstitutor
```

## Custom Implementation Example

```java
package com.mycompany.testcontainers;

import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.ImageNameSubstitutor;

public class MyCustomSubstitutor extends ImageNameSubstitutor {
    
    @Override
    public DockerImageName apply(DockerImageName original) {
        // Example: Always use specific versions instead of latest
        if (original.getVersionPart().equals("latest")) {
            String repo = original.getRepository();
            if (repo.equals("postgres")) {
                return DockerImageName.parse("postgres:13.0");
            }
            if (repo.equals("mysql")) {
                return DockerImageName.parse("mysql:8.0.36");
            }
        }
        
        // Example: Use private registry
        if (original.getRegistry().isEmpty()) {
            return DockerImageName.parse(
                "registry.mycompany.com/" + original.getUnversionedPart() + 
                ":" + original.getVersionPart()
            );
        }
        
        return original;
    }
    
    @Override
    protected String getDescription() {
        return "MyCompany custom image substitutor";
    }
}
```

## Features in Detail

### Chaining

Multiple substitutors can be chained:
1. Default substitutor always runs first
2. Custom substitutor runs second
3. Each sees the output of the previous one

### Logging

The framework automatically logs:
- Which substitutor is being used
- When an image name is substituted
- The original and replacement names

### Thread Safety

The singleton instance is created with synchronized initialization to ensure thread safety.

## Python Implementation Considerations

When implementing this for testcontainers-python, consider:

### Simplifications

1. **No ServiceLoader**: Python doesn't have Java's ServiceLoader
   - Use entry points or explicit registration
   - Or configuration-based discovery only

2. **Simpler Configuration**: 
   - Use environment variables
   - Use Python config files (YAML, TOML, or .env)
   - Or programmatic configuration

3. **Protocol-based Design**:
   - Use `Protocol` for the interface
   - Simple callable: `Callable[[str], str]` or custom protocol

### Recommended Python API

```python
from typing import Protocol

class ImageNameSubstitutor(Protocol):
    """Transform Docker image names before use."""
    
    def substitute(self, image_name: str) -> str:
        """
        Transform an image name.
        
        Args:
            image_name: Original image name
            
        Returns:
            Transformed image name
        """
        ...
    
    def description(self) -> str:
        """Human-readable description of this substitutor."""
        ...

# Usage in GenericContainer
class GenericContainer:
    def __init__(self, image: str):
        substitutor = ImageNameSubstitutor.get_instance()
        self._image = substitutor.substitute(image)
```

### Configuration Options

```python
# Environment variable
export TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX=registry.mycompany.com/mirror/

# Or in pyproject.toml
[tool.testcontainers]
hub_image_name_prefix = "registry.mycompany.com/mirror/"
image_substitutor = "mymodule.MyCustomSubstitutor"

# Or programmatic
from testcontainers import configure_image_substitutor

configure_image_substitutor(MyCustomSubstitutor())
```

## When to Use

### Use ImageNameSubstitutor when:

✅ You need to use a private registry instead of Docker Hub
✅ You want to avoid Docker Hub rate limits
✅ You need different image sources per environment (dev/CI/prod)
✅ Corporate policy requires all images from approved registries
✅ You want to audit all images used in tests
✅ You need to substitute specific images with patched versions

### Don't use when:

❌ You only use a few images (manually specify registry instead)
❌ Everyone has direct Docker Hub access without rate limits
❌ You don't need any image name transformation

## Summary

**ImageNameSubstitutor** is a flexible, enterprise-friendly mechanism for transforming Docker image names in Testcontainers. It provides:

- **Transparency**: Tests don't need to know about registry details
- **Flexibility**: Different configurations per environment
- **Control**: Central management of image sources
- **Auditability**: Logging of all substitutions

For Python implementation, we should adapt the pattern to Python idioms while maintaining the core functionality and flexibility.

## References

- Java Source: `core/src/main/java/org/testcontainers/utility/ImageNameSubstitutor.java`
- Documentation: `docs/features/image_name_substitution.md`
- Related: `DockerImageName`, `RemoteDockerImage`
