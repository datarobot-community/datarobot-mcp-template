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

import logging
from typing import Annotated

from datarobot_genai.drmcp import dr_mcp_tool  # noqa: F401
from fastmcp.exceptions import ToolError
from fastmcp.tools.tool import ToolResult

logger = logging.getLogger(__name__)

"""
Example of a user tool, use as a template for your own tools implementation.
NOTE: uncomment the @dr_mcp_tool decorator to register the tool
"""


# @dr_mcp_tool(tags={"user", "tools", "example"})
async def user_tool_example(
    argument1: Annotated[str, "A user tool example argument."],
) -> ToolResult:
    """
    A user tool example description.
    """

    if not argument1 or not argument1.strip():
        raise ToolError("Argument validation error: 'argument1' cannot be empty.")

    logger.info(f"User tool example called with argument: {argument1}")
    return ToolResult(structured_content={"message": "user tool example"})
