# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased Changes

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
