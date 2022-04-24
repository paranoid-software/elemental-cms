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
from tests.ephemeralmongocontext import MongoDbState


class TestPushAllCommandShould:

    @pytest.fixture
    def specs(self):
        return [{
            '_id': ObjectId(),
            'name': 'nav-bar',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'footer',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_display_empty_folder_feedback(self, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as db_name:
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'push',
                                             '--all'])
                assert_that(result.output).contains('There are no snippets to push.')

    def test_push_current_specs(self, specs, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as db_name:
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                os.makedirs(folder_path)
                for spec in specs:
                    name = spec['name']
                    spec_file_path = f'{folder_path}/{name}.json'
                    content_file_path = f'{folder_path}/{name}.html'
                    with open(spec_file_path, 'x') as s:
                        s.write(json_util.dumps(spec))
                    with open(content_file_path, 'x') as s:
                        s.write('<div></div>')
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'push',
                                             '--all'])
                total_specs = len(specs)
                assert_that(re.findall('pushed successfully', result.output)).is_length(total_specs)
