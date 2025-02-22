# Shared Resource Decorator

This package provides a simple decorator, `@shared_resource()`, which allows creation and sharing of resource instances between tests. Instead of repeatedly creating and then closing (or finalizing) the same resource in every test, a resource can be created once, shared across tests, and automatically finalized after all tests have finished.

## Installation

Install the package via pip:

```bash
pip install vedro-shared-resource
```

## Overview

In some testing scenarios, a resource is created and then closed or finalized separately in each test. For example:

```python
# Test 1
resource = create_resource()
defer(resource.close)
# do something with resource

# Test 2
resource = create_resource()
defer(resource.close)
# do something with resource
```

(Note: Here, the `defer` function registers a callback to be executed after the current test scenario finishes)

Repeatedly creating the resource can lead to longer test execution times and increased resource consumption. By defining a shared resource that is created only once and cached using `@shared_resource()`, tests can run faster while ensuring that:
- **Performance Improvement:** Expensive resource initialization is executed only once per unique set of arguments.
- **Consistency:** All tests that request the resource with the same parameters receive the same shared instance.
- **Resource Management:** The resource is finalized (closed) only once after all tests complete, reducing the risk of resource leaks.

## Usage

### 1. Creating a Shared Resource

To share a resource, wrap the resource-creation function with the `@shared_resource()` decorator. Within the function, use `defer_global` to register the resource’s finalization callback.

```python
from vedro_shared_resource import shared_resource
from vedro import defer_global

@shared_resource()
def create_shared_resource():
    resource = create_resource()
    defer_global(resource.close)
    return resource
```

(Note: While `defer` registers a callback for the current test scenario, `defer_global` registers a callback for the entire test suite)

### 2. Using the Shared Resource in Tests

When the decorated function is called in tests, the first call executes the function and caches its result. Subsequent calls return the cached resource immediately, avoiding redundant and expensive resource creation.

```python
# Test 1
resource = create_shared_resource()
# perform operations with resource

# Test 2
resource = create_shared_resource()
# perform operations with resource
```

## The `@shared_resource()` Decorator

The `@shared_resource()` decorator caches the result of the resource creation function:

- **First call:** The resource creation function is executed, and its result is stored in a cache.
- **Subsequent calls:** The cached resource is returned immediately, avoiding the expense of re-creating the resource.

If the function accepts arguments, they become part of the cache key, ensuring that each unique combination of arguments results in a separate cached resource.

### Parameters

- **max_instances (int):**  
  Specifies the maximum number of unique cached results for the function. This limit is applied per resource function. Once the cache reaches this size, the least-recently-used entry is evicted.

- **type_sensitive (bool):**  
  If set to `True`, arguments of different types (for example, `1` vs. `1.0`) are treated as distinct cache keys.

### Under the Hood

- For **synchronous functions**, the decorator leverages Python's built-in `functools.lru_cache`.
- For **asynchronous functions**, it utilizes `async_lru.alru_cache`.

## Use Cases

### Use Case 1: Sharing an Asynchronous Resource (HTTP Client)

An asynchronous HTTP client from the `httpx` library can be shared between tests. Although instantiating an `AsyncClient` might not be highly resource-intensive by itself, [the official httpx documentation](https://www.python-httpx.org/async/#opening-and-closing-clients) recommends reusing a single client instance to take full advantage of connection pooling. Instantiating multiple clients—especially inside a "hot loop"—can prevent efficient reuse of connections. Caching the client instance ensures that it is created only once and reused throughout the test suite, supporting optimal connection pooling.

```python
from vedro_shared_resource import shared_resource
from vedro import defer_global
from httpx import AsyncClient

@shared_resource()
async def async_client() -> AsyncClient:
    client = AsyncClient()
    await client.__aenter__()

    defer_global(client.aclose)

    return client
```

Usage in tests:

```python
client = await async_client()
response = await client.get("https://example.com")
```

### Use Case 2: Sharing a Synchronous Resource (Web Browser)

Sharing a Chromium browser instance while accepting parameters allows different configurations to be cached separately. The resource creation function uses keyword arguments as part of the cache key, meaning that launching the Chromium browser with specified parameters (e.g., `headless=False`) is performed only once per configuration. Because launching a browser repeatedly can significantly slow down tests, caching the launched browser instance improves performance and ensures consistency across tests.

```python
from vedro_shared_resource import shared_resource
from vedro import defer_global
from playwright.sync_api import sync_playwright, Browser

@shared_resource()
def chromium(**kwargs) -> Browser:
    playwright = sync_playwright().start()
    defer_global(playwright.stop)

    chromium = playwright.chromium.launch(**kwargs)
    defer_global(chromium.close)

    return chromium
```

Usage in tests:

```python
browser = chromium(headless=False)
page = browser.new_page()
page.goto("https://example.com")
```

## Caveats and Considerations

Introducing global variables and any kind of caching can sometimes lead to unexpected issues, such as shared state conflicts or challenges with test isolation. It is recommended to use resource caching only when resource creation is a true bottleneck and when sharing a resource does not compromise the reliability and correctness of tests.
