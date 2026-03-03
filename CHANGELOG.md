# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased Changes

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
