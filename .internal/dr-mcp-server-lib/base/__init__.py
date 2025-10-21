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

"""
DataRobot MCP Server Library

A reusable library for building Model Context Protocol (MCP) servers with DataRobot integration.
"""

__version__ = "0.1.0"

# Export main server components
from .core.common import get_sdk_client
from .core.config import MCPServerConfig, get_config
from .core.config_utils import (
    extract_datarobot_credential_runtime_param_payload,
    extract_datarobot_dict_runtime_param_payload,
    extract_datarobot_runtime_param_payload,
)
from .core.constants import RUNTIME_PARAM_ENV_VAR_NAME_PREFIX
from .core.credentials import MCPServerCredentials, get_credentials
from .core.dr_mcp_server import (
    BaseServerLifecycle,
    DataRobotMCPServer,
    create_mcp_server,
)
from .core.logging import MCPLogging
from .core.mcp_instance import dr_mcp_tool, register_tools

__all__ = [
    # Version
    "__version__",
    # Main server
    "DataRobotMCPServer",
    "create_mcp_server",
    "BaseServerLifecycle",
    # Configuration
    "get_config",
    "MCPServerConfig",
    # Credentials
    "get_credentials",
    "MCPServerCredentials",
    # Constants
    "RUNTIME_PARAM_ENV_VAR_NAME_PREFIX",
    # User extensibility
    "get_sdk_client",
    "dr_mcp_tool",
    "register_tools",
    # Utilities
    "MCPLogging",
    "extract_datarobot_runtime_param_payload",
    "extract_datarobot_dict_runtime_param_payload",
    "extract_datarobot_credential_runtime_param_payload",
]
