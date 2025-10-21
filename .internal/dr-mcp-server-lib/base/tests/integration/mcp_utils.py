# Copyright 2025 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import contextlib
import os
from pathlib import Path
from typing import AsyncGenerator, Optional

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Try to load from script directory first, then fall back to root
_script_dir = Path(__file__).resolve().parent
_script_env = _script_dir / ".env"
_project_dir = _script_dir.parent.parent
_root_dir = _project_dir.parent
_root_env = _root_dir / ".env"

# Try script directory first, then root
if _script_env.exists():
    print(f"Loading .env from script directory: {_script_env}")
    load_dotenv(dotenv_path=_script_env, verbose=True, override=True)
else:
    print(f"Loading .env from root directory: {_root_env}")
    load_dotenv(dotenv_path=_root_env, verbose=True, override=True)


def integration_test_mcp_server_params() -> StdioServerParameters:
    env = {
        "DATAROBOT_API_TOKEN": os.environ.get("DATAROBOT_API_TOKEN") or "test-token",
        "DATAROBOT_ENDPOINT": os.environ.get("DATAROBOT_ENDPOINT")
        or "https://test.datarobot.com/api/v2",
        "MCP_SERVER_LOG_LEVEL": os.environ.get("MCP_SERVER_LOG_LEVEL") or "WARNING",
        "APP_LOG_LEVEL": os.environ.get("APP_LOG_LEVEL") or "WARNING",
        "OTEL_ENABLED": os.environ.get("OTEL_ENABLED") or "false",
        "MCP_SERVER_REGISTER_DYNAMIC_TOOLS_ON_STARTUP": os.environ.get(
            "MCP_SERVER_REGISTER_DYNAMIC_TOOLS_ON_STARTUP"
        )
        or "false",
    }

    server_script = str(_script_dir / "integration_mcp_server.py")

    return StdioServerParameters(
        command="uv",
        args=["run", server_script],
        env={
            "PYTHONPATH": str(_project_dir),  # Add project root to Python path
            "MCP_SERVER_NAME": "integration",
            "MCP_SERVER_PORT": "8081",
            **env,
        },
    )


@contextlib.asynccontextmanager
async def integration_test_mcp_session(
    server_params: Optional[StdioServerParameters] = None,
) -> AsyncGenerator[ClientSession, None]:
    """
    Create and connect a client for the MCP server as a context manager.

    Args:
        server_params: Parameters for configuring the server connection

    Yields:
        ClientSession: Connected MCP client session

    Raises:
        ConnectionError: If session initialization fails
        TimeoutError: If session initialization exceeds timeout
    """
    server_params = server_params or integration_test_mcp_server_params()

    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await asyncio.wait_for(session.initialize(), timeout=5)
                yield session

    except asyncio.TimeoutError:
        raise TimeoutError("Session initialization timed out after 5 seconds")
