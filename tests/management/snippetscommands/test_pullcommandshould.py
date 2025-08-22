import datetime
import json
import os
import re
import pytest
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli
from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPullCommandShould:

    @pytest.fixture
    def snippets(self):
        return [{
            '_id': ObjectId(),
            'name': 'nav-bar',
            'content': '<div></div>',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'footer',
            'content': '<div></div>',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_display_2_unsuccessful_pull_operations_feedback_message(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets',
                                                 'pull',
                                                 '-s', 'workspace/snippets/snippet-one',
                                                 '-s', 'folder1/snippet-two'])
                    assert_that(re.findall('does not exist', result.output)).is_length(2)

    def test_create_spec_for_pulled_snippets(self, default_elemental_fixture, default_settings_fixture, snippets):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='snippets',
                                                                         items=snippets)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    runner.invoke(cli, ['snippets',
                                        'pull',
                                        '-s', 'nav-bar',
                                        '-s', 'footer'])
                    folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                    [assert_that(f'{folder_path}/{snippet["name"]}.json').exists() for snippet in snippets]

    def test_create_backup_file_for_pulled_snippet(self, default_elemental_fixture, default_settings_fixture, snippets):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='snippets',
                                                            items=snippets)
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, [
                    (f'{folder_path}/nav-bar.json', '{}'),
                    (f'{folder_path}/nav-bar.html', '<div></div>')
                ]):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli,
                                           [
                                               'snippets',
                                               'pull',
                                               '-s', 'nav-bar'
                                           ],
                                           standalone_mode=False)

                    assert_that(result.return_value[0][0]).exists()
                    assert_that(result.return_value[0][1]).exists()

    def test_display_1_successful_pull_operation_feedback_message(self,
                                                                  default_elemental_fixture,
                                                                  default_settings_fixture,
                                                                  snippets):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='snippets',
                                                            items=snippets)
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets',
                                                 'pull',
                                                 '-s', 'workspace/snippets/footer'])
                    assert_that(re.findall('pulled successfully', result.output)).is_length(1)
