import json
import os

from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.core import MongoDbContext
from elementalcms.management import cli
from tests import EphemeralMongoContext
from tests.ephemeralmongocontext import MongoDbState


class TestInitCommandShould:

    def test_exit_early_when_project_is_already_initialized(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            with open('.elemental', 'w') as e:
                e.write('{}')
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['init'])
            assert_that(result.output).contains('Elemental CMS has been already initialized.')

    def test_create_default_folder_structure(self, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as db_name:
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                runner.invoke(cli, ['init'])
                app_name = default_settings_fixture['cmsCoreContext']['APP_NAME']
                [assert_that(folder).exists() for folder in ['media',
                                                             'static',
                                                             f'static/{app_name}',
                                                             'templates',
                                                             'workspace',
                                                             'workspace/global_deps',
                                                             'workspace/snippets',
                                                             'workspace/pages',
                                                             '.elemental']]

    def test_display_success_feedback(self, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as db_name:
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['init'])
                assert_that(result.output).contains('Initialization completed...')
