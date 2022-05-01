import json
import os
from typing import Optional, List, Tuple

from click.testing import CliRunner


class EphemeralElementalFileSystem:

    runner: CliRunner

    def __init__(self,
                 default_elemental_spec: Optional[dict] = None,
                 default_config_spec: Optional[dict] = None,
                 files_specs: List[Tuple] = None):

        if default_elemental_spec:
            open('.elemental', 'w').write(json.dumps(default_elemental_spec))

        if default_config_spec:
            config_file_path_folder = os.path.dirname(default_elemental_spec['configFilePath'])
            os.makedirs(config_file_path_folder, exist_ok=True)
            with open(default_elemental_spec['configFilePath'], 'w') as f:
                f.write(json.dumps(default_config_spec))

        for file_spec in files_specs or []:
            path_parts = file_spec[0].split(os.path.sep)
            folder = os.path.sep.join(path_parts[0:-1])
            if folder:
                os.makedirs(folder, exist_ok=True)
            open(file_spec[0], 'w').write(file_spec[1])

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
