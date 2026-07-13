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

import time
from collections.abc import Callable

import requests

BUILD_SUCCESS = "COMPLETED"
BUILD_FAILURES = frozenset({"FAILED", "CANCELLED"})


class WorkloadClient:
    def __init__(self, endpoint: str, token: str) -> None:
        self._base = endpoint.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    @staticmethod
    def code_ref(catalog_id: str, catalog_version_id: str) -> dict:
        return {
            "type": "datarobot",
            "provider": "datarobot",
            "datarobot": {
                "catalogId": catalog_id,
                "catalogVersionId": catalog_version_id,
            },
        }

    def create_service_artifact(
        self, *, name, port, code_ref, environment_vars, cpu, memory, gpu
    ) -> str:
        payload = {
            "name": name,
            "type": "service",
            "spec": {
                "containerGroups": [
                    {
                        "containers": [
                            {
                                "name": "primary",
                                "primary": True,
                                "port": port,
                                "imageUri": "",
                                "codeRef": code_ref,
                                "environmentVars": environment_vars,
                                "resourceRequest": {
                                    "cpu": cpu,
                                    "memory": memory,
                                    "gpu": gpu,
                                },
                                "readinessProbe": {
                                    "path": "/",
                                    "port": port,
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 5,
                                    "failureThreshold": 6,
                                    "scheme": "HTTP",
                                },
                            }
                        ]
                    }
                ]
            },
        }
        resp = self._session.post(self._url("/artifacts/"), json=payload)
        resp.raise_for_status()
        return resp.json()["id"]

    def trigger_build(self, artifact_id: str) -> list[str]:
        resp = self._session.post(self._url(f"/artifacts/{artifact_id}/builds"))
        resp.raise_for_status()
        data = resp.json()
        return data.get("buildIds") or data.get("build_ids") or []

    def get_build(self, artifact_id: str, build_id: str) -> dict:
        resp = self._session.get(self._url(f"/artifacts/{artifact_id}/builds/{build_id}"))
        resp.raise_for_status()
        return resp.json()

    def get_build_logs(self, artifact_id: str, build_id: str) -> str:
        resp = self._session.get(self._url(f"/artifacts/{artifact_id}/builds/{build_id}/logs"))
        resp.raise_for_status()
        return resp.text

    def wait_for_build(
        self,
        artifact_id: str,
        build_id: str,
        *,
        timeout_s: int,
        interval_s: int,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], float] = time.monotonic,
    ) -> str:
        deadline = now() + timeout_s
        while True:
            status = str(self.get_build(artifact_id, build_id).get("status", "UNKNOWN"))
            if status == BUILD_SUCCESS:
                return status
            if status in BUILD_FAILURES:
                logs = ""
                try:
                    logs = self.get_build_logs(artifact_id, build_id)
                except requests.HTTPError:
                    pass
                raise RuntimeError(f"build {build_id} {status}\n{logs[-4000:]}")
            if now() >= deadline:
                raise TimeoutError(f"build {build_id} not done after {timeout_s}s (last={status})")
            sleep(interval_s)
