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

import os

from datarobot_genai.drmcp import create_mcp_server

from app.core.server_lifecycle import ServerLifecycle
from app.core.user_config import get_user_config
from app.core.user_credentials import get_user_credentials

if __name__ == "__main__":
    # Get paths to user modules
    app_dir = os.path.dirname(__file__)

    # Create server with user extensions
    server = create_mcp_server(
        config_factory=get_user_config,
        credentials_factory=get_user_credentials,
        lifecycle=ServerLifecycle(),
        additional_module_paths=[
            (os.path.join(app_dir, "tools"), "app.tools"),
            (os.path.join(app_dir, "prompts"), "app.prompts"),
            (os.path.join(app_dir, "resources"), "app.resources"),
        ],
        transport="streamable-http",
    )

    server.run(show_banner=True)
