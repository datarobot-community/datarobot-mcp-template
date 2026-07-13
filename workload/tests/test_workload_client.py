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
import responses
from workload_deploy.workload_client import WorkloadClient

BASE = "https://x/api/v2"


@responses.activate
def test_create_service_artifact_sends_code_ref_and_returns_id():
    responses.post(f"{BASE}/artifacts/", json={"id": "art1"}, status=201)
    c = WorkloadClient(BASE, "tok")
    aid = c.create_service_artifact(
        name="mcp",
        port=8080,
        code_ref=WorkloadClient.code_ref("cat1", "ver1"),
        environment_vars=[{"name": "MCP_SERVER_PORT", "value": "8080"}],
        cpu=1, memory=1073741824, gpu=0,
    )
    assert aid == "art1"
    body = responses.calls[0].request.body
    import json
    payload = json.loads(body)
    container = payload["spec"]["containerGroups"][0]["containers"][0]
    assert payload["type"] == "service"
    assert container["primary"] is True
    assert container["port"] == 8080
    assert container["codeRef"]["datarobot"]["catalogId"] == "cat1"
    assert container["codeRef"]["datarobot"]["catalogVersionId"] == "ver1"
    assert container["resourceRequest"]["memory"] == 1073741824


@responses.activate
def test_trigger_build_returns_build_ids():
    responses.post(f"{BASE}/artifacts/art1/builds", json={"buildIds": ["b1"]}, status=202)
    assert WorkloadClient(BASE, "tok").trigger_build("art1") == ["b1"]


@responses.activate
def test_wait_for_build_success():
    responses.get(f"{BASE}/artifacts/art1/builds/b1", json={"status": "IN_PROGRESS"})
    responses.get(f"{BASE}/artifacts/art1/builds/b1", json={"status": "COMPLETED"})
    status = WorkloadClient(BASE, "tok").wait_for_build(
        "art1", "b1", timeout_s=30, interval_s=0, sleep=lambda _s: None
    )
    assert status == "COMPLETED"


@responses.activate
def test_wait_for_build_failure_raises_with_logs():
    responses.get(f"{BASE}/artifacts/art1/builds/b1", json={"status": "FAILED"})
    responses.get(f"{BASE}/artifacts/art1/builds/b1/logs", body="boom trace")
    with pytest.raises(RuntimeError, match="boom trace"):
        WorkloadClient(BASE, "tok").wait_for_build(
            "art1", "b1", timeout_s=30, interval_s=0, sleep=lambda _s: None
        )
