import datetime
import json
import os
import re
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext
from elementalcms.management import cli

from tests import EphemeralMongoContext
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPullAllCommandShould:

    def test_show_empty_repository_feedback(self, debug_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='global_deps',
                                                                         items=[])
                                                    ])
                                   ]) as db_name:
            debug_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                result = runner.invoke(cli, ['global-deps',
                                             'pull',
                                             '--all'])
                assert_that(result.output).contains('There are no global dependencies to pull.')

    def test_fetch_every_global_dependency(self, debug_settings_fixture):
        items = [{
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
                    'type': 'model',
                    'url': '',
                    'meta': {},
                    'createdAt': datetime.datetime.utcnow(),
                    'lastModifiedAt': datetime.datetime.utcnow()
                }]
        with EphemeralMongoContext(MongoDbContext(debug_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='global_deps',
                                                                         items=items)
                                                    ])
                                   ]) as db_name:
            debug_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/debug.json', 'w') as f:
                    f.write(json.dumps(debug_settings_fixture))
                result = runner.invoke(cli, ['global-deps',
                                             'pull',
                                             '--all'])
                total_items = len(items)
                assert_that(re.findall('pulled successfully', result.output)).is_length(total_items)
