import datetime
import re
import pytest
from assertpy import assert_that
from bson import ObjectId, json_util
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli

from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestPublishAllCommandShould:

    @pytest.fixture
    def specs(self):
        return [{
            '_id': ObjectId(),
            'name': 'home',
            'language': 'en',
            'title': 'Home',
            'description': '',
            'isHome': True,
            'cssDeps': [],
            'jsDeps': [],
            'content': '<div>Home</div>',
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'home',
            'language': 'es',
            'title': 'Inicio',
            'description': '',
            'isHome': True,
            'cssDeps': [],
            'jsDeps': [],
            'content': '<div>Inicio</div>',
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'about',
            'language': 'en',
            'title': 'About',
            'description': '',
            'isHome': False,
            'cssDeps': [],
            'jsDeps': [],
            'content': '<div>About</div>',
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_display_no_drafts_message_when_no_drafts_exist(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                 initial_state=[
                                     MongoDbState(db_name='elemental', data=[])
                                 ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                               'publish',
                                               '--all'])
                    assert_that(result.output).contains('There are no draft pages to publish.')

    def test_publish_all_draft_pages(self, default_elemental_fixture, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                 initial_state=[
                                     MongoDbState(db_name='elemental', data=[
                                         MongoDbStateData(coll_name='drafts',
                                                        items=specs)
                                     ])
                                 ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                               'publish',
                                               '--all'])
                    assert_that(re.findall('published successfully', result.output)).is_length(len(specs))
                    assert_that(reader.count('pages')).is_equal_to(len(specs))
