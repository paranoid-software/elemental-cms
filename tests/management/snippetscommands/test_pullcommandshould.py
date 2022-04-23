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

    def test_display_2_unsuccessful_pull_operations_feedback_message(self, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as db_name:
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'pull',
                                             '-s', 'snippet-one',
                                             '-s', 'snippet-two'])
                assert_that(re.findall('does not exist', result.output)).is_length(2)

    def test_create_backup_file_for_pulled_item(self, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='snippets',
                                                            items=[{
                                                                '_id': ObjectId(),
                                                                'name': 'nav-bar',
                                                                'content': '<div></div>',
                                                                'cssDeps': [],
                                                                'jsDeps': [],
                                                                'createdAt': datetime.datetime.utcnow(),
                                                                'lastModifiedAt': datetime.datetime.utcnow()
                                                            }])
                                       ])
                                   ]) as db_name:
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                name = 'nav-bar'
                folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                spec_file_path = f'{folder_path}/{name}.json'
                content_file_path = f'{folder_path}/{name}.html'
                with open(spec_file_path, 'x') as s:
                    s.write('...')
                with open(content_file_path, 'x') as s:
                    s.write('...')
                os.makedirs('settings')
                with open('settings/prod.json', 'w') as f:
                    f.write(json.dumps(default_settings_fixture))
                # noinspection PyTypeChecker
                result = runner.invoke(cli,
                                       [
                                           'snippets',
                                           'pull',
                                           '-s', name
                                       ],
                                       standalone_mode=False)

                assert_that(result.return_value).is_length(1)
                assert_that(result.return_value[0][0]).exists()
                assert_that(result.return_value[0][1]).exists()
