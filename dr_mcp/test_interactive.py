#!/usr/bin/env python3
# Copyright 2025 DataRobot, Inc.
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
"""
Interactive MCP Client Test Script
This script allows you to test arbitrary commands with the MCP server
using an LLM agent that can decide which tools to call.
"""

import asyncio
import os
from pathlib import Path

from datarobot_genai.drmcp import LLMMCPClient, get_dr_mcp_server_url, get_headers
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_mcp_interactive() -> None:
    """Test the MCP server interactively with LLM agent."""

    # Check for required environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or export it")
        return

    # Optional Azure OpenAI settings
    openai_api_base = os.environ.get("OPENAI_API_BASE")
    openai_api_deployment_id = os.environ.get("OPENAI_API_DEPLOYMENT_ID")
    openai_api_version = os.environ.get("OPENAI_API_VERSION")

    print("🤖 Initializing LLM MCP Client...")

    # Initialize the LLM client
    config = {
        "openai_api_key": openai_api_key,
        "openai_api_base": openai_api_base,
        "openai_api_deployment_id": openai_api_deployment_id,
        "openai_api_version": openai_api_version,
        "save_llm_responses": False,
    }
    llm_client = LLMMCPClient(str(config))

    # Get MCP server URL
    mcp_server_url = get_dr_mcp_server_url()
    if not mcp_server_url:
        print("❌ Error: MCP server URL is not configured")
        print("Please set the required environment variables for the MCP server URL")
        return

    print(f"🔗 Connecting to MCP server at: {mcp_server_url}")

    # Connect to the MCP server
    async with streamablehttp_client(
        url=mcp_server_url,
        headers=get_headers(),
    ) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print("✅ Connected to MCP server!")
            print("📋 Available tools:")

            # List available tools
            tools_result = await session.list_tools()
            for i, tool in enumerate(tools_result.tools, 1):
                print(f"  {i}. {tool.name}: {tool.description}")

            print("\n" + "=" * 60)
            print("🎯 Interactive Testing Mode")
            print("=" * 60)
            print(
                "Type your questions/commands. The AI will decide which tools to use."
            )
            print("Type 'quit' or 'exit' to stop.")
            print()

            while True:
                try:
                    # Get user input
                    user_input = input("🤔 You: ").strip()

                    if user_input.lower() in ["quit", "exit", "q"]:
                        print("👋 Goodbye!")
                        break

                    if not user_input:
                        continue

                    print("🤖 AI is thinking...")

                    # Process the prompt with MCP support
                    response = await llm_client.process_prompt_with_mcp_support(
                        prompt=user_input,
                        mcp_session=session,
                    )

                    print("\n🤖 AI Response:")
                    print("-" * 40)
                    print(response.content)

                    if response.tool_calls:
                        print("\n🔧 Tools Used:")
                        for i, tool_call in enumerate(response.tool_calls, 1):
                            print(f"  {i}. {tool_call.tool_name}")
                            print(f"     Parameters: {tool_call.parameters}")
                            print(f"     Reasoning: {tool_call.reasoning}")

                    print("\n" + "=" * 60)

                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print("Please try again.")


if __name__ == "__main__":
    # Ensure we're in the right directory
    if not Path("app").exists():
        print("❌ Error: Please run this script from the mcp directory")
        exit(1)

    # Load environment variables from .env file
    print("📄 Loading environment variables...")
    load_dotenv()

    print("🚀 Starting Interactive MCP Client Test")
    print("Make sure the MCP server is running with: task dev-background 8082")
    print()

    asyncio.run(test_mcp_interactive())
