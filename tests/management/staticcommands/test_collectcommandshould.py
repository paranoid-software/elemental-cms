from assertpy import assert_that
from click.testing import CliRunner
from elementalcms.management import cli
from tests import EphemeralGcsContext, EphemeralElementalFileSystem
from tests.ephemeralgcscontext import GcsState


class TestCollectCommandShould:

    def test_fail_when_no_static_bucket_setting_found(self, default_elemental_fixture, missing_gcs_buckets_settings_fixture):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with EphemeralElementalFileSystem(default_elemental_fixture, missing_gcs_buckets_settings_fixture):
                # noinspection PyTypeChecker
                result = runner.invoke(cli, ['static', 'collect', 'static/*'])
                assert_that(result.output).contains('STATIC_BUCKET parameter not found on current settings.')

    def test_updload_static_files_to_static_bucket(self, default_elemental_fixture, default_settings_fixture):
        with EphemeralGcsContext(initial_state=[
            GcsState(default_settings_fixture['cmsCoreContext']['STATIC_BUCKET'])
        ]) as bucket_name:
            default_settings_fixture['cmsCoreContext']['STATIC_BUCKET'] = bucket_name
            runner = CliRunner()
            with runner.isolated_filesystem():
                with EphemeralElementalFileSystem(default_elemental_fixture, default_settings_fixture, [
                    ('static/collect-test.txt', 'Hi stranger, I am a static file.')
                ]):
                    # noinspection PyTypeChecker
                    result = runner.invoke(cli, ['static', 'collect', 'static/*.jpg', '--ignore-internals'])
                    assert_that(result.output).contains('Collect command excecuted successfully.')
