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

import sys
from pathlib import Path

from workload_deploy.bundle import assemble_bundle
from workload_deploy.config import Settings, build_environment_vars, load_settings
from workload_deploy.files_api import FilesApiClient
from workload_deploy.state import STATE_PATH, mcp_url, write_state
from workload_deploy.workload_client import WorkloadClient

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DR_MCP_DIR = _REPO_ROOT / "dr_mcp"


def run_deploy(
    settings: Settings,
    files_client,
    wl_client,
    *,
    dr_mcp_dir,
    env,
    state_path: Path = STATE_PATH,
) -> dict:
    print(f"==> Assembling bundle from {dr_mcp_dir}")
    files = assemble_bundle(dr_mcp_dir)

    print("==> Uploading source to Files API")
    catalog_id, version_id = files_client.upload_bundle(files)
    # Print the catalog ids before the artifact step (which can fail) so a
    # failed deploy leaves a recoverable reference to the uploaded source.
    print(f"    uploaded: catalogId={catalog_id} catalogVersionId={version_id}")

    print(
        "==> Creating draft artifact (imageBuildConfig/codeRef, generated Dockerfile)"
    )
    artifact_id = wl_client.create_service_artifact(
        name=settings.workload_name,
        port=settings.port,
        image_build_config=wl_client.image_build_config(
            catalog_id,
            version_id,
            exec_env_id=settings.exec_env_id,
            exec_env_version_id=settings.exec_env_version_id,
            entrypoint=settings.entrypoint,
        ),
        environment_vars=build_environment_vars(env),
    )

    print(f"==> Triggering image build for artifact {artifact_id}")
    build_ids = wl_client.trigger_build(artifact_id)
    if not build_ids:
        raise RuntimeError("no build id returned from trigger_build")
    build_id = build_ids[0]
    print(f"==> Waiting for build {build_id} (up to {settings.build_timeout_s}s)")
    wl_client.wait_for_build(
        artifact_id,
        build_id,
        timeout_s=settings.build_timeout_s,
        interval_s=settings.poll_interval_s,
    )

    print("==> Creating workload")
    workload_id = wl_client.create_workload(
        name=settings.workload_name,
        artifact_id=artifact_id,
        importance=settings.importance,
        replica_count=settings.replica_count,
        resource_bundle_id=settings.resource_bundle_id,
    )

    print(f"==> Starting workload {workload_id}")
    wl_client.start_workload(workload_id)
    try:
        wl_client.wait_for_workload(
            workload_id,
            timeout_s=settings.run_timeout_s,
            interval_s=settings.poll_interval_s,
        )
    except (RuntimeError, TimeoutError) as exc:
        print(f"!! workload did not reach running: {exc}", file=sys.stderr)
        _dump_diagnostics(wl_client, workload_id)
        raise

    endpoint = wl_client.active_endpoint(workload_id) or ""
    result = {
        "artifactId": artifact_id,
        "workloadId": workload_id,
        "catalogId": catalog_id,
        "catalogVersionId": version_id,
        "buildId": build_id,
        "endpoint": endpoint,
        "mcpUrl": mcp_url(endpoint) if endpoint else "",
    }
    write_state(result, state_path)
    return result


def _dump_diagnostics(wl_client, workload_id: str) -> None:
    try:
        logs = wl_client.get_workload_logs(workload_id, level="debug", limit=100)
        print("---- recent OTel logs ----", file=sys.stderr)
        print(logs, file=sys.stderr)
    except Exception as exc:  # noqa: BLE001 - best-effort diagnostics
        print(f"(could not fetch OTel logs: {exc})", file=sys.stderr)
    try:
        events = wl_client.get_workload_events(workload_id)
        print("---- workload events ----", file=sys.stderr)
        for ev in events:
            print(ev, file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"(could not fetch events: {exc})", file=sys.stderr)


def main() -> int:
    import os

    settings = load_settings()
    files_client = FilesApiClient(settings.endpoint, settings.token)
    wl_client = WorkloadClient(settings.endpoint, settings.token)
    result = run_deploy(
        settings,
        files_client,
        wl_client,
        dr_mcp_dir=_DR_MCP_DIR,
        env=os.environ,
    )
    print("\n=== MCP workload deployed ===")
    for k in ("artifactId", "workloadId", "catalogVersionId", "buildId"):
        print(f"{k}: {result[k]}")
    print(f"Endpoint: {result['endpoint']}")
    print(f"MCP URL : {result['mcpUrl']}")
    print(
        "Note: callers authenticate per-request with their own DataRobot bearer token."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
