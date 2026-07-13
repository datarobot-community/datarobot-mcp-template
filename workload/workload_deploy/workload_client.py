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

WORKLOAD_TARGET = "running"
WORKLOAD_FAILURES = frozenset({"errored", "terminated"})


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
        self, *, name: str, port: int, code_ref: dict, environment_vars: list[dict[str, str]], cpu: int, memory: int, gpu: int
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
                except requests.RequestException:
                    pass
                raise RuntimeError(f"build {build_id} {status}\n{logs[-4000:]}")
            if now() >= deadline:
                raise TimeoutError(f"build {build_id} not done after {timeout_s}s (last={status})")
            sleep(interval_s)

    # --- workload lifecycle ---

    def create_workload(
        self,
        *,
        name: str,
        artifact_id: str,
        importance: str,
        replica_count: int,
        resource_bundle_id: str | None = None,
    ) -> str:
        runtime: dict = {"replicaCount": replica_count}
        if resource_bundle_id:
            runtime["resourceBundles"] = [resource_bundle_id]
        payload = {
            "name": name,
            "artifactId": artifact_id,
            "importance": importance,
            "runtime": runtime,
        }
        resp = self._session.post(self._url("/workloads/"), json=payload)
        resp.raise_for_status()
        return resp.json()["id"]

    def start_workload(self, workload_id: str) -> None:
        self._session.post(self._url(f"/workloads/{workload_id}/start")).raise_for_status()

    def stop_workload(self, workload_id: str) -> None:
        self._session.post(self._url(f"/workloads/{workload_id}/stop")).raise_for_status()

    def delete_workload(self, workload_id: str) -> None:
        resp = self._session.delete(self._url(f"/workloads/{workload_id}"))
        if resp.status_code != 404:
            resp.raise_for_status()

    def delete_artifact(self, artifact_id: str) -> None:
        resp = self._session.delete(self._url(f"/artifacts/{artifact_id}"))
        if resp.status_code != 404:
            resp.raise_for_status()

    def get_workload(self, workload_id: str) -> dict:
        resp = self._session.get(self._url(f"/workloads/{workload_id}"))
        resp.raise_for_status()
        return resp.json()

    def list_protons(self, workload_id: str) -> list[dict]:
        resp = self._session.get(self._url(f"/workloads/{workload_id}/protons"))
        resp.raise_for_status()
        return resp.json().get("data", []) or []

    def get_workload_events(self, workload_id: str) -> list[dict]:
        resp = self._session.get(self._url(f"/workloads/{workload_id}/events"))
        resp.raise_for_status()
        return resp.json().get("data", []) or []

    def get_workload_logs(self, workload_id: str, *, level: str = "info", limit: int = 100) -> dict:
        params: dict[str, str | int] = {"level": level, "limit": limit}
        resp = self._session.get(
            self._url(f"/otel/workload/{workload_id}/logs/"),
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    def wait_for_workload(
        self,
        workload_id: str,
        *,
        target: str = WORKLOAD_TARGET,
        timeout_s: int,
        interval_s: int,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], float] = time.monotonic,
    ) -> str:
        deadline = now() + timeout_s
        while True:
            status = str(self.get_workload(workload_id).get("status", "")).lower()
            if status == target:
                return status
            if status in WORKLOAD_FAILURES:
                raise RuntimeError(f"workload {workload_id} entered '{status}'")
            if now() >= deadline:
                raise TimeoutError(
                    f"workload {workload_id} not '{target}' after {timeout_s}s (last={status})"
                )
            sleep(interval_s)

    def active_endpoint(self, workload_id: str) -> str | None:
        protons = self.list_protons(workload_id)
        running = [p for p in protons if str(p.get("status", "")).lower() == "running"]
        chosen = running[0] if running else (protons[0] if protons else None)
        return chosen.get("endpoint") if chosen else None
