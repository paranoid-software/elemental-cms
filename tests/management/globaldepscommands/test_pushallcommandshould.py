import datetime
import json
import os
import pytest
from assertpy import assert_that
from bson import ObjectId, json_util
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli

from tests import EphemeralMongoContext
from tests.ephemeralmongocontext import MongoDbState


class TestPushAllCommandShould:

    @pytest.fixture
    def specs(self):
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
            'order': 1,
            'name': 'semantic-ui',
            'type': 'text/css',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'order': 2,
            'name': 'slack',
            'type': 'module',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_display_empty_folder_feedback(self, default_settings_fixture):
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
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--all'])
                assert_that(result.output).contains('There are no global dependencies to push.')

    def test_push_current_specs(self, specs, default_settings_fixture):
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
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
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
                # noinspection PyTypeChecker
                runner.invoke(cli, ['global-deps',
                                    'push',
                                    '--all'])
                assert_that(reader.count('global_deps')).is_equal_to(len(specs))
