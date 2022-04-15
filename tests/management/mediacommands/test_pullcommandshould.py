import json
import os

from assertpy import assert_that
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
            assert_that('media/default/test').exists()
