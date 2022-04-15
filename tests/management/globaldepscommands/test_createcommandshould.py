import json
import os
from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.core import FlaskContext
from elementalcms.management import cli


class TestCreateCommandShould:

    def test_fail_when_type_is_not_supported(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['global-deps',
                                         'create',
                                         '-d', 'dep-one', 'unsupported-type'])
            assert_that(result.output).contains('type is not supported.')

    def test_fail_when_spec_file_already_exist(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            name = 'jquery'
            _type = 'application/javascript'
            root_folder_path = FlaskContext(default_settings_fixture['cmsCoreContext']).GLOBAL_DEPS_FOLDER
            type_folder_name = _type.replace('/', '_')
            folder_path = f'{root_folder_path}/{type_folder_name}'
            if not os.path.exists(f'{folder_path}'):
                os.makedirs(f'{folder_path}')
            spec_file_path = f'{folder_path}/{name}.json'
            with open(spec_file_path, 'x') as s:
                s.write('...')
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['global-deps',
                                         'create',
                                         '-d', name, _type])
            assert_that(result.output).contains('already exist.')

    def test_create_spec_file_for_new_global_dependency(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            name = 'jquery'
            _type = 'application/javascript'
            root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
            type_folder_name = _type.replace('/', '_')
            folder_path = f'{root_folder_path}/{type_folder_name}'
            # noinspection PyTypeChecker
            runner.invoke(cli, ['global-deps',
                                'create',
                                '-d', name, _type])
            assert_that(f'{folder_path}/{name}.json').exists()
