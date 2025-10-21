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

from typing import Any, Union

import pytest

from base.core.dynamic_tools.deployment.config import (
    _convert_tool_string as convert_tool_string,
)
from base.core.dynamic_tools.schema import json_schema_to_python_type


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("Tool [v1] (test)!", "tool_test"),
        ("My Tool Name", "my_tool_name"),
        ("Tool__Name  [abc]", "tool_name"),
        ("[ignore] Tool!", "tool"),
        ("Tool-Name", "tool_name"),
        ("Tool   Name", "tool_name"),
        ("Tool__Name__", "tool_name"),
        ("Tool", "tool"),
        ("", ""),
        ("__Tool__", "tool"),
        ("!!!", ""),
        ("___", ""),
        ("Tool [v1] (test)!@#", "tool_test"),
    ],
)
def test_convert_tool_string(input_text: str, expected: str) -> None:
    assert convert_tool_string(input_text) == expected


class TestJsonSchemaToPythonType:
    @pytest.mark.parametrize(
        "schema_type,,expected",
        [
            ("string", str),
            ("integer", int),
            ("number", float),
            ("boolean", bool),
            ("array", list),
            ("object", dict),
            ("null", type(None)),
            ("unknown", object),
            (None, object),
            ("", object),
        ],
    )
    def test_basic_types(self, schema_type: Any, expected: type) -> None:
        result = json_schema_to_python_type(schema_type)
        if schema_type in ("unknown", None, ""):
            assert result == Any
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "schema_type,expected_types",
        [
            (["string", "null"], Union[str, type(None)]),
            (["string", "integer", "null"], Union[str, int, type(None)]),
            (["boolean", "number"], Union[bool, float]),
            (["array", "object", "null"], Union[list, dict, type(None)]),
            (["string", "string", "null"], Union[str, type(None)]),
            (["unknown", "null"], Union[Any, type(None)]),
            ([["string", "null"], "integer"], Union[str, type(None), int]),
        ],
    )
    def test_union_types(self, schema_type: Any, expected_types: Any) -> None:
        result = json_schema_to_python_type(schema_type)
        assert set(result.__args__) == set(expected_types.__args__)
