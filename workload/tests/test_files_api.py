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

import responses
from workload_deploy.files_api import FilesApiClient

BASE = "https://x/api/v2"


@responses.activate
def test_upload_bundle_runs_full_sequence():
    responses.post(f"{BASE}/files/fromFile/", json={"catalogId": "cat1"}, status=201)
    responses.post(f"{BASE}/files/cat1/stages/", json={"stageId": "stg1"}, status=201)
    responses.post(f"{BASE}/files/cat1/stages/stg1/upload/", json={}, status=200)
    responses.post(
        f"{BASE}/files/cat1/fromStage/", json={"catalogVersionId": "ver1"}, status=200
    )

    cat, ver = FilesApiClient(BASE, "tok").upload_bundle(
        [("Dockerfile", b"FROM base"), ("uv.lock", b"lock")]
    )
    assert (cat, ver) == ("cat1", "ver1")
    # two files uploaded to the stage
    upload_calls = [c for c in responses.calls if c.request.url.endswith("/upload/")]
    assert len(upload_calls) == 2
    # auth header present
    assert responses.calls[0].request.headers["Authorization"] == "Bearer tok"
