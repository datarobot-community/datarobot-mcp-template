# Testing

To run `pytest` (note: this will also show you which lines are not covered and fail if the total coverage is below 85%.)

```bash
uv sync --all-extras && uv run pytest
```

## This repo is made of 3 directories:

### Unit tests
Located in `/tests/unit/`, these tests focus on testing individual components in isolation:
- Test individual functions and classes
- Mock external dependencies (DataRobot SDK, HTTP requests, etc.)
- Fast execution and quick feedback
- Help identify issues in specific components

### Integration tests
Located in `/tests/integration/`, these tests verify component interactions:
- Test MCP server with DataRobot client
- Verify tool registration and execution
- Test end-to-end flows with external services
- Ensure components work together correctly
- Use `mcp_test_server.py` for running a test MCP server

#### Note

For Integration tests, you must create a `.env` file in the integration test directory or the root directory with the following variables if you are using a real dependencies and not the mocks:

```bash
DATAROBOT_API_TOKEN=your_api_token
DATAROBOT_ENDPOINT=your_datarobot_endpoint
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_SESSION_TOKEN=your_aws_session_token
# AWS_PREDICTIONS_S3_BUCKET=optional_your_aws_predictions_s3_bucket_optional
# AWS_PREDICTIONS_S3_PREFIX=optional_your_aws_predictions_s3_prefix_optional
# MCP_SERVER_PORT=8081
# MCP_SERVER_LOG_LEVEL=DEBUG
```

### ETE tests
Located in `/tests/ete/`, these tests simulate real-world production usage where:

1. A user provides a natural language prompt to an LLM
2. The LLM decides whether to call DataRobot tools via MCP
3. The MCP server executes real DataRobot API calls
4. The LLM processes tool results and provides a final response

`User Prompt` → `LLM Decision` → `MCP Tool Call` → `DataRobot API` → `Tool Result` → `LLM Response`

#### Note

For ETE tests, you must create a `.env` file in the ete test directory or the root directory with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=your_openai_api_base
OPENAI_API_DEPLOYMENT_ID=your_openai_api_deployment_id
OPENAI_API_VERSION=your_openai_api_version
SAVE_LLM_RESPONSES=true
# DR_MCP_SERVER_URL=http://localhost:8080/mcp
```
