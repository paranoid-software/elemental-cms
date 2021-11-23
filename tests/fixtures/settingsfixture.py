import json

import pytest
from from_root import from_root


@pytest.fixture
def debug_settings_fixture():
    with open(from_root('tests/settings/debug.json')) as settings_as_json:
        return json.load(settings_as_json)


@pytest.fixture
def prod_settings_fixture():
    with open(from_root('tests/settings/prod.json')) as settings_as_json:
        return json.load(settings_as_json)
