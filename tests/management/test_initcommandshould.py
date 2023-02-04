import os

from assertpy import assert_that
from click.testing import CliRunner

from elementalcms.core import MongoDbContext
from elementalcms.management import cli
from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState


class TestInitCommandShould:

    def test_fail_when_config_file_does_not_exist(self):
        runner = CliRunner()
        # noinspection PyTypeChecker
        with runner.isolated_filesystem():
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['init', '-c', 'settings/default.json'])
            assert_that(result.output).contains('settings/default.json does not exist.')

    def test_create_default_folder_structure(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    runner.invoke(cli, ['init', '-c', 'settings/default.json'])
                    [assert_that(folder).exists() for folder in ['media',
                                                                 'static',
                                                                 'templates',
                                                                 'workspace',
                                                                 os.path.join('workspace', 'global_deps'),
                                                                 os.path.join('workspace', 'snippets'),
                                                                 os.path.join('workspace', 'pages'),
                                                                 '.elemental']]

    def test_display_success_feedback(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['init', '--with-config-file', 'settings/default.json'])
                    assert_that(result.output).contains('Initialization completed...')
