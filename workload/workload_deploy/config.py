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
from dataclasses import dataclass
from collections.abc import Mapping

DEFAULT_BASE_IMAGE = "datarobotdev/env-python-genai-agents:68e68b3735af84120828b074"

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
# Never forwarded to the container (per-request auth).
_NEVER_ENV = frozenset({"DATAROBOT_API_TOKEN"})


@dataclass(frozen=True)
class Settings:
    endpoint: str
    token: str
    workload_name: str
    base_image: str
    cpu: int
    memory: int
    gpu: int
    replica_count: int
    importance: str
    port: int
    resource_bundle_id: str | None
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
    return Settings(
        endpoint=endpoint,
        token=token,
        workload_name=e.get("WORKLOAD_NAME", e.get("MCP_SERVER_NAME", "datarobot-mcp-server")),
        base_image=e.get("WORKLOAD_BASE_IMAGE", DEFAULT_BASE_IMAGE),
        cpu=int(e.get("WORKLOAD_CPU", "1")),
        memory=int(e.get("WORKLOAD_MEMORY_BYTES", str(1024 * 1024 * 1024))),
        gpu=int(e.get("WORKLOAD_GPU", "0")),
        replica_count=int(e.get("WORKLOAD_REPLICAS", "1")),
        importance=e.get("WORKLOAD_IMPORTANCE", "low"),
        port=int(e.get("MCP_SERVER_PORT", "8080")),
        resource_bundle_id=e.get("WORKLOAD_BUNDLE_ID") or None,
        build_timeout_s=int(e.get("WORKLOAD_BUILD_TIMEOUT_S", "900")),
        run_timeout_s=int(e.get("WORKLOAD_RUN_TIMEOUT_S", "600")),
        poll_interval_s=int(e.get("WORKLOAD_POLL_INTERVAL_S", "5")),
    )


def build_environment_vars(env: Mapping[str, str] | None = None) -> list[dict[str, str]]:
    e = _env(env)
    out: dict[str, str] = {}
    for name, default in _ALWAYS_ENV.items():
        val = e.get(name) or default
        out[name] = val
    for name in _PASSTHROUGH_ENV:
        val = e.get(name)
        if val:
            out[name] = val
    for name in _NEVER_ENV:
        out.pop(name, None)
    return [{"name": k, "value": v} for k, v in out.items()]
