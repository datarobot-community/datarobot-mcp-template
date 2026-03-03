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
from unittest.mock import Mock

from pydantic import AnyUrl

from dev_tools.lineage.entities import (
    UserMCPPromptMetadata,
    UserMCPResourceMetadata,
    UserMCPToolMetadata,
)


class TestUserMCPToolMetadata:
    def test_from_mcp_tool(self) -> None:
        expected_naem = "dafa"
        expected_category = "adfas"
        mcp_tool = Mock()
        mcp_tool.name = expected_naem
        mcp_tool.meta = {"tool_category": expected_category}
        output = UserMCPToolMetadata.from_mcp_tool(mcp_tool)

        assert output == UserMCPToolMetadata(name=expected_naem, type=expected_category)


class TestUserMCPPromptMetadata:
    def test_from_mcp_prompt(self) -> None:
        expected_naem = "dafa"
        expected_category = "adfas"
        mcp_prompt = Mock()
        mcp_prompt.name = expected_naem
        mcp_prompt.meta = {"prompt_category": expected_category}
        output = UserMCPPromptMetadata.from_mcp_prompt(mcp_prompt)

        assert output == UserMCPPromptMetadata(
            name=expected_naem, type=expected_category
        )


class TestUserMCPResourceMetadata:
    def test_from_mcp_resource(self) -> None:
        expected_naem = "dafa"
        expected_category = "adfas"
        expected_uri = "uri://adafs"
        mcp_resource = Mock()
        mcp_resource.name = expected_naem
        mcp_resource.meta = {"resource_category": expected_category}
        mcp_resource.uri = AnyUrl(expected_uri)
        output = UserMCPResourceMetadata.from_mcp_resource(mcp_resource)

        assert output == UserMCPResourceMetadata(
            name=expected_naem, type=expected_category, uri=expected_uri
        )
