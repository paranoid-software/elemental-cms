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
    def pages(self):
        return [{
            '_id': ObjectId(),
            'name': 'home',
            'language': 'en',
            'title': 'Home',
            'description': '',
            'isHome': True,
            'content': '<div>Home</div>',
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
            'content': '<div>Inicio</div>',
            'isHome': True,
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
            'content': '<div>Privacy policy</div>',
            'isHome': True,
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
                                                        MongoDbStateData(coll_name='pages',
                                                                         items=[])
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                                 'list'])
                    assert_that(result.output).contains('There are no pages to list.')

    def test_display_current_pages_list(self, default_elemental_fixture, default_settings_fixture, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='pages',
                                                                         items=pages)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                                 'list'])
                    assert_that(all(substring in result.output for substring in ['home', 'privacy-policy']))

    def test_indicate_missing_local_files(self, default_elemental_fixture, default_settings_fixture, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='pages',
                                                                         items=pages)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                root_folder_path = default_settings_fixture["cmsCoreContext"]["PAGES_FOLDER"]
                files = [
                    (f'{root_folder_path}/en/.keep', ''),  # Empty file to ensure folder exists
                    (f'{root_folder_path}/es/.keep', '')   # Empty file to ensure folder exists
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages', 'list'])
                    # Should show * for all pages as they don't exist locally
                    assert_that(result.output).contains('* home (en)')
                    assert_that(result.output).contains('* home (es)')
                    assert_that(result.output).contains('* privacy-policy (en)')

    def test_indicate_local_changes(self, default_elemental_fixture, default_settings_fixture, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='pages',
                                                                         items=pages)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                # Create local files with different content
                root_folder_path = default_settings_fixture["cmsCoreContext"]["PAGES_FOLDER"]
                # Create a modified version of home (en)
                home_en = pages[0].copy()
                home_en['cssDeps'] = ['style.css']  # Change to trigger difference
                
                files = [
                    # home (en) with changes
                    (f'{root_folder_path}/en/home.json', json_util.dumps(home_en)),
                    (f'{root_folder_path}/en/home.html', '<div>Changed</div>'),
                    # home (es) and privacy-policy exact copy from fixture
                    (f'{root_folder_path}/es/home.json', json_util.dumps(pages[1])),
                    (f'{root_folder_path}/es/home.html', pages[1]['content']),
                    (f'{root_folder_path}/en/privacy-policy.json', json_util.dumps(pages[2])),
                    (f'{root_folder_path}/en/privacy-policy.html', pages[2]['content'])
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages', 'list'])
                    # home (en) should show change indicator, others should not
                    assert_that(result.output).contains('* home (en)')
                    assert_that(result.output).contains('  home (es)')
                    assert_that(result.output).contains('  privacy-policy (en)')

    def test_indicate_local_only_pages(self, default_elemental_fixture, default_settings_fixture, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='pages',
                                                                         items=pages)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                # Create local files including one that's not in the database
                root_folder_path = default_settings_fixture["cmsCoreContext"]["PAGES_FOLDER"]
                files = [
                    # home (es) exact copy from fixture
                    (f'{root_folder_path}/es/home.json', json_util.dumps(pages[1])),
                    (f'{root_folder_path}/es/home.html', pages[1]['content']),
                    # local-only page
                    (f'{root_folder_path}/en/about.json', json_util.dumps({
                        '_id': ObjectId(),
                        'name': 'about',
                        'language': 'en',
                        'title': 'About Us',
                        'description': '',
                        'isHome': False,
                        'cssDeps': [],
                        'jsDeps': []
                    })),
                    (f'{root_folder_path}/en/about.html', '<div>About Us</div>')
                ]
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages', 'list'])
                    # home (es) should not show indicator, about (en) should show indicator
                    assert_that(result.output).contains('  home (es)')
                    assert_that(result.output).contains('* about (en)')