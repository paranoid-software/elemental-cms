from assertpy import assert_that
from click.testing import CliRunner
from elementalcms.management import cli


class TestVersionCommandShould:

    def test_display_current_version(self, default_settings_fixture):
        runner = CliRunner()
        # noinspection PyTypeChecker
        result = runner.invoke(cli, ['version'])
        assert_that(result.output).contains('.')
