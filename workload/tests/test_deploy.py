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

import workload_deploy.deploy as deploy
from workload_deploy.config import Settings


class FakeFiles:
    def upload_bundle(self, files):
        names = {a for a, _ in files}
        assert "uv.lock" in names and "pyproject.toml" in names
        assert "Dockerfile" not in names  # generated server-side, not shipped
        return ("cat1", "ver1")


class FakeWL:
    def __init__(self):
        self.started = False

    @staticmethod
    def code_ref(c, v):
        return {"catalogId": c, "catalogVersionId": v}

    @staticmethod
    def image_build_config(c, v, *, exec_env_id, exec_env_version_id, entrypoint):
        return {
            "codeRef": {"catalogId": c, "catalogVersionId": v},
            "dockerfile": {
                "source": "generated",
                "executionEnvironmentId": exec_env_id,
                "executionEnvironmentVersionId": exec_env_version_id,
                "entrypoint": entrypoint,
            },
        }

    def create_service_artifact(self, **kw):
        self.artifact_kw = kw
        return "art1"

    def trigger_build(self, aid):
        return ["b1"]

    def wait_for_build(self, aid, bid, **kw):
        return "COMPLETED"

    def create_workload(self, **kw):
        return "wl1"

    def start_workload(self, wid):
        self.started = True

    def wait_for_workload(self, wid, **kw):
        return "running"

    def active_endpoint(self, wid):
        return "https://x/api/v2/endpoints/workloads/wl1?protonId=p2"


def _settings():
    return Settings(
        endpoint="https://x/api/v2",
        token="tok",
        workload_name="mcp",
        exec_env_id="ee1",
        exec_env_version_id="eev1",
        entrypoint=["python", "-m", "app.main"],
        replica_count=1,
        importance="low",
        port=8080,
        resource_bundle_id="cpu.medium",
        build_timeout_s=1,
        run_timeout_s=1,
        poll_interval_s=0,
    )


def test_run_deploy_happy_path(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_bytes(b"x")
    (tmp_path / "pyproject.toml").write_bytes(b"x")
    (tmp_path / "uv.lock").write_bytes(b"x")
    state_file = tmp_path / ".last_deploy.json"

    wl = FakeWL()
    result = deploy.run_deploy(
        _settings(),
        FakeFiles(),
        wl,
        dr_mcp_dir=tmp_path,
        env={"DATAROBOT_ENDPOINT": "https://x/api/v2", "DATAROBOT_API_TOKEN": "tok"},
        state_path=state_file,
    )
    assert result["workloadId"] == "wl1"
    assert result["artifactId"] == "art1"
    assert result["endpoint"].endswith("protonId=p2")
    assert result["mcpUrl"].endswith("/mcp?protonId=p2")
    assert wl.started is True
    # The server needs a startup token; it is forwarded into the container env.
    env_names = {e["name"] for e in wl.artifact_kw["environment_vars"]}
    assert "DATAROBOT_API_TOKEN" in env_names
    assert state_file.is_file()
