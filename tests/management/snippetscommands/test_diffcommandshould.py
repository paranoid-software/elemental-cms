import datetime
import pytest
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner
from bson import json_util

from elementalcms.core import MongoDbContext
from elementalcms.management import cli
from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestDiffCommandShould:

    @pytest.fixture
    def snippet(self):
        return {
            '_id': ObjectId(),
            'name': 'nav-bar',
            'content': '<div>Original</div>',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }

    def test_show_error_when_snippet_not_in_db(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='snippets',
                                                                         items=[])
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'diff', '-s', 'nav-bar'])
                    assert_that(result.output).contains('Snippet nav-bar not found in database.')

    def test_show_error_when_no_local_files(self, default_elemental_fixture, default_settings_fixture, snippet):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='snippets',
                                                                         items=[snippet])
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'diff', '-s', 'nav-bar'])
                    assert_that(result.output).contains('No local files found for snippet nav-bar.')

    def test_show_no_differences_when_files_match(self, default_elemental_fixture, default_settings_fixture, snippet):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='snippets',
                                                                         items=[snippet])
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                folder_path = default_settings_fixture["cmsCoreContext"]["SNIPPETS_FOLDER"]
                files = [
                    (f'{folder_path}/nav-bar.json', json_util.dumps(snippet)),
                    (f'{folder_path}/nav-bar.html', snippet['content'])
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'diff', '-s', 'workspace/snippets/nav-bar'])
                    assert_that(result.output).contains('No differences found')

    def test_show_differences_when_files_differ(self, default_elemental_fixture, default_settings_fixture, snippet):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='snippets',
                                                                         items=[snippet])
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                # Create local files with different content
                folder_path = default_settings_fixture["cmsCoreContext"]["SNIPPETS_FOLDER"]
                modified_snippet = snippet.copy()
                modified_snippet['cssDeps'] = ['style.css']
                files = [
                    (f'{folder_path}/nav-bar.json', json_util.dumps(modified_snippet)),
                    (f'{folder_path}/nav-bar.html', '<div>Changed</div>')
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'diff', '-s', 'nav-bar'])
                    # Check for spec changes
                    assert_that(result.output).contains('-  "cssDeps": []')
                    assert_that(result.output).contains('+    "style.css"')
                    # Check for content changes
                    assert_that(result.output).contains('-<div>Original</div>')
                    assert_that(result.output).contains('+<div>Changed</div>')

