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

# import logging

# from fastmcp.prompts.prompt import PromptMessage, TextContent

# from base.core.mcp_instance import dr_mcp_extras

# logger = logging.getLogger(__name__)


# @mcp.prompt
# @dr_mcp_extras(type="prompt")
# async def get_deployment_info_prompt(deployment_id: str) -> PromptMessage:
#     """Get detailed information about a deployment including its features, model type, and requirements"""
#     text = f"""
#     Show me detailed information about deployment {deployment_id}, including:
#     - Model type and configuration
#     - Required features and their importance
#     - Target variable details
#     - Time series configuration (if applicable)
#     """
#     return PromptMessage(role="user", content=TextContent(type="text", text=text))
