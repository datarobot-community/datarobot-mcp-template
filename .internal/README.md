# Internal Directory

This directory contains the **dr-mcp-server-lib** - a reusable library for building MCP servers with DataRobot integration.

## What's Inside

### `dr-mcp-server-lib/`

A standalone, reusable Python library that provides:
- Core MCP server implementation using FastMCP
- Pre-built DataRobot tools (data, projects, models, training, deployments, predictions)
- Configuration and credentials management
- Dynamic tool registration
- OpenTelemetry integration
- Memory management
- Extensible architecture for custom implementations

## Purpose

This library was extracted from the main application to:
1. **Enable Reuse**: Other projects can depend on this library instead of copying code
2. **Separate Concerns**: Core functionality is separate from application-specific code
3. **Independent Versioning**: Library can be versioned and released independently
4. **Better Testing**: Library can be tested in isolation
5. **Easier Maintenance**: Changes to core functionality happen in one place

## Using This Library

```bash
# Once published to PyPI
pip install dr-mcp-server-lib

# Or from source (for development)
pip install -e .internal/dr-mcp-server-lib/
```

Then use it:

```python
from base import create_mcp_server

server = create_mcp_server()
server.run()
```

## Development

### Install Dependencies

```bash
cd dr-mcp-server-lib
task install
```

### Run Tests

```bash
task test
```

### Build Package

```bash
task build
```



