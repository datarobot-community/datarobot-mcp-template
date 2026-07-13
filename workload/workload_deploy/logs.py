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

from workload_deploy.config import load_settings
from workload_deploy.state import read_state
from workload_deploy.workload_client import WorkloadClient


def run_logs(wl_client, workload_id, *, level: str, limit: int) -> dict:
    return wl_client.get_workload_logs(workload_id, level=level, limit=limit)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch runtime OTel logs for the MCP workload.")
    ap.add_argument("--workload-id")
    ap.add_argument("--level", default="info")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()
    settings = load_settings()
    wl_client = WorkloadClient(settings.endpoint, settings.token)
    workload_id = args.workload_id or read_state()["workloadId"]
    result = run_logs(wl_client, workload_id, level=args.level, limit=args.limit)
    import json
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
