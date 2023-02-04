import datetime
import json
import os
import re
import pytest
from assertpy import assert_that
from bson import ObjectId
from click.testing import CliRunner

from elementalcms.core import MongoDbContext
from elementalcms.management import cli
from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState, MongoDbStateData


class TestListCommandShould:

    @pytest.fixture
    def deps(self):
        return [{
            '_id': ObjectId(),
            'order': 0,
            'name': 'jquery',
            'type': 'application/javascript',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'order': 1,
            'name': 'jquery-ui',
            'type': 'text/css',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'order': 2,
            'name': 'datejs',
            'type': 'model',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_display_empty_repository_feedback(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='global_deps',
                                                                         items=[])
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['global-deps',
                                                 'list'])
                    assert_that(result.output).contains('There are no global dependencies to list.')

    def test_display_current_global_dependencies_list(self, default_elemental_fixture, default_settings_fixture, deps):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[
                                                        MongoDbStateData(coll_name='global_deps',
                                                                         items=deps)
                                                    ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['global-deps',
                                                 'list'])
                    assert_that(re.findall('<->', result.output)).is_length(len(deps))
