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

from workload_deploy.destroy import resolve_ids, run_destroy


class FakeWL:
    def __init__(self):
        self.calls = []

    def stop_workload(self, wid):
        self.calls.append(("stop", wid))

    def wait_for_workload(self, wid, **kw):
        self.calls.append(("wait", wid, kw.get("target")))
        return "stopped"

    def delete_workload(self, wid):
        self.calls.append(("del_wl", wid))

    def delete_artifact(self, aid):
        self.calls.append(("del_art", aid))


def test_resolve_ids_prefers_cli():
    wid, aid = resolve_ids(
        "wlX", "artX", lambda: {"workloadId": "s", "artifactId": "s"}
    )
    assert (wid, aid) == ("wlX", "artX")


def test_resolve_ids_falls_back_to_state():
    wid, aid = resolve_ids(
        None, None, lambda: {"workloadId": "wlS", "artifactId": "artS"}
    )
    assert (wid, aid) == ("wlS", "artS")


def test_run_destroy_full_sequence():
    wl = FakeWL()
    run_destroy(wl, "wl1", "art1", timeout_s=1, interval_s=0, sleep=lambda _s: None)
    kinds = [c[0] for c in wl.calls]
    assert kinds == ["stop", "wait", "del_wl", "del_art"]
    assert wl.calls[1][2] == "stopped"


def test_run_destroy_tolerates_wait_failure_and_still_deletes():
    class FailWaitWL(FakeWL):
        def wait_for_workload(self, wid, **kw):
            self.calls.append(("wait", wid, kw.get("target")))
            raise RuntimeError("still stopping")

    wl = FailWaitWL()
    run_destroy(wl, "wl1", "art1", timeout_s=1, interval_s=0, sleep=lambda _s: None)
    assert [c[0] for c in wl.calls] == ["stop", "wait", "del_wl", "del_art"]
