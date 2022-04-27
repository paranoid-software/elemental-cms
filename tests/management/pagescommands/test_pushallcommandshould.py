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
            'name': 'home',
            'language': 'en',
            'title': 'Home',
            'description': '',
            'isHome': True,
            'requiresUserIdentity': False,
            'redirectUsersTo': '',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'home',
            'language': 'es',
            'title': 'Inicio',
            'description': '',
            'isHome': True,
            'requiresUserIdentity': False,
            'redirectUsersTo': '',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'privacy-policy',
            'language': 'en',
            'title': 'Privacy policy',
            'description': '',
            'isHome': True,
            'requiresUserIdentity': False,
            'redirectUsersTo': '',
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
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['pages',
                                             'push',
                                             '--all'])
                assert_that(result.output).contains('There are no pages to push.')

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
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
                for spec in specs:
                    folder_path = f'{root_folder_path}/{spec["language"]}'
                    os.makedirs(folder_path, exist_ok=True)
                    name = spec['name']
                    spec_filepath = f'{folder_path}/{name}.json'
                    content_filepath = f'{folder_path}/{name}.html'
                    with open(spec_filepath, 'w') as s:
                        s.write(json_util.dumps(spec))
                    with open(content_filepath, 'w') as s:
                        s.write('<div></div>')
                # noinspection PyTypeChecker
                runner.invoke(cli, ['pages',
                                    'push',
                                    '--all'])
                assert_that(reader.count('drafts')).is_equal_to(len(specs))
