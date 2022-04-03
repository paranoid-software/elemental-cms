import datetime
import json
import os
import re

from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli
from tests import EphemeralMongoContext
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPullCommandShould:

    def test_fail_when_database_parameters_are_missing(self, debug_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]):
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'pull',
                                             '-d', 'jquery', 'application/javascript'])
                assert_that(result.exception).is_not_none()

    def test_show_2_unsuccessful_pull_operations_feedback_message(self, debug_settings_fixture):
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
                result = runner.invoke(cli, ['global-deps',
                                             'pull',
                                             '-d', 'dep-one', 'module',
                                             '-d', 'dep-two', 'application/javascript'])
                assert_that(re.findall('does not exist', result.output)).is_length(2)

    def test_show_1_successful_pull_operation_feedback_message(self, debug_settings_fixture: dict):
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
                result = runner.invoke(cli, ['global-deps',
                                             'pull',
                                             '-d', 'jquery', 'application/javascript'])
                assert_that(re.findall('pulled successfully', result.output)).is_length(1)

    def test_create_spec_file_for_pulled_item(self, debug_settings_fixture):
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
                name = 'jquery'
                _type = 'application/javascript'
                # noinspection PyTypeChecker
                runner.invoke(cli, ['global-deps',
                                    'pull',
                                    '-d', name, _type])
                root_folder_path = FlaskContext(debug_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
                type_folder_name = _type.replace('/', '_')
                folder_path = f'{root_folder_path}/{type_folder_name}'
                assert_that(f'{folder_path}/{name}.json').exists()

    def test_create_backup_file_for_pulled_item(self, debug_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='global_deps',
                                                            items=[{
                                                                '_id': ObjectId(),
                                                                'order': 0,
                                                                'name': 'jquery-ui',
                                                                'type': 'text/css',
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
                name = 'jquery-ui'
                _type = 'text/css'
                root_folder_path = FlaskContext(debug_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
                type_folder_name = _type.replace('/', '_')
                folder_path = f'{root_folder_path}/{type_folder_name}'
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                spec_file_path = f'{folder_path}/{name}.json'
                with open(spec_file_path, 'x') as s:
                    s.write('...')
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli,
                                       [
                                           'global-deps',
                                           'pull',
                                           '-d', name, _type
                                       ],
                                       standalone_mode=False)

                assert_that(result.return_value).is_length(1)
                assert_that(result.return_value[0]).exists()
