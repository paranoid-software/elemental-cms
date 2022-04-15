import json
import os

from assertpy import assert_that
from click.testing import CliRunner
from elementalcms.management import cli
from tests import EphemeralGcsContext
from tests.ephemeralgcscontext import GcsState


class TestPushCommandShould:

    def test_fail_when_no_media_bucket_setting_found(self, missing_gcs_buckets_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(missing_gcs_buckets_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['media', 'push', '*'])
            assert_that(result.output).contains('MEDIA_BUCKET parameter not found on current settings.')

    def test_exit_early_when_no_files_found_by_specified_pattern(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            os.makedirs('media')
            with open('media/push-media-test.txt', 'w') as f:
                f.write('Hi stranger, I am a media file.')
            pattern = '*.jpg'
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['media', 'push', pattern])
            assert_that(result.output).contains(f'We found 0 files for the search pattern {pattern}')

    def test_upload_media_files_to_media_bucket(self, default_settings_fixture):
        with EphemeralGcsContext(initial_state=[
            GcsState(default_settings_fixture['cmsCoreContext']['MEDIA_BUCKET'])
        ]) as bucket_name:
            default_settings_fixture['cmsCoreContext']['MEDIA_BUCKET'] = bucket_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                os.makedirs('media')
                with open('media/push-media-test.txt', 'w') as f:
                    f.write('Hi stranger, I am a media file.')
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['media', 'push', '*.*'])
                assert_that(result.output).contains('media/push-media-test.txt pushed successfully.')
