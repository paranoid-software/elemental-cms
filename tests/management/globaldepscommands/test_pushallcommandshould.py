import datetime
import os
import pytest
from assertpy import assert_that
from bson import ObjectId, json_util
from click.testing import CliRunner

from elementalcms.core import MongoDbContext, FlaskContext
from elementalcms.management import cli

from tests import EphemeralMongoContext, EphemeralElementalFileSystem
from tests.ephemeralmongocontext import MongoDbState


class TestPushAllCommandShould:

    @pytest.fixture
    def specs(self):
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
            'name': 'semantic-ui',
            'type': 'text/css',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'order': 2,
            'name': 'slack',
            'type': 'module',
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_display_empty_folder_feedback(self, default_elemental_fixture, default_settings_fixture):
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
                    result = runner.invoke(cli, ['global-deps',
                                                 'push',
                                                 '--all'])
                    assert_that(result.output).contains('There are no global dependencies to push.')

    def test_push_current_specs(self, default_elemental_fixture, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).GLOBAL_DEPS_FOLDER
                files_specs = []
                for spec in specs:
                    name = spec['name']
                    _type = spec['type']
                    type_folder_name = _type.replace('/', '_')
                    folder_path = os.path.join(root_folder_path, type_folder_name)
                    files_specs.append((os.path.join(folder_path, f'{name}.json'), json_util.dumps(spec)))
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files_specs):
                    # noinspection PyTypeChecker
                    runner.invoke(cli, ['global-deps',
                                        'push',
                                        '--all'])
                    assert_that(reader.count('global_deps')).is_equal_to(len(specs))
