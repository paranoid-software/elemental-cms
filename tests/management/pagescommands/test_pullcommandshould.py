import datetime
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

    def test_create_spec_for_pulled_pages(self, default_elemental_fixture, default_settings_fixture, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='pages',
                                                                         items=pages[:2])
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    runner.invoke(cli, ['pages',
                                        'pull',
                                        '-p', 'home', 'en',
                                        '-p', 'home', 'es'])
                    folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
                    [assert_that(f'{folder_path}/{page["language"]}/{page["name"]}.json').exists() for page in pages[:2]]

    def test_create_backup_file_for_pulled_page(self, default_elemental_fixture, default_settings_fixture, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='pages',
                                                            items=pages)
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
                folder_path = f'{root_folder_path}/en'
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, [
                    (f'{folder_path}/home.json', '{}'),
                    (f'{folder_path}/home.html', '<div></div>')
                ]):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli,
                                           [
                                               'pages',
                                               'pull',
                                               '--page', 'home', 'en'
                                           ],
                                           standalone_mode=False)

                    assert_that(result.return_value[0][0]).exists()
                    assert_that(result.return_value[0][1]).exists()

    def test_display_1_successful_pull_operation_feedback_message(self,
                                                                  default_elemental_fixture,
                                                                  default_settings_fixture,
                                                                  pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
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
                                                 'pull',
                                                 '-p', 'home', 'en'])
                    assert_that(re.findall('pulled successfully', result.output)).is_length(1)
