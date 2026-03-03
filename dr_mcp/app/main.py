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
import errno
import logging
import os
import socket
import sys
from typing import Any

import requests
from datarobot.errors import ClientError
from datarobot_genai.drmcp import create_mcp_server, get_config

from app.core.server_lifecycle import ServerLifecycle
from app.core.user_config import get_user_config
from app.core.user_credentials import get_user_credentials

logger = logging.getLogger(__name__)

_CONNECTION_ERROR_MSG = "Could not reach DataRobot. Check your network connection and ensure VPN is connected, then try again."
_AUTH_ERROR_MSG = (
    "DataRobot API authentication failed. Your API token may be expired or invalid. "
    "Update DATAROBOT_API_TOKEN in your .env and try again."
)


def _get_server_port() -> int:
    """Return the MCP server port from datarobot_genai.drmcp config (env + default)."""
    return get_config().mcp_server_port


def _is_port_in_use(port: int, host: str = "0.0.0.0") -> bool:
    """Return True if the given host:port is already in use (EADDRINUSE only)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                logger.error("%s", _format_port_in_use_message(port))
                return True
            raise


def _format_port_in_use_message(port: int) -> str:
    """Return a user-friendly message and commands for port-in-use errors."""
    return (
        f"Port {port} is already in use. Another process (often a previous MCP server) is using it.\n\n"
        "To free the port:\n"
        "  1. See what is using it:\n"
        f"     lsof -i :{port}\n"
        "  2. Stop the process (use the PID from the output above):\n"
        "     kill <PID>\n"
        "     # or force kill:  kill -9 <PID>\n\n"
        "Alternatively, use a different port:\n"
        f"     export MCP_SERVER_PORT={port + 1}\n"
        "  then start the server again."
    )


def suppress_keyboard_interrupt_traceback(
    exc_type: type[BaseException] | None,
    exc_value: BaseException | None,
    exc_traceback: Any | None,
) -> None:
    """Suppress traceback for KeyboardInterrupt, exit cleanly for other exceptions."""
    if exc_type is KeyboardInterrupt:
        # Suppress KeyboardInterrupt traceback
        sys.exit(0)
    # Use default exception handler for other exceptions
    if exc_type is not None and exc_value is not None:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def handle_asyncio_exception(
    loop: asyncio.AbstractEventLoop, context: dict[str, Any]
) -> None:
    """Handle exceptions in asyncio tasks, suppressing KeyboardInterrupt tracebacks."""
    exception = context.get("exception")
    if isinstance(exception, KeyboardInterrupt):
        # Suppress KeyboardInterrupt tracebacks during shutdown
        return
    # User-friendly message for port-already-in-use (e.g. from uvicorn bind)
    if (
        isinstance(exception, OSError)
        and getattr(exception, "errno", None) == errno.EADDRINUSE
    ):
        port = _get_server_port()
        logger.error("%s", _format_port_in_use_message(port))
        sys.exit(1)
    # Let other exceptions be handled normally
    default_handler = loop.default_exception_handler
    if default_handler is not None:
        default_handler(context)


class CustomEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """Custom event loop policy that sets exception handler for KeyboardInterrupt."""

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        loop = super().new_event_loop()
        loop.set_exception_handler(handle_asyncio_exception)
        return loop


if __name__ == "__main__":
    # Suppress KeyboardInterrupt tracebacks globally
    sys.excepthook = suppress_keyboard_interrupt_traceback

    # Set custom event loop policy to handle KeyboardInterrupt in asyncio tasks
    # even when the loop is created inside server.run()
    asyncio.set_event_loop_policy(CustomEventLoopPolicy())

    # Get paths to user modules
    app_dir = os.path.dirname(__file__)

    # Check if port is already in use before starting (avoids noisy traceback)
    port = _get_server_port()
    if _is_port_in_use(port):
        sys.exit(1)

    # Create server with user extensions
    server = create_mcp_server(
        config_factory=get_user_config,
        credentials_factory=get_user_credentials,
        lifecycle=ServerLifecycle(),
        additional_module_paths=[
            (os.path.join(app_dir, "tools"), "app.tools"),
            (os.path.join(app_dir, "prompts"), "app.prompts"),
            (os.path.join(app_dir, "resources"), "app.resources"),
        ],
        transport="streamable-http",
        load_native_mcp_tools=True,
    )

    try:
        server.run(show_banner=True)
    except requests.exceptions.ConnectionError:
        # Handle before OSError: ConnectionError is a subclass of OSError; if we
        # caught OSError first we would re-raise (errno is None) and this would never run.
        logger.error("%s", _CONNECTION_ERROR_MSG)
        sys.exit(1)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logger.error("%s", _format_port_in_use_message(port))
        else:
            raise
        sys.exit(1)
    except ClientError as e:
        if e.status_code == 401:
            logger.error("%s", _AUTH_ERROR_MSG)
            sys.exit(1)
        raise
    except KeyboardInterrupt:
        # Exit cleanly on Ctrl+C without showing traceback
        sys.exit(0)
