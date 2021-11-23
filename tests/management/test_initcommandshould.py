import json
import os
from click.testing import CliRunner
from elementalcms.management import cli


class TestInitCommandShould:

    def test_exit_early_when_project_is_already_initialized(self, debug_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(debug_settings_fixture))
            with open('.elemental', 'w') as e:
                e.write('{}')
            result = runner.invoke(cli, ['init'])
            assert 'Elemental CMS has been already initialized.' in result.output
            assert 'Initializing Elemental CMS' not in result.output
            assert 'Initialization completed...' not in result.output

    def test_create_default_folder_structure(self, debug_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(debug_settings_fixture))
            runner.invoke(cli, ['init'])
            assert os.path.exists('media')
            assert os.path.exists('static')
            assert os.path.exists(f'static/{debug_settings_fixture["cmsCoreContext"]["APP_NAME"]}')
            assert os.path.exists('templates')
            assert os.path.exists('workspace')
            assert os.path.exists('workspace/global_deps')
            assert os.path.exists('workspace/snippets')
            assert os.path.exists('workspace/pages')
            assert os.path.exists('.elemental')

    def test_show_success_feedback(self, debug_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.makedirs('settings')
            with open('settings/debug.json', 'w') as f:
                f.write(json.dumps(debug_settings_fixture))
            result = runner.invoke(cli, ['init'])
            assert 'Initialization completed...' in result.output
