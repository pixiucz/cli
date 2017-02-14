import pytest
from click.testing import CliRunner
from pixiu import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_initialize(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'october'
