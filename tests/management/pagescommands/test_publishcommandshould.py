import datetime
import pytest
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext
from elementalcms.management import cli

from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPublishCommandShould:

    @pytest.fixture
    def drafts(self):
        return [{
                    '_id': ObjectId(),
                    'name': 'home',
                    'language': 'en',
                    'title': 'Home',
                    'description': '',
                    'isHome': True,
                    'content': '<div>New Home</div>',
                    'cssDeps': [],
                    'jsDeps': [],
                    'createdAt': datetime.datetime.utcnow(),
                    'lastModifiedAt': datetime.datetime.utcnow()
                }]

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

    def test_fail_when_draft_version_is_missing(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                                 'publish',
                                                 '--page', 'home', 'en'])
                    assert_that(result.output).contains('home (en) does not have a draft version.')

    def test_fail_when_page_is_already_released(self, default_elemental_fixture, default_settings_fixture, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData('drafts', pages),
                                                        MongoDbStateData('pages', pages),
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                                 'publish',
                                                 '--page', 'home', 'en'])
                    assert_that(result.output).contains('home (en) is already published.')

    def test_display_success_feedback_message(self, default_elemental_fixture, default_settings_fixture, drafts):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData('drafts', drafts)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                                 'publish',
                                                 '--page', 'home', 'en'])
                    assert_that(result.output).contains('home (en) published successfully.')

    def test_create_backup_file_for_published_page(self, default_elemental_fixture, default_settings_fixture, drafts, pages):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData('drafts', drafts),
                                           MongoDbStateData('pages', pages)
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli,
                                           ['pages',
                                            'publish',
                                            '-p', 'home', 'en'],
                                           standalone_mode=False)

                    assert_that(result.return_value[0][0]).exists()
                    assert_that(result.return_value[0][1]).exists()
