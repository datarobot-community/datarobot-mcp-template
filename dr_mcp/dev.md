# MCP

DataRobot MCP Server Implementation.

## Prerequisites

- uv (Python package installer)
- DataRobot account and API credentials
- AWS credentials (if using AWS-related features)

## Setup

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a `.env` file in the root directory from `.env.sample` with the following variables:

```bash
DATAROBOT_API_TOKEN=your_api_token
DATAROBOT_ENDPOINT=your_datarobot_endpoint
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# AWS_SESSION_TOKEN=your_aws_session_token
# AWS_PREDICTIONS_S3_BUCKET=optional_your_aws_predictions_s3_bucket_optional
# AWS_PREDICTIONS_S3_PREFIX=optional_your_aws_predictions_s3_prefix_optional
# MCP_SERVER_NAME=optional_your_server_name_optional
# MCP_SERVER_PORT=optional_8080_optional
# MCP_SERVER_LOG_LEVEL=optional_DEBUG_optional
# MCP_SERVER_HOST=optional_127.0.0.1_optional
# MCP_SERVER_REGISTER_DYNAMIC_TOOLS_ON_STARTUP=optional_true_optional
# MCP_SERVER_TOOL_REGISTRATION_ALLOW_EMPTY_SCHEMA=optional_true_optional
# MCP_SERVER_TOOL_REGISTRATION_DUPLICATE_BEHAVIOR=optional_warn_optional
# APP_LOG_LEVEL=optional_DEBUG_optional
# OTEL_COLLECTOR_BASE_URL=optional_OTEL_URL_optional
# OTEL_ENABLED=optional_false_optional
# OTEL_ENTITY_ID=optional_ID_optional
# OTEL_ENABLED_HTTP_INSTRUMENTORS=optional_true_optional
```

## Running the Server

Create a virtual environment, install dependencies and run the main server locally:
```bash
task mcp:dev
```

Deploy into DataRobot:
```bash
task deploy
```

## Development

### MCP Client Setup

#### Cursor
Edit `~/.cursor/mcp.json`
```json
{
  "mcpServers": {
    "datarobot-mcp-server": {
      "url": "http://localhost:8080/mcp/"
    },
    "datarobot-mcp-server-remote": {
      "url": "https://app.datarobot.com/deployments/<deployment-id>/directAccess/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

#### VSCode

Edit `~/Library/Application Support/Code/User/mcp.json`

```json
    "mcp": {
        "servers": {
            "datarobot-mcp-server": {
                "url": "http://localhost:8080/mcp/",
                "type": "http"
            }
        }
    }
```

#### Claude Desktop

```bash
brew install node
```

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "datarobot-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://app.datarobot.com/deployments/<deployment-id>/directAccess/mcp/",
        "--header",
        "Authorization: ${AUTH_HEADER}",
        "--transport",
        "http"
      ],
      "env": {
        "AUTH_HEADER": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### OpenTelemetry Configuration
The server supports OpenTelemetry for distributed tracing.

#### Features
- Automatic HTTP client instrumentation (aiohttp, httpx, requests)
- Tool execution tracing with parameters and results
- Error tracking and status monitoring
- Custom attribute support

#### Optional Environment Variables
```bash
# OTEL URL (default: OTEL DATAROBOT_ENDPOINT)
OTEL_COLLECTOR_BASE_URL=https://otel-collector.example.com

# Enable/disable OpenTelemetry (default: true)
OTEL_ENABLED=true

# Entity ID for tracing
OTEL_ENTITY_ID=deployment-<id>

# Custom attributes as JSON (optional)
OTEL_ATTRIBUTES='{"deployment": "prod"}'

# Enable/disable HTTP instrumentors (default: false)
OTEL_ENABLED_HTTP_INSTRUMENTORS=false
```

### Dynamic Tool Registration
When enabled, the server will scan for deployments tagged as tools (tag: tool) and register each as a tool automatically. Please refer to the [dedicated guide on dynamic tool registration](docs/dynamic_tool_registration.md) to read more about this feature, supported workflows, and all the prerequisites.

```bash
# Enable/disable Dynamic Tool Registration on startup (default: false)
MCP_SERVER_REGISTER_DYNAMIC_TOOLS_ON_STARTUP=true
``` 

### Debugging
Check the the Output of the MCP Logs

### Sorting, linter and formatter
```bash
uv sync --all-extras && uv run ruff check --select I --fix && uv run ruff format
```

### Run tests
```bash
uv sync --all-extras && uv run pytest
```