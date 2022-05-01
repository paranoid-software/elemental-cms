import json
import os

from assertpy import assert_that
from click.testing import CliRunner
from elementalcms.management import cli
from tests import EphemeralGcsContext, EphemeralElementalFileSystem
from tests.ephemeralgcscontext import GcsState


class TestPullCommandShould:

    def test_create_local_media_files(self, default_elemental_fixture, default_settings_fixture):
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
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    runner.invoke(cli, ['media', 'pull', '--all'])
                    media_folder = default_settings_fixture["cmsCoreContext"]["MEDIA_FOLDER"]
                    [assert_that(os.path.join(media_folder, file_name)).exists() for file_name in file_names_list]
