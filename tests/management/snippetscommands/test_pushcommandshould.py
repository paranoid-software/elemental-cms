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

    def test_fail_when_spec_file_is_missing(self, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['snippets',
                                         'push',
                                         '-s', 'nav-bar'])
            assert_that(result.output).contains('There is no spec file for nav-bar snippet.')

    def test_fail_when_content_file_is_missing(self, specs, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/prod.json', 'w') as f:
                f.write(json.dumps(default_settings_fixture))
            folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
            os.makedirs(folder_path)
            for spec in specs:
                with open(f'{folder_path}/{spec["name"]}.json', 'w') as f:
                    f.write(json_util.dumps(spec))
            # noinspection PyTypeChecker
            result = runner.invoke(cli, ['snippets',
                                         'push',
                                         '-s', 'nav-bar'])
            assert_that(result.output).contains('There is no content file for nav-bar snippet.')

    def test_display_2_success_feedback_messages(self, default_settings_fixture, specs):
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
                    with open(f'{folder_path}/{spec["name"]}.json', 'w') as f:
                        f.write(json_util.dumps(spec))
                    with open(f'{folder_path}/{spec["name"]}.html', 'w') as f:
                        f.write('<div></div>')
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'push',
                                             '-s', 'nav-bar', '-s', 'footer'])
                assert_that(re.findall('pushed successfully', result.output)).is_length(2)

    def test_create_backup_file_for_pushed_spec(self, specs, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='snippets',
                                                            items=[specs[1]])
                                       ])
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
                    with open(f'{folder_path}/{spec["name"]}.json', 'w') as f:
                        f.write(json_util.dumps(spec))
                    with open(f'{folder_path}/{spec["name"]}.html', 'w') as f:
                        f.write('<div></div>')
                # noinspection PyTypeChecker
                result = runner.invoke(cli,
                                       [
                                           'snippets',
                                           'push',
                                           '-s', 'footer'
                                       ],
                                       standalone_mode=False)
                assert_that(result.return_value).is_length(1)
                assert_that(result.return_value[0][0]).exists()
                assert_that(result.return_value[0][1]).exists()
