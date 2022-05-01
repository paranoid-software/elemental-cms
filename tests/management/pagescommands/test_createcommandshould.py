from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.core import FlaskContext
from elementalcms.management import cli
from tests import EphemeralElementalFileSystem


class TestCreateCommandShould:

    def test_fail_when_language_is_not_supported(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['pages',
                                             'create',
                                             '-p', 'home', 'ru'])
                assert_that(result.output).contains('language is not supported')

    def test_fail_when_spec_file_already_exist(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            root_folder_path = FlaskContext(default_settings_fixture['cmsCoreContext']).PAGES_FOLDER
            folder_path = f'{root_folder_path}/en'
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, [
                (f'{folder_path}/home.json', '...')
            ]):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['pages',
                                             'create',
                                             '-p', 'home', 'en'])
                assert_that(result.output).contains('already exist')

    def test_create_page_spec_file(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                runner.invoke(cli, ['pages',
                                    'create',
                                    '--page', 'home', 'en'])
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
                folder_path = f'{root_folder_path}/en'
                assert_that(f'{folder_path}/home.json').exists()

    def test_create_page_content_file(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                runner.invoke(cli, ['pages',
                                    'create',
                                    '--page', 'home', 'en'])
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
                folder_path = f'{root_folder_path}/en'
                assert_that(f'{folder_path}/home.html').exists()

    def test_display_success_feedback_message(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['pages',
                                             'create',
                                             '--page', 'home', 'en'])
                assert_that(result.output).contains('home.json|html files has been created successfully.')
