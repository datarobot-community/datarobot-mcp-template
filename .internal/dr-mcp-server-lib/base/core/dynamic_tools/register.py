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
import logging
from typing import Any, Callable, Coroutine, Dict, Literal, Optional, Set
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientTimeout
from aiohttp_retry import ExponentialRetry, RetryClient
from fastmcp.tools.tool import Tool, ToolResult
from pydantic import BaseModel, Field

from base.core.config import get_config
from base.core.dynamic_tools.schema import create_input_schema_pydantic_model
from base.core.mcp_instance import register_tools
from base.core.utils import format_response_as_tool_result

logger = logging.getLogger(__name__)


# HTTP request retry configuration
REQUEST_RETRY_SLEEP = 0.1
REQUEST_MAX_RETRY = 5
REQUEST_RETRYABLE_STATUS_CODES = {429, 570, 502, 503, 504}

# HTTP connection timeouts in seconds
REQUEST_CONNECT_TIMEOUT = 30
REQUEST_TOTAL_TIMEOUT = 600


class ExternalToolRegistrationConfig(BaseModel):
    """Configuration for registering an external HTTP API endpoint as an MCP tool.

    This specification defines how to register a generic external HTTP API as a tool
    that can be called by LLM agents through the MCP (Model Context Protocol) server.
    The tool acts as a bridge between the LLM and any external HTTP API, automatically
    handling request construction, retry logic, and response formatting.
    """

    name: str = Field(..., description="Name of the tool.")
    title: Optional[str] = Field(None, description="Title for LLMs and users.")
    description: Optional[str] = Field(
        None, description="Description for LLMs and users."
    )
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"] = Field(
        ..., description="HTTP method to use."
    )
    base_url: str = Field(..., description="Base URL of the external API.")
    endpoint: str = Field(
        ...,
        description="URL endpoint/route for the external API, may include path params.",
    )
    headers: Optional[Dict[str, str]] = Field(
        None, description="Optional static headers to include in requests."
    )
    input_schema: Dict[str, Any] = Field(
        ..., description="Pydantic schema defining the tool's input schema."
    )
    tags: Optional[Set[str]] = Field(
        None, description="Optional tags for tool categorization and filtering."
    )


def _external_tool_callable_factory(
    spec: ExternalToolRegistrationConfig,
) -> Callable[[Any], Coroutine[Any, Any, ToolResult]]:
    """Dynamically creates an async callable that makes HTTP requests
    based on the given spec. This callable is the execution logic of the
    tool making the external API call.

    Args:
        spec: Configuration specifying how to make the HTTP request.

    Returns:
        An async callable that takes validated inputs and returns a ToolResult.
    """
    config = get_config()

    InputModel = create_input_schema_pydantic_model(
        input_schema=spec.input_schema,
        allow_empty=config.tool_registration_allow_empty_schema,
    )

    async def call_external_tool(inputs: InputModel) -> ToolResult:  # type: ignore[valid-type]
        request_input = inputs.model_dump()  # type: ignore[attr-defined]

        # Extract request parameters
        path_params = request_input.get("path_params", {})
        params = request_input.get("query_params")
        data = request_input.get("data")
        json = request_input.get("json")
        headers = spec.headers or {}

        # Build full URL with path params
        url = urljoin(spec.base_url, spec.endpoint.format(**path_params))

        # Configure timeouts
        client_timeout = ClientTimeout(
            total=REQUEST_TOTAL_TIMEOUT,
            connect=REQUEST_CONNECT_TIMEOUT,
        )

        # Configure retry strategy with exponential backoff
        retry_options = ExponentialRetry(
            attempts=REQUEST_MAX_RETRY,
            start_timeout=REQUEST_RETRY_SLEEP,
            statuses=REQUEST_RETRYABLE_STATUS_CODES,
            exceptions={
                aiohttp.ClientError,
                aiohttp.ServerTimeoutError,
                asyncio.TimeoutError,
            },
        )

        # Execute request with retry logic
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            retry_client = RetryClient(
                client_session=session,
                retry_options=retry_options,
                logger=logger,
            )

            async with retry_client.request(
                method=spec.method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
            ) as response:
                content = await response.read()

                return format_response_as_tool_result(
                    data=content,
                    content_type=response.content_type,
                    charset=response.charset or "utf-8",
                )

    return call_external_tool


async def register_external_tool(
    config: ExternalToolRegistrationConfig, **kwargs: Any
) -> Tool:
    """Create and register a generic HTTP tool in the MCP server.

    This function creates a dynamic tool that makes HTTP requests to external APIs
    and registers it with the MCP server for use by LLM agents.

    Args:
        config: ExternalToolRegistrationConfig object containing all tool parameters.
        **kwargs: Additional keyword arguments to pass to tools registration.

    Returns:
        The registered Tool instance with full MCP integration.

    Raises:
        ValueError: If required path parameters are missing from input_schema.
        aiohttp.ClientError: If the HTTP request fails during tool execution.

    Example:
        >>> config = ExternalToolRegistrationConfig(
        ...     name="get_user",
        ...     description="Fetch user by ID",
        ...     base_url="https://api.example.com/v1",
        ...     endpoint="users/{user_id}",
        ...     method="GET",
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "path_params": {
        ...                 "type": "object",
        ...                 "properties": {"user_id": {"type": "string"}},
        ...                 "required": ["user_id"]
        ...             }
        ...         }
        ...     },
        ...     tags={"example", "user"}
        ... )
        >>> tool = await register_external_tool(config=config)

    Note:
        The tool remains registered until explicitly removed or the server restarts.
    """
    external_tool_callable = _external_tool_callable_factory(config)

    registered_tool = await register_tools(
        fn=external_tool_callable,
        name=config.name,
        title=config.title,
        description=config.description,
        tags=config.tags,
        **kwargs,
    )

    return registered_tool
