# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased Changes

## 11.10.0
- Upgraded MCP library `datarobot-genai[drmcp]` to `>=0.23.18,<0.24.0` (see [datarobot-genai CHANGELOG](https://github.com/datarobot-oss/datarobot-genai/blob/main/CHANGELOG.md) for full release notes). MCP-relevant changes since **0.15.45**:
  - **0.23.18** — Replaced `datarobot-early-access` with stable `datarobot[fs]>=3.17`.
  - **0.23.15** — Fixed `workload_logs_get` (`list_workload_logs`) raising on every call due to wrong request `params` type.
  - **0.23.13** — New `mcp_client_with_xaa_support` MCP client type with XAA support in the NAT plugin.
  - **0.23.11** — `file_manage` delete rejects non-empty directories without `recursive=True`; `files_to_omit` on clone tolerates JSON-encoded strings.
  - **0.23.10** — Targeted log secret redaction (JWTs, Bearer/Basic, API keys); shared `log_redaction` patterns in `drmcputils`.
  - **0.23.9** — Agentic Resource Discovery (ARD) support; Global MCP tool registration uses a single source of truth.
  - **0.23.5** — Sandbox SLO/SLI metrics and OTel `MeterProvider` bootstrap; fixed OTEL endpoint/headers resolving as a pair when `otel_entity_id` is set.
  - **0.23.3** — Per-request category gates via `x-datarobot-mcp-enable-proxy` and `x-datarobot-mcp-enable-dynamic-tools` (default enabled; explicit `false` disables proxied user MCP or dynamic deployment tools for that request).
  - **0.23.2** — `file_manage` copy/move `overwrite` parameter; reject recursive `file_list` at `dr://`.
  - **0.23.1** — Renamed workload MCP tools (update allowlists); polished tool metadata across connectors, predictive, panels, files API, workloads, and web search.
  - **0.23.0** — *Breaking*: `dr_mem0_memory` TTL is now in days (`default_ttl_days` / `AGENT_MEMORY_TTL_DAYS`, was seconds).
  - **0.19.7** — Pre-defined MCP tool category filters and improved tool registration.
  - **0.19.4** — `x-datarobot-external-access-token` header support for Okta integration.
  - **0.18.14** — Panels served as read-only MCP resources (`panels://…`) with review tools; sandbox entitlement fix (`ENABLE_MCP_SANDBOX`); removed API-key enforcement on MCP startup (credentials from headers at runtime).
  - **0.18.8** — `MCPServerConfig` / `MCPToolConfig` extend `DataRobotAppFrameworkBaseSettings`.
  - **0.18.6–0.18.7** — Added `file_write`, `file_manage`, `file_import`, `file_get_status`, and `file_upload` Files API tools.
  - **0.18.2** — New Files API MCP tools (`file_list`, `file_info`, `file_read`, `file_sign`), gated by `ENABLE_FILES_API_TOOLS`.
  - **0.17.7** — Consolidated workload/artifact MCP tools (39→21) for agent ergonomics.
  - **0.17.4** — Workload lifecycle submit-and-poll pattern; `workload_wait_for_status` replaced by non-blocking `workload_get_status`.
  - **0.16.5–0.16.19** — Workload MCP tool suite: proton inspection, OTel logs, artifact management, builds/repos, and rolling replacement.
  - **0.15.127** — Workload settings and observability tools (`workload_settings_get`, `workload_stats`, `workload_events`, etc.).
  - **0.15.124** — Dynamic tools core moved to `drmcpbase` for shared use with global MCP.
  - **0.15.115** — `UserMCPProvider` for user MCP proxy.
  - **0.15.109** — `execute_code` sandbox via workload API; shared `is_tool_feature_enabled` tool-gating policy.
  - **0.15.108** — Atlassian (Jira/Confluence): `AtlassianAuth` supports OAuth Bearer (HTTP) and API token Basic auth (config) via `ATLASSIAN_API_TOKEN`, optional `ATLASSIAN_EMAIL` / `ATLASSIAN_SITE_URL`.
  - **0.15.107** — MCP catalog transforms moved to `drmcpbase.fastmcp_transforms`; optional `x-datarobot-mcp-tools` header filters `tools/list` and `tools/call` by exact tool name.
  - **0.15.106** — `AUTH_RESOLUTION_STRATEGY` (`http` or `config`, default `http`) on `ToolsAuthCredentials`; strategy-aware token/secret/OAuth resolution; FastMCP auth middleware refactored into injectable `drmcpbase` middleware wired by `drmcp`.
  - **0.15.103** — Tool credentials refactored to `ToolsAuthCredentials` / `DataRobotCredentials` on `DataRobotAppFrameworkBaseSettings` (env, runtime params, `.env`, file secrets, `pulumi_config.json`); replaced `MCPServerCredentials`; added third-party config fields for Tavily, Perplexity, and Atlassian.
  - **0.15.102** — Jira `Issue` model tolerates real payloads (optional assignee email, `displayName` / `accountId` fallbacks).
  - **0.15.101** — Removed OAuth provider startup gating (`IS_*_OAUTH_PROVIDER_CONFIGURED`); predictive tools default to disabled (opt in via `ENABLE_PREDICTIVE_TOOLS` / `MCP_CLI_CONFIGS`); `/metadata` reports tool `enabled` only.
  - **0.15.100** — Renamed MCP tools (unit, integration, and acceptance tests updated).
  - **0.15.93** — Per-user DataRobot API access: `request_user_dr_client` / `request_user_dr_sdk` (ContextVar-scoped); removed `get_sdk_client()` / `get_api_client()` from `drmcp.core.clients` (use `request_user_dr_sdk` from `drtools`).
  - **0.15.82** — Removed memory management MCP tools, S3-backed agent storage, and `enable_memory_management` / AWS S3 credential fields (dropped `boto3` from the `drmcp` extra).
  - **0.15.81** — `MCPServerConfig` reads `pulumi_config.json` and standard OTEL exporter env vars for local tracing.
  - **0.15.79** — New `drmcpbase` subpackage/extra; Jira/Confluence use separate OBO token resolvers and headers; dynamic prompt removal uses FastMCP 3.x APIs.
  - **0.15.76** — Pinned `starlette>=1.0.1` and hardened MCP middleware path handling (CVE-2026-48710).
  - **0.15.59** — Dynamic tools: chat-capable deployments route to `/chat/completions` instead of `/predictions`.
  - **0.15.49** — Predictive tool `is_eligible_for_timeseries_training`: richer cadence and data-quality signals, clearer errors (what / why / fix), duplicate-row detection, and scoring-dataset handling when the target is all-null.
  - **0.15.48** — New vector-database MCP tools: `list_vector_databases` and `query_vector_database`, implemented with `tool_metadata` and plain dict returns in drtools.
  - **0.15.45** — Predictive batch scoring as submit-and-poll: `predict_by_ai_catalog` / `predict_from_project_data` return job metadata early; new `get_batch_prediction_job_status`; `get_batch_prediction_results` with configurable download timeouts; `get_exploratory_insights` optional catalog-backed column profile and histogram; realtime predict tool docs updated for the batch flow.
- **Deployment infra aligned with library auth/config model:**
  - Removed Jinja2-based `metadata.yaml` / `model-metadata.yaml` generation at deploy time; deleted `dr_mcp/metadata.yaml` and `dr_mcp/user-metadata.yaml`.
  - Added `infra/infra/dr_mcp_api_keys.py` to register Perplexity, Tavily, and Atlassian credentials as DataRobot runtime credentials when `AUTH_RESOLUTION_STRATEGY=config` and the relevant tools are enabled.
  - `infra/infra/dr_mcp.py` passes `auth_resolution_strategy` as a runtime parameter; removed AWS S3 credential wiring, OAuth “configured” booleans, and `enable_memory_management`.
  - Infra: replaced `jinja2` with direct `pulumi-datarobot>=0.10.33` dependency; bumped `datarobot-pulumi-utils` to `>=0.1.6`; default Pulumi DataRobot plugin updated to v0.10.36; lineage managers export MCP metadata record counts to the Pulumi stack; updated unit tests.
- **DR CLI (`dr_mcp.yaml`):**
  - Added optional **Configure tool credentials via environment variables** (`config_auth`) under enabled tools; opens an `auth_config` section for Perplexity/Tavily API keys and Atlassian token auth.
  - Config mode is opt-in (default remains HTTP auth); guidance notes that OAuth 2 tools (Google Drive, Microsoft Graph) are not supported in config mode and that config credentials should only be used for personal, non-shared agents.
  - Updated default MCP execution environment version ID.
- **User config:** `user_config.py` and `user_credentials.py` now extend `DataRobotAppFrameworkBaseSettings` (env, runtime params, `.env`, and `pulumi_config.json`) instead of hand-rolled `BaseSettings`.
- **Local dev / tracing:**
  - Infra: new `start`, `deploy-dev`, `dev`, and `check-use-case-id` tasks; `dr-experimentation-plugin-check` ensures the `xp` plugin is installed.
  - `dr_mcp/Taskfile.yaml`: `dev` task backgrounds `dr xp` for the local experimentation tracing dashboard.
  - `.env.template`: optional `OTEL_SDK_DISABLED` note.
- **Docs:** MCP guides moved to [`docs/datarobot-mcp/`](docs/datarobot-mcp/README.md) (client setup, architecture, dynamic tools, custom tools, deployment info); removed `dr_mcp/dev.md`; README updated for user runtime parameters via `DataRobotAppFrameworkBaseSettings` in `user_config.py` instead of `user-metadata.yaml`; [`docs/base.md`](docs/base.md) adds local OTel tracing guidance.
- **Agent skills:** Added `.claude/skills` symlink and `datarobot-app-framework-setup` skill for official DataRobot agent skills.
- **Template sync:** Refreshed `.datarobot/answers/base.yml` and `.datarobot/answers/drmcp-dr_mcp.yml` from upstream `af-component-base` and `af-component-datarobot-mcp` components.
- **CI:** Bumped `actions/checkout` 6→7 and `arduino/setup-task` 2→3.

## 11.9.0
- Upgraded MCP library `datarobot-genai[drmcp]` (see [datarobot-genai CHANGELOG](https://github.com/datarobot-oss/datarobot-genai/blob/main/CHANGELOG.md) for full release notes). MCP-relevant changes since **0.15.32** (the version noted in 11.8.0):
  - **0.15.49** — Predictive tool `is_eligible_for_timeseries_training`: richer cadence and data-quality signals, clearer errors (what / why / fix), duplicate-row detection, and scoring-dataset handling when the target is all-null.
  - **0.15.48** — New vector-database MCP tools: `list_vector_databases` and `query_vector_database`, implemented with `tool_metadata` and plain dict returns in drtools.
  - **0.15.45** — Predictive batch scoring as submit-and-poll: `predict_by_ai_catalog` / `predict_from_project_data` return job metadata early; new `get_batch_prediction_job_status`; `get_batch_prediction_results` with configurable download timeouts; `get_exploratory_insights` optional catalog-backed column profile and histogram; realtime predict tool docs updated for the batch flow.

## 11.8.0
- Upgraded MCP `datarobot-genai` from 0.15.2 to 0.15.32
  - Improved predictive drtools for MCP agents: rich tool_metadata descriptions, robust batch download polling and async-safe waits, safer CSV/JSON parsing for realtime predict, and more resilient deployment CSV validation (importance + whitespace/empty rows).
  - Categorized ToolErrors, OAuth access tokens with x-datarobot-*-access-token fallback, MCP logging that surfaces kinds to FastMCP, SDK ClientError → tool errors in predictive tools and improved third party APIs tool_metadata descriptions.
  - Implemented pagination for predictive data MCP tools.
  - Improved MCP lineage sync logic and made it always run during user MCP startup.
  - Implemented pagination for predictive model MCP tool.

- **Recipe vs base scaffolding are separate now (#115, APP-5614).** Before, one upstream “base” package carried both generic app defaults and recipe-specific pieces. Now the template uses two upstream inputs: **base** (shared DataRobot app defaults) and **datarobot-recipe** (recipe-specific defaults). That split required updating how answers are wired in and a few follow-up corrections.
- **MCP / `dr_mcp` template brought up to date (#114, #116, #120).** The files that come from the community MCP component (`af-component-datarobot-mcp`), including the snapshot under `.datarobot/answers/drmcp-dr_mcp.yml`, were refreshed to match that repo. #120 also adds template files that were supposed to ship with an earlier refresh but were missing.
- **Default answer files refreshed (#113, #117, #118, #119).** The checked-in defaults under `.datarobot/answers/` (`base.yml`, `datarobot_recipe.yml`, and related bumps) were updated to the same versions as the current `af-component-base` (and matching recipe answer) sources, so a new copy of this template starts with those up-to-date defaults.

## 11.6.2
  - Infra: raise minimum `litellm` to `>=1.74.9` (addresses CVE-2025-45809 for proxy `/key/block`)
  - DR CLI (`dr_mcp.yaml`): set `MCP_CLI_CONFIGS` multiselect to `optional: true` so Enter works with no selections

## 11.6.1
  - Updated `dr_mcp` component from 0.0.13 to 0.0.15:
  - Fix loading JSON schemas from the package directory in DRUM adapter to work from wheel or source
  - Fix dynamic tool deployment registration to filter deployments with tool tag name and value using strict AND logic
  - Fix configuration parsing to correctly disable predictive tools when MCP_CLI_CONFIGS is empty
  - Added always_prompt option to the MCP CLI config
  
## 11.6.0
- Upgrade datarobot-genai[drmcp] to >=0.5.12,<0.6.0
- Constrain Python to >=3.11,<3.14
- Add dev tools lineage: CLI `load-and-save-mcp-item-metadata` to export MCP tools, prompts, and resources metadata to YAML
- Add Taskfile task `load-and-save-mcp-item-metadata` and unit tests for lineage (entities, utils, CLI)
- Improve port-in-use handling: check before start and show user-friendly message with `lsof`/`kill` hints when MCP server port is already in use
- Add DR CLI options: "Register DataRobot dynamic tools on startup" and "Register DataRobot dynamic prompts on startup" (dynamic_tools, dynamic_prompts)
- Infra: use `resolve_execution_environment_version` from datarobot_pulumi_utils for execution environment version resolution
- Add infra tests for dr_mcp Pulumi module
- Taskfile: emoji in task descriptions; simplify dev task; deploy task uses DeployComponents list
- Template updates from af-component-datarobot-mcp and base (answers/drmcp-dr_mcp.yml, answers/base.yml)
- Add click>=8.3.0 for dev (lineage CLI)

## 11.5.0
- Upgrade to latest gen ai drmcp to >=0.4.2
- Add DR CLI support
- Add new integration tools:
    - gdrive
    - microsoft_graph
    - jira
    - confluence
    - perplexity
    - tavily

## 11.4.0
- Upgrade gen ai drmcp to 0.1.71 version
- Upgrade core libraries
- Fix client auth token
- Add DR ascii banner
- Add prefix for DR Pulumi assets when deployed
- Fix task file
- Add prompt management support
- Add CLEAN_PYTHON_ENV for codespace env
- Update README.md

## 11.2.4
- Fix readme file bug
- Add session secret
- Expose deployment ID

## 11.2.3
- Upgrade to use datarobot-genai drmcp library
- Rename infra user configs to be based on the mcp template name

## 11.2.2
- Update documentation
- Add deployment support to old releases
- Implement header forwarding
- Pin fastmcp to 2.12.2

## 11.2.1
- Exclude unit test workflow from the public repo
- Update documentations

## 11.2.0
- Initial DataRobot MCP Template Implementation
- DataRobot Predictive Tools
- Dynamic DataRobot Tool Registration
- Bring Your Own Tools
- Tracing Support
