import os
from datetime import datetime

import pytest


@pytest.fixture
def default_elemental_fixture():
    return {
        'configFilePath': os.path.join('settings', 'default.json'),
        'lastUpdateTime': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
