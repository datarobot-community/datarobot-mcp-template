# workload — Deploy the MCP server as a DataRobot Workload

Deploys `dr_mcp` (the DataRobot MCP server) via the DataRobot **Workload API**
(build-on-demand from source, no Pulumi/infrastructure-as-code involved). This
is a lightweight alternative to the `infra/` Pulumi stack for teams that want
a quick, disposable deployment path.

The flow: bundle `dr_mcp` source + `dr_mcp/docker/Dockerfile.workload` →
upload to the Files API → create a draft service artifact with a `codeRef` →
trigger an image build → wait for the build → create + start the workload →
wait until it's running → print the endpoint and MCP URL.

## Prerequisites

- `DATAROBOT_ENDPOINT` — your DataRobot API endpoint (e.g.
  `https://app.datarobot.com/api/v2`).
- `DATAROBOT_API_TOKEN` — a DataRobot API token with permission to create
  Files API catalog entries, service artifacts, and workloads. This token is
  used **only** by the local deploy/destroy/logs tooling — it is never
  forwarded into the deployed container (see "Auth model" below).
- The `ENABLE_WORKLOAD_API_CODE` feature flag must be enabled on your
  DataRobot instance/org. Without it, artifact creation or the image build
  will fail (typically surfacing as a 4xx from the Workload API).

Install dependencies once with `task workload:install` (or let
`task deployasworkload` do it for you).

## Tasks

Run these from the repo root (they delegate into `workload/` via the Taskfile
`workload` include), or from inside `workload/` using the bare task names.

| Root task | workload/ task | Description |
| --- | --- | --- |
| `task deployasworkload` | `task install && task deploy` | Installs deps, then bundles + uploads + builds + deploys the MCP server as a workload. Prints the artifact/workload/build ids, the workload endpoint, and the derived MCP URL on success. |
| `task destroyworkload` | `task destroy` | Stops and deletes the workload, then deletes the service artifact. Reads ids from `workload/.last_deploy.json` (written by the last successful deploy) unless `--workload-id`/`--artifact-id` are passed explicitly. |
| `task workloadlogs` | `task logs` | Fetches recent runtime OTel logs for the workload (`--workload-id`, `--level`, `--limit`). Useful for confirming the server booted and for diagnosing a failed deploy. |

Extra CLI args pass through, e.g.:

```bash
task destroyworkload -- --workload-id <id> --artifact-id <id>
task workloadlogs -- --level debug --limit 200
```

You can also run the underlying modules directly from `workload/`:

```bash
uv run python -m workload_deploy.deploy
uv run python -m workload_deploy.destroy [--workload-id ID] [--artifact-id ID]
uv run python -m workload_deploy.logs [--workload-id ID] [--level info] [--limit 100]
```

## Configuration (env vars)

All settings are read from the environment (see `workload_deploy/config.py`).

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATAROBOT_ENDPOINT` | *(required)* | DataRobot API endpoint. |
| `DATAROBOT_API_TOKEN` | *(required)* | Token for the local deploy/destroy/logs tooling. **Not** forwarded to the container. |
| `WORKLOAD_NAME` | `MCP_SERVER_NAME` or `datarobot-mcp-server` | Name of the service artifact/workload. |
| `WORKLOAD_BASE_IMAGE` | `datarobotdev/env-python-genai-agents:<tag>` | Base image the workload build starts from. |
| `WORKLOAD_CPU` | `1` | CPU units requested for the workload. |
| `WORKLOAD_MEMORY_BYTES` | `1073741824` (1 GiB) | Memory requested for the workload. |
| `WORKLOAD_GPU` | `0` | GPU units requested. |
| `WORKLOAD_REPLICAS` | `1` | Replica count. |
| `WORKLOAD_IMPORTANCE` | `low` | Workload importance/priority tier. |
| `WORKLOAD_BUNDLE_ID` | *(unset)* | Optional resource bundle id override. |
| `WORKLOAD_BUILD_TIMEOUT_S` | `900` | Max seconds to wait for the image build. |
| `WORKLOAD_RUN_TIMEOUT_S` | `600` | Max seconds to wait for the workload to reach running (deploy) or stopped (destroy). |
| `WORKLOAD_POLL_INTERVAL_S` | `5` | Poll interval in seconds for build/workload status checks. |
| `MCP_SERVER_PORT` | `8080` | Port the MCP server listens on inside the container. |
| `MCP_SERVER_LOG_LEVEL`, `APP_LOG_LEVEL`, `OTEL_ENABLED`, and the other `MCP_SERVER_*`/`OTEL_*`/`ENABLE_*`/`AWS_*` variables | — | Forwarded into the container's environment when set (see `_PASSTHROUGH_ENV` in `config.py`); otherwise omitted. |

## Auth model — no token in the container

`DATAROBOT_API_TOKEN` is used locally by this tooling to call the Files API
and Workload API on your behalf, but it is explicitly excluded from the
environment variables baked into the deployed workload
(`_NEVER_ENV` in `config.py`). The deployed MCP server itself does **not**
carry a service-wide credential.

Instead, the deployed server relies on **per-request auth**: each MCP client
must pass its own DataRobot bearer token with every request. This means:

- The workload can boot and pass health checks with no
  `DATAROBOT_API_TOKEN` set in its environment.
- Every caller is authenticated/authorized individually, using their own
  DataRobot token/permissions — there is no shared credential to leak or
  rotate for the whole deployment.

When validating a deploy, confirm the server started without
`DATAROBOT_API_TOKEN` in its environment (`task workloadlogs`), and confirm
that hitting the MCP URL without a bearer token is rejected while a request
with a valid per-caller token succeeds.

## MCP mount path

The MCP URL printed after a deploy is derived by appending a mount path
(default `/mcp`) to the workload's active endpoint — see `mcp_url()` in
`workload_deploy/state.py`. This default matches how the FastMCP server in
`dr_mcp` is expected to mount its MCP route, but **verify it against the
actual running server** after each deploy (e.g. `curl` the printed MCP URL,
or check `dr_mcp/app` for how the mount path is configured) — if the server
mounts MCP elsewhere, adjust the mount path used to build the URL.

## State file

A successful deploy writes `workload/.last_deploy.json` with the artifact id,
workload id, catalog/version ids, build id, endpoint, and MCP URL.
`destroyworkload` and `workloadlogs` read this file by default so you don't
have to pass ids by hand; pass `--workload-id`/`--artifact-id` explicitly to
override.

## Local development

```bash
task workload:install   # uv sync --all-extras --dev
task workload:test      # uv run pytest -q
task workload:lint      # ruff format + ruff check --fix + mypy
```
