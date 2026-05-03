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
import pytest

from typing import Iterator
from unittest.mock import Mock
from unittest.mock import patch

from datarobot.errors import ClientError
from dev_tools.lineage.utils import is_lineage_feature_enabled


@pytest.fixture
def module_under_test() -> str:
    return "dev_tools.lineage.utils"


@pytest.fixture
def mock_fetch_flag_statuses(module_under_test: str) -> Iterator[Mock]:
    with patch(f"{module_under_test}.fetch_flag_statuses") as mock_func:
        yield mock_func


def test_is_lineage_feature_enabled(mock_fetch_flag_statuses: Mock) -> None:
    flag_enablement = Mock()
    expected_feature_flag = "ENABLE_MCP_TOOLS_GALLERY_SUPPORT"
    mock_fetch_flag_statuses.return_value = {expected_feature_flag: flag_enablement}
    output = is_lineage_feature_enabled()

    mock_fetch_flag_statuses.assert_called_once_with([expected_feature_flag])
    assert output == flag_enablement


def test_is_lineage_feature_enabled_return_false_if_raise_error(
    mock_fetch_flag_statuses: Mock,
) -> None:
    expected_feature_flag = "ENABLE_MCP_TOOLS_GALLERY_SUPPORT"
    mock_fetch_flag_statuses.side_effect = ClientError(Mock(), Mock())
    output = is_lineage_feature_enabled()

    mock_fetch_flag_statuses.assert_called_once_with([expected_feature_flag])
    assert output is False
