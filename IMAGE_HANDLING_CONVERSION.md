# Image Handling Conversion Documentation

## Overview

This document describes the conversion of image handling functionality from Java to Python. Image handling manages Docker image pulling, caching, and pull policies.

## Files Converted

### Java Files

| Java File | Lines | Description |
|-----------|-------|-------------|
| ImagePullPolicy.java | 7 | Base interface |
| ImageData.java | 33 | Image metadata |
| AbstractImagePullPolicy.java | 48 | Base pull policy |
| AlwaysPullPolicy.java | 21 | Always pull policy |
| DefaultPullPolicy.java | 14 | Default pull policy |
| AgeBasedPullPolicy.java | 24 | Age-based pull policy |
| PullPolicy.java | 80 | Policy factory |
| RemoteDockerImage.java | 190 | Image pulling logic |
| **Total** | **~417** | |

### Python Output

| Python File | Lines | Description |
|-------------|-------|-------------|
| image_pull_policy.py | ~30 | Protocol interface |
| image_data.py | ~70 | Image metadata |
| policies.py | ~130 | All pull policy implementations |
| pull_policy.py | ~60 | Policy factory |
| remote_image.py | ~180 | Simplified image pulling |
| **Total** | **~470** | |

## Key Conversions

### 1. Interface → Protocol

**Java:**
```java
public interface ImagePullPolicy {
    boolean shouldPull(DockerImageName imageName);
}
```

**Python:**
```python
class ImagePullPolicy(Protocol):
    def should_pull(self, image_name: str) -> bool:
        ...
```

### 2. Image Data

**Java:**
```java
@Value
@Builder
public class ImageData {
    @NonNull
    Instant createdAt;
    
    static ImageData from(InspectImageResponse response) {
        // ...
    }
}
```

**Python:**
```python
@dataclass
class ImageData:
    created_at: datetime
    
    @classmethod
    def from_inspect_response(cls, inspect_response: dict) -> ImageData:
        # ...
```

### 3. Pull Policies

**Java - Multiple files:**
```java
public abstract class AbstractImagePullPolicy implements ImagePullPolicy {
    protected abstract boolean shouldPullCached(DockerImageName imageName, ImageData localImageData);
}

class AlwaysPullPolicy implements ImagePullPolicy { }
class DefaultPullPolicy extends AbstractImagePullPolicy { }
class AgeBasedPullPolicy extends AbstractImagePullPolicy { }
```

**Python - Single file:**
```python
class AbstractImagePullPolicy(ABC, ImagePullPolicy):
    @abstractmethod
    def _should_pull_cached(self, image_name: str, local_image_data: ImageData) -> bool:
        pass

class AlwaysPullPolicy(ImagePullPolicy):
    def should_pull(self, image_name: str) -> bool:
        return True

class DefaultPullPolicy(AbstractImagePullPolicy):
    def _should_pull_cached(self, image_name: str, local_image_data: ImageData) -> bool:
        return False
```

### 4. Remote Docker Image

**Java:**
```java
public class RemoteDockerImage extends LazyFuture<String> {
    private Future<DockerImageName> imageNameFuture;
    ImagePullPolicy imagePullPolicy = PullPolicy.defaultPolicy();
    
    @Override
    protected final String resolve() {
        // Complex pull logic with retry
        Awaitility.await()
            .pollInSameThread()
            .pollDelay(Duration.ZERO)
            .atMost(PULL_RETRY_TIME_LIMIT)
            .pollInterval(interval)
            .until(tryImagePullCommand(...));
    }
}
```

**Python:**
```python
class RemoteDockerImage:
    def __init__(self, image_name: str, pull_policy: Optional[ImagePullPolicy] = None):
        self._image_name = image_name
        self._pull_policy = pull_policy or PullPolicy.default_policy()
    
    def resolve(self, pull_timeout: timedelta = timedelta(seconds=300)) -> str:
        if not self._pull_policy.should_pull(self._image_name):
            return self._image_name
        
        # Simple retry logic with exponential backoff
        self._pull_image(timeout_seconds)
        return self._image_name
```

## Design Decisions

### 1. Simplified Image Pulling

**Java** uses complex frameworks:
- Awaitility for polling
- Guava Futures for lazy loading
- Custom poll intervals

**Python** uses simple retry logic:
```python
retry_delay = 0.05
while time.time() - start_time < timeout_seconds:
    try:
        self._docker_client.images.pull(repository, tag=tag)
        return
    except APIError:
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, max_retry_delay)
```

### 2. Removed LazyFuture Pattern

Java's `LazyFuture<String>` is replaced with simple lazy evaluation:
```python
def resolve(self) -> str:
    if self._resolved_image_name is not None:
        return self._resolved_image_name
    # ... perform resolution
    self._resolved_image_name = image_name
    return self._resolved_image_name
```

### 3. No Image Name Substitution

Java has `ImageNameSubstitutor` for complex name transformations. Python implementation is simplified - can be added later if needed.

### 4. Simplified Local Cache

Java has a complex `LocalImagesCache` singleton. Python uses a simple dict in `AbstractImagePullPolicy` for basic caching.

### 5. Direct docker-py Integration

Uses docker-py's built-in pull functionality instead of wrapping docker-java's callbacks:

```python
# Simple and direct
self._docker_client.images.pull(repository, tag=tag)
```

vs Java's callback pattern:
```java
pullImageCmd.exec(new TimeLimitedLoggedPullImageResultCallback(logger)).awaitCompletion()
```

## Features Implemented

✅ **ImagePullPolicy Protocol** - Interface for pull policies
✅ **ImageData** - Image metadata with creation time
✅ **AbstractImagePullPolicy** - Base with caching logic
✅ **AlwaysPullPolicy** - Always pull images
✅ **DefaultPullPolicy** - Pull if not cached
✅ **AgeBasedPullPolicy** - Pull if too old
✅ **PullPolicy Factory** - Convenience methods
✅ **RemoteDockerImage** - Image pulling with retry
✅ **Fluent API** - Method chaining
✅ **Full Type Hints** - Complete type annotations

## Features Simplified/Deferred

- ❌ ImageNameSubstitutor - Name transformation (can add later)
- ❌ LocalImagesCache singleton - Using simple dict
- ❌ Logged pull callbacks - Using docker-py's default
- ❌ Platform fallback (linux/amd64) - Can add if needed
- ❌ Configuration loading - Using simple defaults

## Testing

### Test Coverage

**21 new tests covering:**
- ImageData (4 tests)
  - From inspect response
  - From image dict
  - Empty/None handling
  
- AlwaysPullPolicy (1 test)
  - Always returns True
  
- DefaultPullPolicy (2 tests)
  - Pull when not cached
  - Don't pull when cached
  
- AgeBasedPullPolicy (2 tests)
  - Pull old images
  - Don't pull recent images
  
- PullPolicy Factory (3 tests)
  - Default policy
  - Always pull
  - Age-based
  
- RemoteDockerImage (9 tests)
  - Initialization
  - Fluent API
  - String representations
  - Resolve with/without pull
  - Caching
  - Name parsing

**Total: 68 tests passing (47 existing + 21 new)**

## Usage Examples

### Basic Image Pulling

```python
from testcontainers.images import RemoteDockerImage, PullPolicy

# Create image with default policy
image = RemoteDockerImage("nginx:latest")

# Resolve (pull if needed)
image_name = image.resolve()
```

### Custom Pull Policy

```python
from testcontainers.images import RemoteDockerImage, PullPolicy

# Always pull
image = RemoteDockerImage("nginx:latest")
image = image.with_pull_policy(PullPolicy.always_pull())
image_name = image.resolve()

# Age-based pull
from datetime import timedelta
image = RemoteDockerImage("postgres:13")
image = image.with_pull_policy(PullPolicy.age_based(timedelta(days=7)))
image_name = image.resolve()
```

### Direct Policy Usage

```python
from testcontainers.images import DefaultPullPolicy, AlwaysPullPolicy

# Check if should pull
policy = DefaultPullPolicy()
should_pull = policy.should_pull("nginx:latest")

# Always pull
policy = AlwaysPullPolicy()
should_pull = policy.should_pull("redis:alpine")  # Always True
```

## Integration with GenericContainer

Image handling will be used in GenericContainer:

```python
class GenericContainer:
    def __init__(self, image: str | RemoteDockerImage):
        if isinstance(image, str):
            self._image = RemoteDockerImage(image)
        else:
            self._image = image
    
    def start(self):
        # Resolve image before starting
        image_name = self._image.resolve()
        
        # Create and start container with resolved image
        self._container = self._docker_client.containers.create(image_name, ...)
        self._container.start()
```

## Next Steps

With image handling complete, we can now:

1. **Implement GenericContainer** - Main container class
2. **Add Network Support** - Container networking
3. **Add Volume Support** - Volume mounting
4. **Enhance Image Features** - Substitution, caching, etc. as needed

## Statistics

| Metric | Java | Python | Change |
|--------|------|--------|--------|
| Lines of Code | ~417 | ~470 | +13% |
| Files | 8 | 5 | -37% |
| Tests | 0 | 21 | New |
| Dependencies | Guava, Awaitility | docker-py only |

Python is slightly more verbose due to explicit type hints and docstrings, but code is simpler and more maintainable. Fewer files with better organization.
