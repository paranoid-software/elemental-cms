import json

import pytest
from from_root import from_root


@pytest.fixture
def settings_fixture():
    with open(from_root('tests/settings/testing.json')) as settings_as_json:
        return json.load(settings_as_json)
