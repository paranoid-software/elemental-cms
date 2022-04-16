import json

import pytest
from from_root import from_root


@pytest.fixture
def default_settings_fixture():
    with open(from_root('tests/settings/default.json')) as settings_as_json_string:
        return json.load(settings_as_json_string)


@pytest.fixture
def missing_gcs_buckets_settings_fixture():
    with open(from_root('tests/settings/missing-gcs-buckets.json')) as settings_as_json_string:
        return json.load(settings_as_json_string)


@pytest.fixture
def missing_media_folder_settings_fixture():
    with open(from_root('tests/settings/missing-media-folder.json')) as settings_as_json_string:
        return json.load(settings_as_json_string)


@pytest.fixture
def missing_db_name_settings_fixture():
    with open(from_root('tests/settings/missing-db-name.json')) as settings_as_json_string:
        return json.load(settings_as_json_string)
