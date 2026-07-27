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

from workload_deploy.logs import run_logs


class FakeWL:
    def get_workload_logs(self, wid, *, level, limit):
        return {"data": [{"body": "hello", "level": level, "limit": limit}]}


def test_run_logs_passes_params():
    out = run_logs(FakeWL(), "wl1", level="debug", limit=25)
    assert out["data"][0]["level"] == "debug"
    assert out["data"][0]["limit"] == 25
