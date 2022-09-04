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


class TestPushCommandShould:

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
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'privacy-policy',
            'language': 'en',
            'title': 'Privacy policy',
            'description': '',
            'isHome': True,
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]

    def test_fail_when_language_is_not_supported(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['pages',
                                             'push',
                                             '-p', 'home', 'ru'])
                assert_that(result.output).contains('"ru" language not supported')

    def test_fail_when_spec_file_is_missing(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['pages',
                                             'push',
                                             '-p', 'account', 'es'])
                assert_that(result.output).contains('There is no spec file for page account (es)')

    def test_fail_when_content_file_is_missing(self, default_elemental_fixture, default_settings_fixture, specs):
        runner = CliRunner()
        with runner.isolated_filesystem():
            files_specs = []
            root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
            for spec in specs:
                folder_path = f'{root_folder_path}/{spec["language"]}'
                files_specs.append((f'{folder_path}/{spec["name"]}.json', json_util.dumps(spec)))
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files_specs):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['pages',
                                             'push',
                                             '--page', 'home', 'en'])
                assert_that(result.output).contains('There is no content file for page home (en)')

    def test_display_2_success_feedback_messages(self, default_elemental_fixture, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
                files_specs = []
                for spec in specs:
                    folder_path = f'{root_folder_path}/{spec["language"]}'
                    files_specs.append((f'{folder_path}/{spec["name"]}.json', json_util.dumps(spec)))
                    files_specs.append((f'{folder_path}/{spec["name"]}.html', '<div></div>'))
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files_specs):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['pages',
                                                 'push',
                                                 '-p', 'home', 'en',
                                                 '-p', 'home', 'es'])
                    assert_that(re.findall('pushed successfully', result.output)).is_length(2)

    def test_create_backup_file_for_pushed_spec(self, default_elemental_fixture, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).get_connection_string(),
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='drafts',
                                                            items=[specs[1]])
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                root_folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).PAGES_FOLDER
                files_specs = []
                for spec in specs:
                    folder_path = f'{root_folder_path}/{spec["language"]}'
                    files_specs.append((f'{folder_path}/{spec["name"]}.json', json_util.dumps(spec)))
                    files_specs.append((f'{folder_path}/{spec["name"]}.html', '<div></div>'))
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files_specs):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli,
                                           ['pages',
                                            'push',
                                            '-p', 'home', 'es'],
                                           standalone_mode=False)

                    assert_that(result.return_value[0][0]).exists()
                    assert_that(result.return_value[0][1]).exists()
