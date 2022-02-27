import datetime
import json
import os
import re
from assertpy import assert_that
from bson import ObjectId, json_util
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli

from tests import EphemeralMongoContext
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPushAllCommandShould:

    def test_show_empty_folder_feedback(self, debug_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as db_name:
            debug_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--all'])
                assert_that(result.output).contains('There are no global dependencies to push.')

    def test_push_every_global_dependency(self, debug_settings_fixture):
        specs = [{
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
                }, {
                    '_id': ObjectId(),
                    'order': 0,
                    'name': 'plugster-ui',
                    'type': 'module',
                    'url': '',
                    'meta': {},
                    'createdAt': datetime.datetime.utcnow(),
                    'lastModifiedAt': datetime.datetime.utcnow()
                }]
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as db_name:
            debug_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                root_folder_path = FlaskContext(debug_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
                for spec in specs:
                    name = spec['name']
                    _type = spec['type']
                    type_folder_name = _type.replace('/', '_')
                    folder_path = f'{root_folder_path}/{type_folder_name}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    spec_file_path = f'{folder_path}/{name}.json'
                    with open(spec_file_path, 'x') as s:
                        s.write(json_util.dumps(spec))
                result = runner.invoke(cli, ['global-deps',
                                             'push',
                                             '--all'])
                total_specs = len(specs)
                assert_that(re.findall('pushed successfully', result.output)).is_length(total_specs)
