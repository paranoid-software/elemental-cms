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
            'name': 'nav-bar',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }, {
            '_id': ObjectId(),
            'name': 'footer',
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }]
    
    def test_fail_when_snippets_folder_is_incorrect(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'push',
                                             '-s', 'folder1/nav-bar'])
                assert_that(result.output).contains('Snippet folder1/nav-bar is not on required folder: workspace/snippets.')

    def test_fail_when_spec_file_is_missing(self, default_elemental_fixture, default_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'push',
                                             '-s', 'nav-bar'])
                assert_that(result.output).contains('There is no spec file for nav-bar snippet.')

    def test_fail_when_content_file_is_missing(self, default_elemental_fixture, default_settings_fixture, specs):
        runner = CliRunner()
        with runner.isolated_filesystem():
            folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
            files_specs = []
            for spec in specs:
                files_specs.append((f'{folder_path}/{spec["name"]}.json', json_util.dumps(spec)))
            with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files_specs):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['snippets',
                                             'push',
                                             '-s', 'workspace/snippets/nav-bar'])
                assert_that(result.output).contains('There is no content file for nav-bar snippet.')

    def test_display_2_success_feedback_messages(self, default_elemental_fixture, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental',
                                                    data=[])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                files_specs = []
                for spec in specs:
                    files_specs.extend([(f'{folder_path}/{spec["name"]}.json',json_util.dumps(spec)),
                                        (f'{folder_path}/{spec["name"]}.html', '<div></div>')])
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files_specs):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['snippets',
                                                 'push',
                                                 '-s', 'nav-bar', '-s', 'footer'])
                    assert_that(re.findall('pushed successfully', result.output)).is_length(2)

    def test_create_backup_file_for_pushed_spec(self, default_elemental_fixture, default_settings_fixture, specs):
        with EphemeralMongoContext(MongoDbContext(default_settings_fixture['cmsDbContext']).connection_string,
                                   initial_state=[
                                       MongoDbState(db_name='elemental', data=[
                                           MongoDbStateData(coll_name='snippets',
                                                            items=[specs[1]])
                                       ])
                                   ]) as (db_name, reader):
            default_settings_fixture['cmsDbContext']['databaseName'] = db_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                folder_path = FlaskContext(default_settings_fixture["cmsCoreContext"]).SNIPPETS_FOLDER
                files_specs = []
                for spec in specs:
                    files_specs.extend([(f'{folder_path}/{spec["name"]}.json', json_util.dumps(spec)),
                                        (f'{folder_path}/{spec["name"]}.html', '<div></div>')])
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, files_specs):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli,
                                           ['snippets',
                                            'push',
                                            '-s', 'workspace/snippets/footer'],
                                           standalone_mode=False)

                    assert_that(result.return_value[0][0]).exists()
                    assert_that(result.return_value[0][1]).exists()
