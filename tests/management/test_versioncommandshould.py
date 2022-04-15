import json
import os

from click.testing import CliRunner
from elementalcms.management import cli


class TestVersionCommandShould:

    def test_display_current_version(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['version'])
            assert result.exit_code == 0
