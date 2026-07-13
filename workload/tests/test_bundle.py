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

import pytest
from workload_deploy.bundle import assemble_bundle


def _write(tmp_path, rel, content=b"x"):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


def test_bundle_includes_required_files_and_excludes_junk(tmp_path):
    _write(tmp_path, "app/main.py", b"print('hi')")
    _write(tmp_path, "app/tools/user_tools.py")
    _write(tmp_path, "pyproject.toml")
    _write(tmp_path, "uv.lock")
    _write(tmp_path, "app/__pycache__/x.pyc")   # excluded
    _write(tmp_path, "app/tests/test_x.py")    # excluded
    df = _write(tmp_path, "docker/Dockerfile.workload", b"FROM base")
    names = {arc for arc, _ in assemble_bundle(tmp_path, df)}
    assert "Dockerfile" in names
    assert "uv.lock" in names
    assert "pyproject.toml" in names
    assert "app/main.py" in names
    assert "app/tools/user_tools.py" in names
    assert not any(n.endswith(".pyc") for n in names)
    assert "app/tests/test_x.py" not in names


def test_bundle_requires_uv_lock(tmp_path):
    _write(tmp_path, "app/main.py")
    _write(tmp_path, "pyproject.toml")
    df = _write(tmp_path, "docker/Dockerfile.workload", b"FROM base")
    with pytest.raises(FileNotFoundError):
        assemble_bundle(tmp_path, df)


def test_bundle_rewrites_base_image_arg(tmp_path):
    _write(tmp_path, "pyproject.toml")
    _write(tmp_path, "uv.lock")
    df = _write(
        tmp_path,
        "docker/Dockerfile.workload",
        b"ARG WORKLOAD_BASE_IMAGE=default/img:1\nFROM ${WORKLOAD_BASE_IMAGE}\n",
    )
    files = assemble_bundle(tmp_path, df, base_image="my/mirror:2")
    content = dict(files)["Dockerfile"]
    assert b"ARG WORKLOAD_BASE_IMAGE=my/mirror:2" in content
    assert b"default/img:1" not in content


def test_bundle_leaves_dockerfile_unchanged_when_base_image_none(tmp_path):
    _write(tmp_path, "pyproject.toml")
    _write(tmp_path, "uv.lock")
    original = b"ARG WORKLOAD_BASE_IMAGE=default/img:1\nFROM ${WORKLOAD_BASE_IMAGE}\n"
    df = _write(tmp_path, "docker/Dockerfile.workload", original)
    files = assemble_bundle(tmp_path, df, base_image=None)
    content = dict(files)["Dockerfile"]
    assert content == original
