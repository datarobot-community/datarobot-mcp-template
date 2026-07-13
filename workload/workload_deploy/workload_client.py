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
    def _raise_for_status(resp: requests.Response) -> None:
        """raise_for_status that surfaces the response body in the error.

        The Workload API returns actionable validation detail (e.g. which field
        was rejected) in the 4xx body; the default requests message drops it.
        """
        if resp.status_code >= 400:
            body = resp.text[:2000]
            raise requests.HTTPError(
                f"{resp.status_code} {resp.reason} for {resp.request.method} {resp.url}\n{body}",
                response=resp,
            )

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

    @staticmethod
    def image_build_config(
        catalog_id: str,
        catalog_version_id: str,
        *,
        exec_env_id: str,
        exec_env_version_id: str,
        entrypoint: list[str],
    ) -> dict:
        """Build-on-demand config for the primary container.

        codeRef points at the uploaded source bundle; the Dockerfile is
        generated server-side from the given DataRobot execution environment
        (base image pulled from the internal registry — no public docker.io
        pull). entrypoint is the runtime command for the built image.
        """
        return {
            "codeRef": WorkloadClient.code_ref(catalog_id, catalog_version_id),
            "dockerfile": {
                "source": "generated",
                "executionEnvironmentId": exec_env_id,
                "executionEnvironmentVersionId": exec_env_version_id,
                "entrypoint": entrypoint,
            },
        }

    def create_service_artifact(
        self,
        *,
        name: str,
        port: int,
        image_build_config: dict,
        environment_vars: list[dict[str, str]],
    ) -> str:
        # Build-on-demand: the container carries imageBuildConfig (codeRef +
        # Dockerfile) instead of an imageUri. imageUri is server-populated after
        # the build; sending it (even blank) is rejected. Container-level
        # resources were removed from the schema — resources come from the
        # workload runtime (resourceBundles) at create_workload time.
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
                                "imageBuildConfig": image_build_config,
                                "environmentVars": environment_vars,
                            }
                        ]
                    }
                ]
            },
        }
        resp = self._session.post(self._url("/artifacts/"), json=payload)
        self._raise_for_status(resp)
        return resp.json()["id"]

    def trigger_build(self, artifact_id: str) -> list[str]:
        resp = self._session.post(self._url(f"/artifacts/{artifact_id}/builds"))
        resp.raise_for_status()
        data = resp.json()
        return data.get("buildIds") or data.get("build_ids") or []

    def get_build(self, artifact_id: str, build_id: str) -> dict:
        resp = self._session.get(
            self._url(f"/artifacts/{artifact_id}/builds/{build_id}")
        )
        resp.raise_for_status()
        return resp.json()

    def get_build_logs(self, artifact_id: str, build_id: str) -> str:
        resp = self._session.get(
            self._url(f"/artifacts/{artifact_id}/builds/{build_id}/logs")
        )
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
                raise TimeoutError(
                    f"build {build_id} not done after {timeout_s}s (last={status})"
                )
            sleep(interval_s)

    # --- workload lifecycle ---

    def create_workload(
        self,
        *,
        name: str,
        artifact_id: str,
        importance: str,
        replica_count: int,
        resource_bundle_id: str,
        group_name: str = "default",
    ) -> str:
        # Runtime is group-structured: one containerGroup per artifact topology
        # group (our artifact uses the default single group). Each group carries
        # its own replicaCount and resourceBundles; the API requires at least one
        # resource signal (a bundle here).
        payload = {
            "name": name,
            "artifactId": artifact_id,
            "importance": importance,
            "runtime": {
                "containerGroups": [
                    {
                        "name": group_name,
                        "replicaCount": replica_count,
                        "resourceBundles": [resource_bundle_id],
                    }
                ]
            },
        }
        resp = self._session.post(self._url("/workloads/"), json=payload)
        self._raise_for_status(resp)
        return resp.json()["id"]

    def start_workload(self, workload_id: str) -> None:
        self._session.post(
            self._url(f"/workloads/{workload_id}/start")
        ).raise_for_status()

    def stop_workload(self, workload_id: str) -> None:
        self._session.post(
            self._url(f"/workloads/{workload_id}/stop")
        ).raise_for_status()

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

    def get_workload_logs(
        self, workload_id: str, *, level: str = "info", limit: int = 100
    ) -> dict:
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
