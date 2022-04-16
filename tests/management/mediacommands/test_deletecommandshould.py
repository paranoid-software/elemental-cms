import json
import os

from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.management import cli
from tests import EphemeralGcsContext
from tests.ephemeralgcscontext import GcsState


class TestDeleteCommandShould:

    def test_remove_remote_file(self, default_settings_fixture):
        file_names_list = [
            'readme.md'
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
                result = runner.invoke(cli, ['media', 'delete', 'readme.md'])
                assert_that(result.output).contains('readme.md removed successfuly.')
