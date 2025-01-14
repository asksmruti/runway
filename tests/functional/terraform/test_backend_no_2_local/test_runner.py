"""Test migration from no backend to local backend."""
# pylint: disable=redefined-outer-name,unused-argument
from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Generator, cast

import pytest

from runway._cli import cli
from runway.env_mgr.tfenv import TF_VERSION_FILENAME

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest
    from click.testing import CliRunner, Result

CURRENT_DIR = Path(__file__).parent


@pytest.fixture(
    autouse=True,
    params=["0.11.15", "0.12.31", "0.13.7", "0.14.11", "0.15.5"],
    scope="module",
)
def tf_version(request: SubRequest) -> Generator[str, None, None]:
    """Set Terraform version."""
    file_path = CURRENT_DIR / TF_VERSION_FILENAME
    file_path.write_text(cast(str, request.param) + "\n")
    yield cast(str, request.param)
    file_path.unlink(missing_ok=True)  # pylint: disable=unexpected-keyword-arg


@pytest.fixture(scope="function")
def deploy_local_backend_result(
    cli_runner: CliRunner,
    local_backend: Path,
    tf_version: str,
) -> Generator[Result, None, None]:
    """Execute `runway deploy` with `runway destory` as a cleanup step."""
    assert (CURRENT_DIR / "terraform.tfstate.d").exists()
    yield cli_runner.invoke(cli, ["deploy"], env={"CI": "1"})
    # cleanup files
    shutil.rmtree(CURRENT_DIR / ".runway", ignore_errors=True)
    shutil.rmtree(CURRENT_DIR / ".terraform", ignore_errors=True)
    shutil.rmtree(CURRENT_DIR / "terraform.tfstate.d", ignore_errors=True)
    # pylint: disable=unexpected-keyword-arg
    (CURRENT_DIR / ".terraform.lock.hcl").unlink(missing_ok=True)


@pytest.fixture(scope="function")
def deploy_no_backend_result(
    cli_runner: CliRunner,
    no_backend: Path,
    tf_version: str,
) -> Generator[Result, None, None]:
    """Execute `runway deploy` with `runway destory` as a cleanup step."""
    yield cli_runner.invoke(cli, ["deploy"], env={"CI": "1"})


def test_deploy_no_backend_result(deploy_no_backend_result: Result) -> None:
    """Test deploy no backend result."""
    assert deploy_no_backend_result.exit_code == 0


def test_deploy_local_backend_result(deploy_local_backend_result: Result) -> None:
    """Test deploy local backend result."""
    # currently, this is expected to fail - Terraform prompts for user confirmation
    assert deploy_local_backend_result.exit_code != 0
