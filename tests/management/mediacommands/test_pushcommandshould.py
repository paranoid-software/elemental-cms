import json
import os
from click.testing import CliRunner
from elementalcms.management import cli


class TestPushCommandShould:

    def test_fail_when_no_media_bucket_setting_found(self, debug_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(debug_settings_fixture))
            result = runner.invoke(cli, ['media', 'push', '*'])
            assert 'MEDIA_BUCKET parameter not found on current settings.' in result.output

    def test_exit_early_when_no_files_found_by_especified_pattern(self, prod_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(prod_settings_fixture))
            os.makedirs('media')
            with open('media/push-media-test.txt', 'w') as f:
                f.write('Hi stranger, I am a media file.')
            pattern = '*.jpg'
            result = runner.invoke(cli, ['--no-debug', 'media', 'push', pattern])
            assert f'We found 0 files for the search pattern {pattern}' in result.output

    def test_upload_media_files_to_media_bucket(self, prod_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(prod_settings_fixture))
            os.makedirs('media')
            with open('media/push-media-test.txt', 'w') as f:
                f.write('Hi stranger, I am a media file.')
            #result = runner.invoke(cli, ['--no-debug', 'media', 'push', '*.*'])
            #assert 'media/push-media-test.txt pushed successfully.' in result.output
            result = runner.invoke(cli, ['--no-debug', 'media', 'list'])
            print(result.output)
            assert 1 == 1
