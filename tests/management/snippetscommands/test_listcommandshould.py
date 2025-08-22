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


class TestListCommandShould:

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

    def test_display_empty_repository_feedback(self, default_elemental_fixture, default_settings_fixture):
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
                    result = runner.invoke(cli, ['snippets',
                                                 'list'])
                    assert_that(result.output).contains('There are no snippets to list.')

    def test_indicate_missing_local_files(self, default_elemental_fixture, default_settings_fixture, snippets):
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
                folder_path = default_settings_fixture["cmsCoreContext"]["SNIPPETS_FOLDER"]
                files = [(f'{folder_path}/.keep', '')]  # Empty file to ensure folder exists
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'list'])
                    # Should show * for all snippets as they don't exist locally
                    assert_that(result.output).contains('* nav-bar')
                    assert_that(result.output).contains('* footer')

    def test_indicate_local_changes(self, default_elemental_fixture, default_settings_fixture, snippets):
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
                # Create local files with different content
                folder_path = default_settings_fixture["cmsCoreContext"]["SNIPPETS_FOLDER"]
                # Create a modified version of nav-bar
                nav_bar = snippets[0].copy()
                nav_bar['cssDeps'] = ['style.css']  # Change to trigger difference
                
                files = [
                    # nav-bar with changes
                    (f'{folder_path}/nav-bar.json', json_util.dumps(nav_bar)),
                    (f'{folder_path}/nav-bar.html', '<div>Changed</div>'),
                    # footer exact copy from fixture
                    (f'{folder_path}/footer.json', json_util.dumps(snippets[1])),
                    (f'{folder_path}/footer.html', snippets[1]['content'])
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'list'])
                    # nav-bar should show change indicator, footer should not
                    assert_that(result.output).contains('* nav-bar')
                    assert_that(result.output).contains('  footer')

    def test_indicate_local_only_snippets(self, default_elemental_fixture, default_settings_fixture, snippets):
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
                # Create local files including one that's not in the database
                folder_path = default_settings_fixture["cmsCoreContext"]["SNIPPETS_FOLDER"]
                files = [
                    # footer exact copy from fixture
                    (f'{folder_path}/footer.json', json_util.dumps(snippets[1])),
                    (f'{folder_path}/footer.html', snippets[1]['content']),
                    # local-only snippet
                    (f'{folder_path}/local-only.json', '{"name": "local-only", "cssDeps": [], "jsDeps": []}'),
                    (f'{folder_path}/local-only.html', '<div>Local only</div>')
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'list'])
                    # footer should not show indicator, local-only should show indicator
                    assert_that(result.output).contains('  footer')
                    assert_that(result.output).contains('* local-only')

    def test_show_local_only_snippets_when_db_empty(self, default_elemental_fixture, default_settings_fixture):
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
                # Create local files with no corresponding DB entries
                folder_path = default_settings_fixture["cmsCoreContext"]["SNIPPETS_FOLDER"]
                files = [
                    (f'{folder_path}/local-one.json', '{"name": "local-one", "cssDeps": [], "jsDeps": []}'),
                    (f'{folder_path}/local-one.html', '<div>Local one</div>'),
                    (f'{folder_path}/local-two.json', '{"name": "local-two", "cssDeps": [], "jsDeps": []}'),
                    (f'{folder_path}/local-two.html', '<div>Local two</div>')
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets', 'list'])
                    # Both snippets should show indicator as they only exist locally
                    assert_that(result.output).contains('* local-one')
                    assert_that(result.output).contains('* local-two')
