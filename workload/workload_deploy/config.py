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

import os
import shlex
from dataclasses import dataclass
from collections.abc import Mapping

# Build-on-demand base: the IBS renders the Dockerfile from a DataRobot
# execution environment (pulled from the internal registry) rather than a
# public `FROM` image. Defaults to the "MCP Server [genai-demo]" env; override
# via WORKLOAD_EXEC_ENV_ID / WORKLOAD_EXEC_ENV_VERSION_ID.
DEFAULT_EXEC_ENV_ID = "6a4f0d23b4cb1f8f59abd2db"
DEFAULT_EXEC_ENV_VERSION_ID = "6a4f2377ba28149af647b1cc"
# Runtime command for the generated image; the MCP server boots via app.main.
DEFAULT_ENTRYPOINT = ("python", "-m", "app.main")
# Compute bundle for the workload (1 CPU / 1 GB). The API requires a resource
# signal; override via WORKLOAD_BUNDLE_ID. Bundle ids come from
# GET /api/v2/mlops/compute/bundles/ (e.g. cpu.small, cpu.medium, cpu.large).
DEFAULT_RESOURCE_BUNDLE_ID = "cpu.medium"

# name -> default; always emitted (default used only when unset/empty in env).
_ALWAYS_ENV: dict[str, str] = {
    "MCP_SERVER_PORT": "8080",
    "MCP_SERVER_LOG_LEVEL": "WARNING",
    "APP_LOG_LEVEL": "INFO",
    "OTEL_ENABLED": "true",
}
# forwarded from env only when present and non-empty.
_PASSTHROUGH_ENV: tuple[str, ...] = (
    "DATAROBOT_ENDPOINT",
    # The datarobot_genai MCP server requires a DataRobot token at startup
    # (credentials.has_datarobot_credentials); there is no tokenless mode. The
    # token is supplied via the local .env / deploy environment (never committed)
    # and forwarded into the container here.
    "DATAROBOT_API_TOKEN",
    "MCP_SERVER_NAME",
    "MCP_SERVER_REGISTER_DYNAMIC_TOOLS_ON_STARTUP",
    "MCP_SERVER_REGISTER_DYNAMIC_PROMPTS_ON_STARTUP",
    "MCP_SERVER_TOOL_REGISTRATION_DUPLICATE_BEHAVIOR",
    "MCP_SERVER_TOOL_REGISTRATION_ALLOW_EMPTY_SCHEMA",
    "MCP_SERVER_PROMPT_REGISTRATION_DUPLICATE_BEHAVIOR",
    "OTEL_ATTRIBUTES",
    "OTEL_ENABLED_HTTP_INSTRUMENTORS",
    "OTEL_COLLECTOR_BASE_URL",
    "OTEL_ENTITY_ID",
    "ENABLE_MEMORY_MANAGEMENT",
    "ENABLE_PREDICTIVE_TOOLS",
    "ENABLE_PANELS_TOOLS",
    "ENABLE_CONFLUENCE_TOOLS",
    "ENABLE_GDRIVE_TOOLS",
    "ENABLE_JIRA_TOOLS",
    "ENABLE_MICROSOFT_GRAPH_TOOLS",
    "ENABLE_PERPLEXITY_TOOLS",
    "ENABLE_TAVILY_TOOLS",
    "USER_NAME",
    "SANDBOX_IMAGE",
    "SESSION_SECRET_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_PREDICTIONS_S3_BUCKET",
    "AWS_PREDICTIONS_S3_PREFIX",
)
# Reserved for values that must never reach the container. Empty for now.
_NEVER_ENV: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Settings:
    endpoint: str
    token: str
    workload_name: str
    exec_env_id: str
    exec_env_version_id: str
    entrypoint: list[str]
    replica_count: int
    importance: str
    port: int
    resource_bundle_id: str
    build_timeout_s: int
    run_timeout_s: int
    poll_interval_s: int


def _env(env: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if env is None else env


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    e = _env(env)
    endpoint = (e.get("DATAROBOT_ENDPOINT") or "").rstrip("/")
    token = e.get("DATAROBOT_API_TOKEN") or ""
    if not endpoint:
        raise ValueError("DATAROBOT_ENDPOINT is required")
    if not token:
        raise ValueError("DATAROBOT_API_TOKEN is required")
    entrypoint_raw = e.get("WORKLOAD_ENTRYPOINT")
    entrypoint = (
        shlex.split(entrypoint_raw) if entrypoint_raw else list(DEFAULT_ENTRYPOINT)
    )
    return Settings(
        endpoint=endpoint,
        token=token,
        workload_name=e.get(
            "WORKLOAD_NAME", e.get("MCP_SERVER_NAME", "datarobot-mcp-server")
        ),
        exec_env_id=e.get("WORKLOAD_EXEC_ENV_ID") or DEFAULT_EXEC_ENV_ID,
        exec_env_version_id=e.get("WORKLOAD_EXEC_ENV_VERSION_ID")
        or DEFAULT_EXEC_ENV_VERSION_ID,
        entrypoint=entrypoint,
        replica_count=int(e.get("WORKLOAD_REPLICAS") or "1"),
        importance=e.get("WORKLOAD_IMPORTANCE", "low"),
        port=int(e.get("MCP_SERVER_PORT") or "8080"),
        resource_bundle_id=e.get("WORKLOAD_BUNDLE_ID") or DEFAULT_RESOURCE_BUNDLE_ID,
        build_timeout_s=int(e.get("WORKLOAD_BUILD_TIMEOUT_S") or "900"),
        run_timeout_s=int(e.get("WORKLOAD_RUN_TIMEOUT_S") or "600"),
        poll_interval_s=int(e.get("WORKLOAD_POLL_INTERVAL_S") or "5"),
    )


def build_environment_vars(
    env: Mapping[str, str] | None = None,
) -> list[dict[str, str]]:
    e = _env(env)
    out: dict[str, str] = {}
    for name, default in _ALWAYS_ENV.items():
        val = e.get(name) or default
        out[name] = val
    for name in _PASSTHROUGH_ENV:
        passthrough_val = e.get(name)
        if passthrough_val:
            out[name] = passthrough_val
    for name in _NEVER_ENV:
        out.pop(name, None)
    return [{"name": k, "value": v} for k, v in out.items()]
