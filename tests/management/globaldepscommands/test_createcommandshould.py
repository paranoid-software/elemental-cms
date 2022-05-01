import os
from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.core import FlaskContext
from elementalcms.management import cli
from tests import EphemeralElementalFileSystem


class TestCreateCommandShould:

    def test_fail_when_type_is_not_supported(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'create',
                                             '-d', 'dep-one', 'unsupported-type'])
                assert_that(result.output).contains('type is not supported.')

    def test_fail_when_spec_file_already_exist(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                name = 'jquery'
                _type = 'application/javascript'
                root_folder_path = FlaskContext(default_settings_fixture['cmsCoreContext']).GLOBAL_DEPS_FOLDER
                type_folder_name = _type.replace('/', '_')
                folder_path = os.path.join(root_folder_path, type_folder_name)
                os.makedirs(folder_path, exist_ok=True)
                spec_filepath = os.path.join(folder_path, f'{name}.json')
                open(spec_filepath, 'w').write('...')
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'create',
                                             '-d', name, _type])
                assert_that(result.output).contains('already exist')

    def test_create_global_dependency_spec_file(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                name = 'jquery'
                _type = 'application/javascript'
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
                type_folder_name = _type.replace('/', '_')
                folder_path = os.path.join(root_folder_path, type_folder_name)
                # noinspection PyTypeChecker
                runner.invoke(cli, ['global-deps',
                                    'create',
                                    '-d', name, _type])
                assert_that(os.path.join(folder_path, f'{name}.json')).exists()

    def test_display_success_feedback_message(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'create',
                                             '-d', 'jquery', 'application/javascript'])
                assert_that(result.output).contains('file has been created successfully.')
