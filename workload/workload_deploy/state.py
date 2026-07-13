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

import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

STATE_PATH = Path(__file__).resolve().parent.parent / ".last_deploy.json"


def write_state(data: dict, path: Path = STATE_PATH) -> None:
    path.write_text(json.dumps(data, indent=2))


def read_state(path: Path = STATE_PATH) -> dict:
    if not path.is_file():
        raise FileNotFoundError(
            f"no deploy state at {path}; pass ids explicitly or run deployasworkload first"
        )
    return json.loads(path.read_text())


def mcp_url(endpoint: str, mount_path: str = "/mcp") -> str:
    parts = urlsplit(endpoint)
    new_path = parts.path.rstrip("/") + mount_path
    return urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))
