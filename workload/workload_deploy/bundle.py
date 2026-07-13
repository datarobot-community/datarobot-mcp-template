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

import re
from pathlib import Path

EXCLUDE_PATTERNS = [
    re.compile(p)
    for p in [
        r".*tests/.*",
        r".*\.coverage",
        r".*coverage\.xml",
        r".*htmlcov/.*",
        r".*\.env$",
        r".*\.DS_Store",
        r".*\.pyc$",
        r".*\.pyo$",
        r".*\.ruff_cache/.*",
        r".*\.venv/.*",
        r".*\.mypy_cache/.*",
        r".*__pycache__/.*",
        r".*\.pytest_cache/.*",
        r".*\.git/.*",
        r".*\.md$",
    ]
]

# Source globs pulled from dr_mcp/ into the bundle root.
_INCLUDE = ["app", "pyproject.toml", "uv.lock"]


def _excluded(arcname: str) -> bool:
    return any(p.match(arcname) for p in EXCLUDE_PATTERNS)


def assemble_bundle(dr_mcp_dir, dockerfile_path) -> list[tuple[str, bytes]]:
    root = Path(dr_mcp_dir)
    files: list[tuple[str, bytes]] = []
    for item in _INCLUDE:
        src = root / item
        if src.is_file():
            arc = item
            if not _excluded(arc):
                files.append((arc, src.read_bytes()))
        elif src.is_dir():
            for f in sorted(src.rglob("*")):
                if not f.is_file():
                    continue
                arc = str(f.relative_to(root))
                if not _excluded(arc):
                    files.append((arc, f.read_bytes()))
    # Dockerfile always lands at bundle root as "Dockerfile".
    df = Path(dockerfile_path)
    if not df.is_file():
        raise FileNotFoundError(f"Dockerfile not found: {df}")
    files.append(("Dockerfile", df.read_bytes()))

    names = {a for a, _ in files}
    for required in ("Dockerfile", "uv.lock"):
        if required not in names:
            raise FileNotFoundError(
                f"bundle missing required file '{required}' (needed by the image build)"
            )
    return files
