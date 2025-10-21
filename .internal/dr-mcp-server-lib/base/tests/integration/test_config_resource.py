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

import pytest
from mcp.types import ListResourcesResult, ReadResourceResult, TextResourceContents

from .mcp_utils import integration_test_mcp_session


@pytest.mark.skip(
    reason="Skipping config resource test, not included in the MCP server library for now, commented out"
)
@pytest.mark.asyncio
class TestMCPConfigResourceIntegration:
    """Integration tests for MCP config resource."""

    async def test_config_resource(self) -> None:
        """Complete integration test for MCP config resource"""

        async with integration_test_mcp_session() as session:
            # 1 Test listing available resources
            resources_result: ListResourcesResult = await session.list_resources()
            resource_names = [resource.name for resource in resources_result.resources]

            assert "get_server_config" in resource_names

            # 2 Test getting server config
            result: ReadResourceResult = await session.read_resource(
                "config://server",  # type: ignore[arg-type]
            )

            assert len(result.contents) > 0
            assert isinstance(result.contents[0], TextResourceContents)

            result_text = result.contents[0].text
            assert "port" in result_text, f"Result text: {result_text}"
