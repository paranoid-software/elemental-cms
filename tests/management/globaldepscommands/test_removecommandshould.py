import datetime
import json
import os
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext
from elementalcms.management import cli

from tests import EphemeralMongoContext
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestRemoveCommandShould:

    def test_fail_when_dependency_does_not_exist(self, debug_settings_fixture: dict):
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as db_name:
            debug_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli,
                                       [
                                           'global-deps',
                                           'remove',
                                           '-d', 'jquery', 'application/javascript'
                                       ])
                assert_that(result.output).contains('does not exist.')

    def test_show_operation_success_message(self, debug_settings_fixture: dict):
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='global_deps',
                                                            items=[{
                                                                '_id': ObjectId(),
                                                                'order': 0,
                                                                'name': 'jquery',
                                                                'type': 'application/javascript',
                                                                'url': '',
                                                                'meta': {},
                                                                'createdAt': datetime.datetime.utcnow(),
                                                                'lastModifiedAt': datetime.datetime.utcnow()
                                                            }])
                                       ])
                                   ]) as db_name:
            debug_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli,
                                       [
                                           'global-deps',
                                           'remove',
                                           '-d', 'jquery', 'application/javascript'
                                       ])
                assert_that(result.output).contains('removed successfully.')

    def test_crate_backup_file(self, debug_settings_fixture: dict):
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='global_deps',
                                                            items=[{
                                                                '_id': ObjectId(),
                                                                'order': 0,
                                                                'name': 'jquery',
                                                                'type': 'application/javascript',
                                                                'url': '',
                                                                'meta': {},
                                                                'createdAt': datetime.datetime.utcnow(),
                                                                'lastModifiedAt': datetime.datetime.utcnow()
                                                            }])
                                       ])
                                   ]) as db_name:
            debug_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli,
                                       [
                                           'global-deps',
                                           'remove',
                                           '-d', 'jquery', 'application/javascript'
                                       ],
                                       standalone_mode=False)
                assert_that(result.return_value).is_not_none()
                assert_that(result.return_value).exists()
