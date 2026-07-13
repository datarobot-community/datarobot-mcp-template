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

import requests


class FilesApiClient:
    def __init__(self, endpoint: str, token: str) -> None:
        self._base = endpoint.rstrip("/")
        self._token = token
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {token}"})

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    def create_catalog(self) -> str:
        resp = requests.post(
            self._url("/files/fromFile/"),
            headers={"Authorization": f"Bearer {self._token}"},
            files={"file": (".placeholder", b"placeholder", "application/octet-stream")},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("catalogId") or data["id"]

    def create_stage(self, catalog_id: str) -> str:
        resp = self._session.post(
            self._url(f"/files/{catalog_id}/stages/"),
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("stageId") or data["id"]

    def upload_to_stage(
        self, catalog_id: str, stage_id: str, file_name: str, content: bytes
    ) -> None:
        resp = requests.post(
            self._url(f"/files/{catalog_id}/stages/{stage_id}/upload/"),
            headers={"Authorization": f"Bearer {self._token}"},
            files={"file": (file_name, content, "application/octet-stream")},
        )
        resp.raise_for_status()

    def apply_stage(self, catalog_id: str, stage_id: str) -> str:
        resp = self._session.post(
            self._url(f"/files/{catalog_id}/fromStage/"),
            json={"stageId": stage_id, "overwrite": "replace"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("catalogVersionId") or data["versionId"]

    def upload_bundle(self, files: list[tuple[str, bytes]]) -> tuple[str, str]:
        catalog_id = self.create_catalog()
        stage_id = self.create_stage(catalog_id)
        for name, content in files:
            self.upload_to_stage(catalog_id, stage_id, name, content)
        version_id = self.apply_stage(catalog_id, stage_id)
        return catalog_id, version_id
