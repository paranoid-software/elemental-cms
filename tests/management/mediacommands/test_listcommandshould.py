import json
import os

from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.management import cli
from tests import EphemeralGcsContext
from tests.ephemeralgcscontext import GcsState


class TestListCommandShould:

    def test_fail_when_no_media_bucket_setting_found(self, missing_gcs_buckets_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(missing_gcs_buckets_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['media', 'list'])
            assert_that(result.output).contains('MEDIA_BUCKET parameter not found on current settings.')

    def test_fail_when_path_argument_is_missing(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['media', 'list', ''])
            assert_that(result.output).contains('Empty string is not a valid list command argument')

    def test_display_complete_media_files_list(self, default_settings_fixture):
        file_names_list = [
            'default/my-json-file.json',
            'default/image.jpg'
        ]
        with EphemeralGcsContext(initial_state=[
            GcsState(default_settings_fixture['cmsCoreContext']['MEDIA_BUCKET'],
                     file_names_list)
        ]) as bucket_name:
            default_settings_fixture['cmsCoreContext']['MEDIA_BUCKET'] = bucket_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['media', 'list'])
                [assert_that(result.output).contains(file_name) for file_name in file_names_list]

    def test_display_folder_files_list(self, default_settings_fixture):
        default_folder_file_names_list = [
            'default/my-json-file.json',
            'default/image.jpg'
        ]
        with EphemeralGcsContext(initial_state=[
            GcsState(default_settings_fixture['cmsCoreContext']['MEDIA_BUCKET'],
                     default_folder_file_names_list +
                     [
                         'default/docs/profile.txt',
                         'test/another-file.txt'
                     ])
        ]) as bucket_name:
            default_settings_fixture['cmsCoreContext']['MEDIA_BUCKET'] = bucket_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['media', 'list', 'default/'])
                [assert_that(result.output).contains(file_name) for file_name in default_folder_file_names_list]
