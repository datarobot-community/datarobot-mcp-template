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
from workload_deploy.config import load_settings, build_environment_vars


def test_load_settings_requires_endpoint_and_token():
    with pytest.raises(ValueError):
        load_settings({"DATAROBOT_ENDPOINT": "https://x/api/v2"})  # no token
    with pytest.raises(ValueError):
        load_settings({"DATAROBOT_API_TOKEN": "t"})  # no endpoint


def test_load_settings_strips_trailing_slash_and_defaults():
    s = load_settings(
        {
            "DATAROBOT_ENDPOINT": "https://staging.datarobot.com/api/v2/",
            "DATAROBOT_API_TOKEN": "tok",
        }
    )
    assert s.endpoint == "https://staging.datarobot.com/api/v2"
    assert s.token == "tok"
    assert s.port == 8080
    assert s.importance == "low"
    assert s.replica_count == 1
    # Build-on-demand defaults: generated Dockerfile from a DR execution env.
    assert s.exec_env_id
    assert s.exec_env_version_id
    assert s.entrypoint == ["python", "-m", "app.main"]
    assert s.resource_bundle_id  # required resource signal, defaulted


def test_load_settings_overrides_exec_env_and_entrypoint():
    s = load_settings(
        {
            "DATAROBOT_ENDPOINT": "https://x/api/v2",
            "DATAROBOT_API_TOKEN": "tok",
            "WORKLOAD_EXEC_ENV_ID": "ee9",
            "WORKLOAD_EXEC_ENV_VERSION_ID": "eev9",
            "WORKLOAD_ENTRYPOINT": "python -m app.other",
        }
    )
    assert s.exec_env_id == "ee9"
    assert s.exec_env_version_id == "eev9"
    assert s.entrypoint == ["python", "-m", "app.other"]


def test_env_vars_include_defaults_passthrough_and_token():
    env = {
        "DATAROBOT_ENDPOINT": "https://x/api/v2",
        "DATAROBOT_API_TOKEN": "SECRET",
        "MCP_SERVER_NAME": "my-mcp",
        "OTEL_COLLECTOR_BASE_URL": "http://collector:4318",
        "SANDBOX_IMAGE": "",  # empty -> skipped
    }
    pairs = {e["name"]: e["value"] for e in build_environment_vars(env)}
    assert pairs["DATAROBOT_ENDPOINT"] == "https://x/api/v2"
    assert pairs["MCP_SERVER_PORT"] == "8080"  # ALWAYS default
    assert pairs["OTEL_ENABLED"] == "true"  # ALWAYS default
    assert pairs["MCP_SERVER_NAME"] == "my-mcp"  # passthrough
    assert pairs["OTEL_COLLECTOR_BASE_URL"] == "http://collector:4318"
    assert "SANDBOX_IMAGE" not in pairs  # empty skipped
    # The server requires a startup token; it is forwarded from the deploy env.
    assert pairs["DATAROBOT_API_TOKEN"] == "SECRET"
