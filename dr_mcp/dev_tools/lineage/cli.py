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
import asyncio

import click

from dev_tools.lineage.utils import (
    get_dr_mcp_server_instance,
    load_and_save_mcp_prompts_metadata,
    load_and_save_mcp_resources_metadata,
    load_and_save_mcp_tools_metadata,
)


@click.group()
def cli() -> None:
    pass


async def run_load_and_save_mcp_item_metadata() -> None:
    mcp_server = get_dr_mcp_server_instance()
    await load_and_save_mcp_tools_metadata(mcp_server)
    await load_and_save_mcp_prompts_metadata(mcp_server)
    await load_and_save_mcp_resources_metadata(mcp_server)


@cli.command(name="load-and-save-mcp-item-metadata")
def load_and_save_mcp_item_metadata() -> None:
    asyncio.run(run_load_and_save_mcp_item_metadata())


if __name__ == "__main__":
    cli()
