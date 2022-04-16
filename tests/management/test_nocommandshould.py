import json
import os

from click.testing import CliRunner
from elementalcms.management import cli


class TestNoCommandShould:

    def test_display_commands_list(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, [])
            assert 'Commands:' in result.output
            assert 'global-deps' in result.output
            assert 'init' in result.output
            assert 'media' in result.output
            assert 'pages' in result.output
            assert 'snippets' in result.output
            assert 'static' in result.output
            assert 'version' in result.output
