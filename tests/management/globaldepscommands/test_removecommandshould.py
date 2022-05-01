import datetime
import pytest
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext
from elementalcms.management import cli

from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestRemoveCommandShould:

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
        }]

    def test_fail_when_dependency_does_not_exist(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli,
                                           [
                                               'global-deps',
                                               'remove',
                                               '-d', 'jquery', 'application/javascript'
                                           ])
                    assert_that(result.output).contains('does not exist')

    def test_remove_dependency_from_repository(self, default_elemental_fixture, default_settings_fixture, deps):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='global_deps',
                                                                         items=deps)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    runner.invoke(cli, ['global-deps',
                                        'remove',
                                        '-d', 'jquery', 'application/javascript'])
                    assert_that(reader.find_one('global_deps', {'_id': deps[0].get('_id')})).is_none()

    def test_display_success_feedback_message(self, default_elemental_fixture, default_settings_fixture, deps):
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
                    result = runner.invoke(cli,
                                           ['global-deps',
                                            'remove',
                                            '-d', 'jquery', 'application/javascript'])
                    assert_that(result.output).contains('removed successfully.')

    def test_create_backup_file_for_removed_dependency(self, default_elemental_fixture, default_settings_fixture, deps):
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
                    result = runner.invoke(cli,
                                           [
                                               'global-deps',
                                               'remove',
                                               '-d', 'jquery', 'application/javascript'
                                           ],
                                           standalone_mode=False)

                    assert_that(result.return_value).exists()
