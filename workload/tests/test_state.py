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

from workload_deploy.state import write_state, read_state, mcp_url


def test_state_roundtrip(tmp_path):
    p = tmp_path / ".last_deploy.json"
    write_state({"workloadId": "wl1", "artifactId": "art1"}, p)
    assert read_state(p)["workloadId"] == "wl1"


def test_mcp_url_inserts_path_before_query():
    ep = "https://x/api/v2/endpoints/workloads/wl1?protonId=p2"
    assert mcp_url(ep) == "https://x/api/v2/endpoints/workloads/wl1/mcp?protonId=p2"


def test_mcp_url_no_query():
    assert (
        mcp_url("https://x/api/v2/endpoints/workloads/wl1")
        == "https://x/api/v2/endpoints/workloads/wl1/mcp"
    )
