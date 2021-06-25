"""Test ``runway envvars``."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from click.testing import CliRunner
from mock import Mock

from runway._cli import cli

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import LogCaptureFixture, MonkeyPatch

    from ...conftest import CpConfigTypeDef

POSIX_OUTPUT = (
    'export TEST_VAR_01="deployment_1"\n'
    'export TEST_VAR_SHARED="deployment_2"\n'
    'export TEST_VAR_02="deployment_2"\n'
)
PSH_OUTPUT = (
    '$env:TEST_VAR_01 = "deployment_1"\n'
    '$env:TEST_VAR_SHARED = "deployment_2"\n'
    '$env:TEST_VAR_02 = "deployment_2"\n'
)


def test_envvars(
    cd_tmp_path: Path, cp_config: CpConfigTypeDef, monkeypatch: MonkeyPatch
) -> None:
    """Test envvars."""
    monkeypatch.setattr("platform.system", Mock(return_value="Darwin"))
    cp_config("simple_env_vars", cd_tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["envvars"])
    assert result.exit_code == 0
    assert result.output == POSIX_OUTPUT


def test_envvar_windows(
    cd_tmp_path: Path, cp_config: CpConfigTypeDef, monkeypatch: MonkeyPatch
) -> None:
    """Test envvars for Windows."""
    monkeypatch.setattr("platform.system", Mock(return_value="Windows"))
    monkeypatch.delenv("MSYSTEM", raising=False)
    cp_config("simple_env_vars", cd_tmp_path)
    runner = CliRunner()
    result0 = runner.invoke(cli, ["envvars"])
    assert result0.exit_code == 0
    assert result0.output == PSH_OUTPUT

    monkeypatch.setenv("MSYSTEM", "MINGW")
    result1 = runner.invoke(cli, ["envvars"])
    assert result1.output == POSIX_OUTPUT


def test_envvars_no_config(caplog: LogCaptureFixture, cd_tmp_path: Path) -> None:
    """Test envvars with no config in the directory or parent."""
    caplog.set_level(logging.ERROR, logger="runway")
    runner = CliRunner()
    result = runner.invoke(cli, ["envvars"])
    assert result.exit_code == 1

    template = (
        "config file not found at path {path}; looking for one of "
        "['runway.yml', 'runway.yaml']"
    )
    assert template.format(path=cd_tmp_path) in caplog.messages


def test_envvars_no_env_vars(
    caplog: LogCaptureFixture, cd_tmp_path: Path, cp_config: CpConfigTypeDef
) -> None:
    """Test envvars with no env_vars in the config."""
    caplog.set_level(logging.ERROR, logger="runway")
    cp_config("min_required", cd_tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["envvars"])
    assert result.exit_code == 1
    assert (
        "No env_vars defined in %s" % str(cd_tmp_path / "runway.yml") in caplog.messages
    )
