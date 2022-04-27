import datetime
import json
import os
import re
import pytest
from assertpy import assert_that
from bson import ObjectId, json_util
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli

from tests import EphemeralMongoContext
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPushCommandShould:

    @pytest.fixture
    def specs(self):
        return [{
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
        }, {
            '_id': '1',
            'order': 0,
            'name': 'calendar',
            'type': 'module',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    @staticmethod
    def spec_files_setup(specs, debug_settings_fixture):
        root_folder_path = FlaskContext(debug_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
        for spec in specs:
            name = spec['name']
            _type = spec['type']
            type_folder_name = _type.replace('/', '_')
            folder_path = f'{root_folder_path}/{type_folder_name}'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            spec_filepath = f'{folder_path}/{name}.json'
            with open(spec_filepath, 'w') as s:
                s.write(json_util.dumps(spec))
        with open(f'{root_folder_path}/module/invalid.json', 'w') as s:
            s.write('...')
        with open(f'{root_folder_path}/module/missing-name.json', 'w') as s:
            s.write(json_util.dumps({
                '_id': ObjectId(),
                'order': 0,
                'type': 'module',
                'url': '',
                'meta': {},
                'createdAt': datetime.datetime.utcnow(),
                'lastModifiedAt': datetime.datetime.utcnow()
            }))
        with open(f'{root_folder_path}/module/unmatched-name.json', 'w') as s:
            s.write(json_util.dumps({
                '_id': ObjectId(),
                'order': 0,
                'name': 'name',
                'type': 'module',
                'url': '',
                'meta': {},
                'createdAt': datetime.datetime.utcnow(),
                'lastModifiedAt': datetime.datetime.utcnow()
            }))

    def test_fail_when_type_is_not_supported(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['global-deps',
                                         'push',
                                         '-d', 'dep-one', 'unsupported-type'])
            assert_that(result.output).contains('type is not supported.')

    def test_fail_when_spec_file_is_missing(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['global-deps',
                                         'push',
                                         '-d', 'my-missing-css-dep', 'text/css'])
            assert_that(result.output).contains('There is no spec file for my-missing-css-dep (text/css).')

    def test_display_1_invalid_spec_feedback_message(self, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                self.spec_files_setup(specs, default_settings_fixture)
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--dep', 'invalid', 'module'])
                assert_that(re.findall('Invalid spec', result.output)).is_length(1)

    def test_display_1_missing_id_feedback_message(self, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                self.spec_files_setup(specs, default_settings_fixture)
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--dep', 'jquery', 'application/javascript'])
                assert_that(re.findall('Missing spec _id', result.output)).is_length(1)

    def test_display_1_invalid_id_feedback_message(self, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                self.spec_files_setup(specs, default_settings_fixture)
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--dep', 'calendar', 'module'])
                assert_that(re.findall('Invalid spec _id', result.output)).is_length(1)

    def test_display_1_missing_name_feedback_message(self, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                self.spec_files_setup(specs, default_settings_fixture)
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--dep', 'missing-name', 'module'])
                assert_that(re.findall('Missing spec name', result.output)).is_length(1)

    def test_display_1_invalid_name_feedback_message(self, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                self.spec_files_setup(specs, default_settings_fixture)
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--dep', 'unmatched-name', 'module'])
                assert_that(re.findall('Invalid spec name', result.output)).is_length(1)

    def test_display_1_success_feedback_message(self, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                self.spec_files_setup(specs, default_settings_fixture)
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--dep', 'jquery-ui', 'text/css'])
                assert_that(re.findall('pushed successfully', result.output)).is_length(1)

    def test_create_backup_file_for_pushed_dependency(self, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='global_deps',
                                                            items=[specs[1]])
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                self.spec_files_setup(specs, default_settings_fixture)
                name = 'jquery-ui'
                _type = 'text/css'
                # noinspection PyTypeChecker
                result = runner.invoke(cli,
                                       ['global-deps',
                                        'push',
                                        '-d', name, _type],
                                       standalone_mode=False)

                assert_that(result.return_value[0]).exists()
