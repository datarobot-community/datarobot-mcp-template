<p align="center">
  <a href="https://github.com/datarobot/recipe-fastmcp-template">
    <img src="./img/datarobot-logo.avif" width="600px" alt="DataRobot Logo"/>
  </a>
</p>
<p align="center">
    <span style="font-size: 1.5em; font-weight: bold; display: block;">FastMCP Server Template for DataRobot</span>
</p>

<p align="center">
  <a href="https://datarobot.com">Homepage</a>
  ·
  <a href="https://docs.datarobot.com">Documentation</a>
  ·
  <a href="https://modelcontextprotocol.io/">MCP Protocol</a>
  ·
  <a href="https://docs.datarobot.com/en/docs/get-started/troubleshooting/general-help.html">Support</a>
</p>

<p align="center">
  <a href="./LICENSE.txt">
    <img src="https://img.shields.io/github/license/datarobot/recipe-fastmcp-template" alt="License">
  </a>
  <a href="https://github.com/jlowin/fastmcp">
    <img src="https://img.shields.io/badge/FastMCP-2.12.2+-blue" alt="FastMCP">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python">
  </a>
</p>

This repository provides a production-ready template for building [FastMCP](https://github.com/jlowin/fastmcp) servers with DataRobot integration.
Once configured, the template results in a complete framework for creating MCP Servers to be used by agents for calling tools, prompts, and resources.
It can then be deployed as a DataRobot Custom Model Application, enabling seamless integration with AI assistants like Cursor, Claude Desktop, and other MCP-compatible clients.

The template includes pre-built tools for common DataRobot operations, a structured approach for adding custom tools, automated deployment infrastructure, and production-ready features like OpenTelemetry tracing and dynamic tool registration.

---

# FastMCP template navigation

- [Prerequisites](#prerequisites)
- [Getting started](#getting-started)
- [Deployment](#deployment)
- [Next steps](#next-steps)
- [Advanced options](#advanced-options)
- [Get help](#get-help)
- [Contributing](#contributing)
- [Additional resources](#additional-resources)
- [License](#license)

# Prerequisites

Ensure you have the following prerequisites installed:

- [**Python**](https://www.python.org/downloads/): A programming language (v3.11 or higher)
  
  ```bash
  pyenv install 3.11
  ```

- [**git**](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git): A version control system (v2.30.0 or higher)

  ```bash
  brew install git # macOS
  ```

- [**uv**](https://docs.astral.sh/uv/getting-started/installation/): A Python package manager (v0.6.10 or higher)

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- [**Task**](https://taskfile.dev/installation/): A task runner for development workflows (v3.43.3 or higher)

  ```bash
  brew install go-task/tap/go-task # macOS
  ```

- [**Pulumi**](https://www.pulumi.com/docs/iac/download-install/): An Infrastructure as Code tool (v3.163.0 or higher)

  ```bash
  brew install pulumi # macOS
  ```

- [**DataRobot Account**](https://app.datarobot.com/): Valid API credentials with appropriate permissions

## Optional

- [**Docker**](https://docs.docker.com/engine/install/): For containerized deployment
- [**AWS Credentials**](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html): If using AWS-related features (S3 predictions or memory.)
- [**Node.js**](https://nodejs.org/en/download/): Required for Claude Desktop MCP client setup

# Getting started

## Clone the repository

```bash
git clone https://github.com/datarobot/recipe-fastmcp-template.git
cd recipe-fastmcp-template
```

## Install dependencies

> **Note:** This installs dependencies for both the MCP application and infrastructure components.

```bash
task install
```

## Configure environment variables

Create a `.env` file in the `dr_mcp/` directory:

```bash
cd dr_mcp
vim .env # or your preferred editor
```

Copy and paste the following into the `.env` file:

```bash
# Required
DATAROBOT_API_TOKEN=[YOUR_DATAROBOT_API_KEY]
DATAROBOT_ENDPOINT=[YOUR_DATAROBOT_ENDPOINT]

# Optional - Server configuration
# MCP_SERVER_NAME=datarobot-mcp-server
# MCP_SERVER_PORT=8080
# MCP_SERVER_LOG_LEVEL=WARNING
# APP_LOG_LEVEL=INFO

# Optional - Dynamic tool registration
# MCP_SERVER_REGISTER_DYNAMIC_TOOLS_ON_STARTUP=false

# Optional - AWS credentials (for batch predictions and memory)
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# AWS_PREDICTIONS_S3_BUCKET=your_s3_bucket
```

### Add API credentials

Open the DataRobot UI to locate and copy your DataRobot API key and endpoint to your environment variables in `.env`.

> **Note**: For full details, see the [DataRobot API keys documentation](https://docs.datarobot.com/en/docs/get-started/acct-mgmt/acct-settings/api-key-mgmt.html).

1. Log in to your DataRobot account.
2. Click the user icon in the top right of the UI and select **API keys and tools**.

  <img src="./img/api-keys-tools.png" width="250" />

3. Copy your DataRobot API endpoint and paste it into the `.env` file in place of `[YOUR_DATAROBOT_ENDPOINT]`.

  <img src="./img/api-endpoint.png" width="400" />

4. Copy your DataRobot API key and paste it into the `.env` file in place of `[YOUR_DATAROBOT_API_KEY]`.

  <img src="./img/api-key.png" width="400" />

## Run locally

Start the server locally using the `task dev` command:

```bash
task dev
```

The server will start on `http://localhost:8080` with the MCP endpoint at `http://localhost:8080/mcp/`.
Once the FastMCP logo appears, the server is running properly.

<img src="./img/fastmcp-logo.png" width="300" />

> **Note**: When finished, press `Ctrl+C` to stop the server.

From here, you can perform some optional interactive testing on the local server using the steps in the next section. If you would like to skip straight to deploying a server, proceed to [Deployment](#deployment).

### Test your tools interactively (optional)

Once the server is running, you can immediately test your tools with an AI agent using the interactive testing mode:

```bash
task mcp:test-interactive
```

This command will:
- Start the MCP server (if not already running locally)
- Start a local AI agent connected to your MCP server
- Provide an interactive chat interface to test your tools
- Show real-time debug output of MCP server operations
- Allow you to test tool implementations end-to-end prior to deployment

The interactive mode displays detailed logs showing:
- Tool registration and discovery
- Request processing and responses
- Error handling and debugging information
- Agent decision-making process

<img src="./img/interactive-testing-mode.png" width="600" alt="Interactive Testing Mode showing AI agent connected to MCP server with debug output" />

> **Note**: The interactive testing requires an internet connection for the LLM, but all tool execution happens locally through your MCP server.

### Error handling and debugging

When developing tools, you'll encounter errors that need quick resolution. The MCP server provides detailed error information to help you iterate rapidly. The `test-interactive` command displays all of these in one place for you to see as you are testing the tools:

- **Server logs** show real-time error details, including stack traces
- **Tool execution errors** are captured and displayed with context
- **Validation errors** highlight parameter issues immediately
- **Connection errors** provide clear diagnostic information

<img src="./img/mcp_error.png" width="600" alt="MCP server error display showing formatted error messages and stack traces" />

Common debugging steps:
1. Check server logs for detailed error messages
2. Verify tool parameters match expected types
3. Ensure DataRobot API credentials are valid
4. Test individual tool functions in isolation
5. Use the interactive mode to reproduce errors with real agent calls

# Deployment

Now that the local test passed, you can deploy the server to DataRobot.

**What gets deployed**

After deployment is successful, it creates the following resources:

- **Execution Environment**: Docker-based Python 3.12 environment (or uses existing)
- **Custom Model**: MCP server packaged as an unstructured custom model
- **Registered Model**: Versioned model registration
- **Prediction Environment**: DataRobot Serverless platform
- **Deployment**: Active deployment with direct access endpoints

## Obtain a Pulumi access token

The template uses Pulumi Infrastructure as Code for deployment.
During the deploy process, you will be prompted to provide a Pulumi access token.
First, navigate to the [Pulumi website](https://app.pulumi.com/) and create an account or log in with your existing account.

You can generate a new token by accessing the Pulumi [Personal access tokens](https://app.pulumi.com/user/settings/tokens?filter=all) page and clicking **Create token**.
When the token is created, copy the token and paste it into the `task` process when prompted.

For more details, see the [Pulumi documentation](https://www.pulumi.com/docs/reference/cloud-rest-api/personal-access-tokens/).

## Deploy to DataRobot

1. Copy the `.env` file from the `dr_mcp` directory to the root directory:

```bash
cd .. # Previous steps left off in the dr_mcp directory
cp dr_mcp/.env .env
```

1. Deploy to DataRobot using Pulumi:

> **Note**: During this process, you will be prompted to provide a new stack name and your Pulumi access token.
> If prompted to perform an update, select "yes". Deployment can take several minutes to complete.

```bash

# Optional: Use existing execution environment
# export DATAROBOT_DEFAULT_EXECUTION_ENVIRONMENT=your_ee_id

task deploy
```

When the deployment is complete, the process displays the MCP server details:

<img src="./img/deploy-success.png" width="600" />

### Check deployment status

To check the overall deployment status:

```bash
cd infra && uv run pulumi stack
```

<img src="./img/mcp-status.png" width="600" />

### Destroy the deployment

When you are finished with the MCP server, you can destroy the deployment:

```bash
task destroy
```

## Connect to the deployed MCP server

Use the `MCP_SERVER_MCP_ENDPOINT` URL (shown in the **outputs** section in the screenshot above) to connect your MCP clients to the deployed server.

# Next steps

- [Configure your MCP client](/docs/mcp_client_setup.md) for instructions on connecting Cursor, VSCode, or Claude Desktop.
- [Develop custom tools](/docs/custom_tools.md) for instructions on adding custom tools to the server.
- See [MCP server architecture](/docs/mcp_server_architecture.md) for a detailed overview of the server architecture.
- [Advanced options](#advanced-options) for debugging, testing, and further customization.
- Read more about [dynamic tool registration](/docs/dynamic_tool_registration.md) for instructions on automatically registering tools with the server.

# Advanced options

## Runtime Parameters

Customize deployment parameters in `infra/infra/recipe.py`:

```python
MCP_RECIPE_RUNTIME_PARAMETERS = [
    pulumi_datarobot.CustomModelRuntimeParameterValueArgs(
        key="recipe_name",
        type="string",
        value=os.getenv("RECIPE_NAME", "default-recipe"),
    ),
    # Add your custom runtime parameters here
]
```

These parameters will be available as environment variables in the deployed server.

## Debugging

### Check logs

**Server logs** (local development):

- Logs print to console where you ran `task dev`
- Control verbosity with `MCP_SERVER_LOG_LEVEL` and `APP_LOG_LEVEL`

**MCP Client logs**:

- **Cursor**: View "MCP Logs" in the Output panel (View → Output → MCP Logs)
- **Claude Desktop**: Check `~/Library/Logs/Claude/mcp*.log`
- **VSCode**: Check the Output panel for MCP-related logs

### Common issues

<details>
<summary>Server won't start - "Address already in use"</summary>

Another process is using port 8080. Either kill that process or change the port:

```bash
cd dr_mcp
export MCP_SERVER_PORT=8081
task dev
```

</details>

<details>
<summary>Client can't connect - "Connection refused"</summary>

1. Verify server is running: `curl http://localhost:8080/health`
2. Check firewall settings
3. Verify the URL in your client config matches the server

</details>

<details>
<summary>Tools not showing up in client</summary>

1. Check server logs for tool registration errors
2. Verify your tools have proper docstrings and type hints
3. Restart the MCP client after server changes

</details>

# Get help

If you encounter issues or have questions:

- **Check Documentation**: Review the guides in `/docs/`
- **FastMCP Documentation**: [GitHub Repository](https://github.com/jlowin/fastmcp)
- **MCP Protocol**: [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- **DataRobot Support**: [Contact Support](https://docs.datarobot.com/en/docs/get-started/troubleshooting/general-help.html)
- **Open an Issue**: [GitHub Issues](https://github.com/datarobot/recipe-fastmcp-template/issues)
- **Security Issues**: Email oss-community-management@datarobot.com

# Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## Quick contribution guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following our code standards
4. Run tests: `cd dr_mcp && task test`
5. Run linters: `cd dr_mcp && task lint`
6. Commit with proper license headers
7. Push and create a pull request

## Code standards

- All source and test files must include the Apache 2.0 license header
- Imports must be at the top of files (never inside functions)
- Follow RESTful principles for API endpoints
- Make minimal, focused changes - only modify files necessary for your feature
- Use type hints and comprehensive docstrings
- Write tests for new functionality

# Additional resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [DataRobot API Documentation](https://docs.datarobot.com/)
- [DataRobot Python Client](https://datarobot-public-api-client.readthedocs-hosted.com/)
- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

# License

This project is licensed under the Apache License 2.0 - see [LICENSE](./LICENSE) for details.

Copyright 2025 DataRobot, Inc.

---

<p align="center">
  <strong>Built with ❤️ by DataRobot</strong>
</p>
