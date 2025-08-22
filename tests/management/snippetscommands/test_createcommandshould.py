from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.core import FlaskContext
from elementalcms.management import cli
from tests import EphemeralElementalFileSystem


class TestCreateCommandShould:

    def test_fail_when_name_has_uppercase(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                result = runner.invoke(cli, ['snippets', 'create', '-s', 'Header'])
                assert_that(result.output).contains('Snippet name must be lowercase')

    def test_fail_when_name_starts_with_number(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                result = runner.invoke(cli, ['snippets', 'create', '-s', '1header'])
                assert_that(result.output).contains('Snippet name cannot start with a number')

    def test_fail_when_name_has_invalid_chars(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                result = runner.invoke(cli, ['snippets', 'create', '-s', 'header@nav'])
                assert_that(result.output).contains('Snippet name can only contain letters, numbers and hyphens')

    def test_fail_when_spec_file_already_exist(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            folder_path = FlaskContext(default_settings_fixture['cmsCoreContext']).SNIPPETS_FOLDER
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, [
                (f'{folder_path}/nav-bar.json', '{}')
            ]):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'create',
                                             '-s', 'nav-bar'])
                assert_that(result.output).contains('nav-bar snippet already exist')

    def test_create_snippet_spec_file(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                # noinspection PyTypeChecker
                runner.invoke(cli, ['snippets',
                                    'create',
                                    '-s', 'footer'])
                assert_that(f'{folder_path}/footer.json').exists()

    def test_create_snippet_content_file(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                # noinspection PyTypeChecker
                runner.invoke(cli, ['snippets',
                                    'create',
                                    '-s', 'footer'])
                assert_that(f'{folder_path}/footer.html').exists()

    def test_display_success_feedback_message(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'create',
                                             '-s', 'footer'])
                assert_that(result.output).contains('footer.json|html files has been created successfully.')
