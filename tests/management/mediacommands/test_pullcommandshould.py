import json
import os
from click.testing import CliRunner
from elementalcms.management import cli


class TestPullCommandShould:

    def test_fail_when_first_invoked(self, prod_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(prod_settings_fixture))
            os.makedirs('media')
            # noinspection PyTypeChecker
            # result = runner.invoke(cli, ['--no-debug', 'media', 'pull', '--all'])
            result = runner.invoke(cli, ['--no-debug', 'media', 'pull', '--folder', 'default/test/'])
            print(f'\n{result.output}')
            assert 'push' in result.output
