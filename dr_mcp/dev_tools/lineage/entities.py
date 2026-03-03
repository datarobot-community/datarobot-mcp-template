# Copyright 2026 DataRobot, Inc.
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
from dataclasses import dataclass

from fastmcp.prompts import Prompt
from fastmcp.resources import Resource
from fastmcp.tools import Tool


@dataclass(frozen=True)
class UserMCPToolMetadata:
    name: str
    type: str

    @classmethod
    def from_mcp_tool(cls, mcp_tool: Tool) -> "UserMCPToolMetadata":
        return cls(
            name=mcp_tool.name,
            type=mcp_tool.meta["tool_category"],  # type: ignore[index]
        )


@dataclass(frozen=True)
class UserMCPPromptMetadata:
    name: str
    type: str

    @classmethod
    def from_mcp_prompt(cls, mcp_prompt: Prompt) -> "UserMCPPromptMetadata":
        return cls(
            name=mcp_prompt.name,
            type=mcp_prompt.meta["prompt_category"],  # type: ignore[index]
        )


@dataclass(frozen=True)
class UserMCPResourceMetadata:
    name: str
    type: str
    uri: str

    @classmethod
    def from_mcp_resource(cls, mcp_resource: Resource) -> "UserMCPResourceMetadata":
        return cls(
            name=mcp_resource.name,
            type=mcp_resource.meta["resource_category"],  # type: ignore[index]
            uri=str(mcp_resource.uri),
        )
