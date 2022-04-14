import json
import os
from click.testing import CliRunner
from elementalcms.management import cli


class TestListCommandShould:

    def test_fail_when_no_media_bucket_setting_found(self, debug_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(debug_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['media', 'push', '*'])
            assert 'MEDIA_BUCKET parameter not found on current settings.' in result.output

    def test_display_complete_media_files_list(self, prod_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(prod_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['--no-debug', 'media', 'list', '*'])
            assert 'media files found at bucket' in result.output

    def test_display_path_media_files_list(self, prod_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(prod_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['--no-debug', 'media', 'list', 'default/'])
            print(result.output)
            assert 'media files found at default/' in result.output
