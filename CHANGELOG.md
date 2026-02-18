# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased Changes

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
