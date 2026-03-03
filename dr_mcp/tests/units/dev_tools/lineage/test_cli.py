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
import asyncio
from typing import Iterator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from click.testing import CliRunner

from dev_tools.lineage.cli import (
    load_and_save_mcp_item_metadata,
    run_load_and_save_mcp_item_metadata,
)


@pytest.fixture
def module_under_test() -> str:
    return "dev_tools.lineage.cli"


class TestLoadAndSaveMCPItemMetadata:
    CLI_FUNCTION = load_and_save_mcp_item_metadata

    @pytest.fixture
    def mock_get_dr_mcp_server_instance(self, module_under_test: str) -> Iterator[Mock]:
        with patch(f"{module_under_test}.get_dr_mcp_server_instance") as mock_func:
            yield mock_func

    @pytest.fixture
    def mock_asyncio_run(self) -> Iterator[Mock]:
        with patch.object(asyncio, "run") as mock_func:
            yield mock_func

    @pytest.fixture
    def mock_load_and_save_mcp_tools_metadata(
        self, module_under_test: str
    ) -> Iterator[AsyncMock]:
        with patch(
            f"{module_under_test}.load_and_save_mcp_tools_metadata",
            new_callable=AsyncMock,
        ) as mock_func:
            yield mock_func

    @pytest.fixture
    def mock_load_and_save_mcp_prompts_metadata(
        self, module_under_test: str
    ) -> Iterator[AsyncMock]:
        with patch(
            f"{module_under_test}.load_and_save_mcp_prompts_metadata",
            new_callable=AsyncMock,
        ) as mock_func:
            yield mock_func

    @pytest.fixture
    def mock_load_and_save_mcp_resources_metadata(
        self, module_under_test: str
    ) -> Iterator[AsyncMock]:
        with patch(
            f"{module_under_test}.load_and_save_mcp_resources_metadata",
            new_callable=AsyncMock,
        ) as mock_func:
            yield mock_func

    def test_cli_invoke_run_load_and_save_mcp_item_metadata_logic(
        self,
        mock_asyncio_run: Mock,
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(self.CLI_FUNCTION)

        assert result.exit_code == 0

        (coroutine_func,) = mock_asyncio_run.call_args.args
        assert coroutine_func.__name__ == "run_load_and_save_mcp_item_metadata"

    @pytest.mark.asyncio
    async def test_run_load_and_save_mcp_item_metadata(
        self,
        mock_get_dr_mcp_server_instance: Mock,
        mock_load_and_save_mcp_tools_metadata: AsyncMock,
        mock_load_and_save_mcp_prompts_metadata: AsyncMock,
        mock_load_and_save_mcp_resources_metadata: AsyncMock,
    ) -> None:
        await run_load_and_save_mcp_item_metadata()

        mock_get_dr_mcp_server_instance.assert_called_once_with()
        mock_mcp_server_instance = mock_get_dr_mcp_server_instance.return_value
        mock_load_and_save_mcp_tools_metadata.assert_called_once_with(
            mock_mcp_server_instance
        )
        mock_load_and_save_mcp_prompts_metadata.assert_called_once_with(
            mock_mcp_server_instance
        )
        mock_load_and_save_mcp_resources_metadata.assert_called_once_with(
            mock_mcp_server_instance
        )
