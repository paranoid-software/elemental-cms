import json
import os

from click import BaseCommand
from click.testing import CliRunner
from elementalcms.management import cli


class TestCollectCommandShould:

    def test_fail_when_no_static_bucket_setting_found(self, debug_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(debug_settings_fixture))
            result = runner.invoke(cli, ['static', 'collect'])
            assert 'STATIC_BUCKET parameter not found on current settings.' in result.output

    def test_updload_static_files_to_static_bucket(self, prod_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(prod_settings_fixture))
            os.makedirs('static')
            with open('static/collect-test.txt', 'w') as f:
                f.write('Hi stranger, I am a static file.')
            result = runner.invoke(cli, ['--no-debug', 'static', 'collect'])
            print(result.output)
            assert 'Uploading' in result.output
            assert 'Collect command excecuted successfully.' in result.output
