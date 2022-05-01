import datetime
import os
import re
import pytest
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli
from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPullCommandShould:

    @pytest.fixture
    def deps(self):
        return [{
            '_id': ObjectId(),
            'order': 0,
            'name': 'jquery',
            'type': 'application/javascript',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'order': 0,
            'name': 'jquery-ui',
            'type': 'text/css',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_display_2_unsuccessful_pull_operations_feedback_message(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['global-deps',
                                                 'pull',
                                                 '-d', 'dep-one', 'module',
                                                 '-d', 'dep-two', 'application/javascript'])
                    assert_that(re.findall('does not exist', result.output)).is_length(2)

    def test_create_spec_file_for_pulled_dependencies(self, deps, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='global_deps',
                                                            items=deps)
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    name = 'jquery'
                    _type = 'application/javascript'
                    # noinspection PyTypeChecker
                    runner.invoke(cli, ['global-deps',
                                        'pull',
                                        '-d', name, _type])
                    folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
                    assert_that(f'{folder_path}/{_type.replace("/", "_")}/{name}.json').exists()

    def test_create_backup_file_for_pulled_dependency(self, default_elemental_fixture, default_settings_fixture, deps):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='global_deps',
                                                            items=deps)
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                name = 'jquery-ui'
                _type = 'text/css'
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
                type_folder_name = _type.replace('/', '_')
                folder_path = f'{root_folder_path}/{type_folder_name}'
                os.makedirs(folder_path)
                spec_filepath = f'{folder_path}/{name}.json'
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, [
                        (spec_filepath, '...')
                ]):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli,
                                           [
                                               'global-deps',
                                               'pull',
                                               '-d', name, _type
                                           ],
                                           standalone_mode=False)

                    assert_that(result.return_value[0]).exists()

    def test_display_1_successful_pull_operation_feedback_message(self, default_elemental_fixture, default_settings_fixture, deps):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='global_deps',
                                                            items=deps)
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['global-deps',
                                                 'pull',
                                                 '-d', 'jquery', 'application/javascript'])
                    assert_that(re.findall('pulled successfully', result.output)).is_length(1)
