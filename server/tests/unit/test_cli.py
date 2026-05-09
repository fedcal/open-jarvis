"""Unit tests for the `jarvis` CLI entrypoint."""

from __future__ import annotations

import pytest

from jarvis_server import __version__
from jarvis_server.cli import main


@pytest.mark.unit
def test_cli_version_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["version"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert __version__ in captured.out


@pytest.mark.unit
def test_cli_no_args_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert __version__ in captured.out


@pytest.mark.unit
def test_cli_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out
