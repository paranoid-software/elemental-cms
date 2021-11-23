import json
import os

from click.testing import CliRunner
from elementalcms.management import cli


class TestVersionCommandShould:

    def test_show_current_version(self, debug_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(debug_settings_fixture))
            result = runner.invoke(cli, ['version'])
            assert result.exit_code == 0
