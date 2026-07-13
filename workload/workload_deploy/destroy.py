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

import argparse
import time

from workload_deploy.config import load_settings
from workload_deploy.state import read_state
from workload_deploy.workload_client import WorkloadClient


def resolve_ids(args_workload, args_artifact, state_reader=read_state):
    if args_workload:
        return args_workload, args_artifact
    state = state_reader()
    return state["workloadId"], state.get("artifactId")


def run_destroy(
    wl_client,
    workload_id,
    artifact_id,
    *,
    timeout_s,
    interval_s,
    sleep=time.sleep,
    now=time.monotonic,
) -> None:
    wl_client.stop_workload(workload_id)
    try:
        wl_client.wait_for_workload(
            workload_id,
            target="stopped",
            timeout_s=timeout_s,
            interval_s=interval_s,
            sleep=sleep,
            now=now,
        )
    except (RuntimeError, TimeoutError):
        pass  # proceed to delete regardless
    wl_client.delete_workload(workload_id)
    if artifact_id:
        wl_client.delete_artifact(artifact_id)


def main() -> int:
    ap = argparse.ArgumentParser(description="Destroy the MCP workload + artifact.")
    ap.add_argument("--workload-id")
    ap.add_argument("--artifact-id")
    args = ap.parse_args()
    settings = load_settings()
    wl_client = WorkloadClient(settings.endpoint, settings.token)
    workload_id, artifact_id = resolve_ids(args.workload_id, args.artifact_id)
    run_destroy(
        wl_client,
        workload_id,
        artifact_id,
        timeout_s=settings.run_timeout_s,
        interval_s=settings.poll_interval_s,
    )
    print(
        f"Destroyed workload {workload_id}"
        + (f" and artifact {artifact_id}" if artifact_id else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
