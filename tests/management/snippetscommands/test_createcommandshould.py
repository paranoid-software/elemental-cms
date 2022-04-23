import json
import os
from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.core import FlaskContext
from elementalcms.management import cli


class TestCreateCommandShould:

    def test_fail_when_spec_file_already_exist(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            folder_path = FlaskContext(default_settings_fixture['cmsCoreContext']).SNIPPETS_FOLDER
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            spec_file_path = f'{folder_path}/nav-bar.json'
            with open(spec_file_path, 'x') as s:
                s.write('...')
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['snippets',
                                         'create',
                                         '-s', 'nav-bar'])
            assert_that(result.output).contains('already exist')

    def test_create_spec_file_for_the_new_snippet(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
            # noinspection PyTypeChecker
            runner.invoke(cli, ['snippets',
                                'create',
                                '-s', 'footer'])
            assert_that(f'{folder_path}/footer.json').exists()
