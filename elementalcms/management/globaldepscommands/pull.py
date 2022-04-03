import time
import os
from shutil import copyfile
from typing import Optional

import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services.global_deps import GetMe, GetAll


class Pull:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, deps) -> [str]:
        if isinstance(deps, str):
            get_all_result = GetAll(self.context.cms_db_context).execute()
            deps_tuples = [] if get_all_result.is_failure() else [(item['name'], item['type'])
                                                                  for item in get_all_result.value()]
            if len(deps_tuples) == 0:
                click.echo('There are no global dependencies to pull.')
                return []
        else:
            deps_tuples = deps

        root_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER

        spec_backup_file_paths = []
        for element in deps_tuples:
            name = element[0]
            _type = element[1]
            get_me_result = GetMe(self.context.cms_db_context).execute(name, _type)
            dep = get_me_result.value()
            if dep is None:
                click.echo(f'Global dependency {name} ({_type}) does not exist.')
                continue
            type_folder_name = _type.replace('/', '_')
            folder_path = f'{root_folder_path}/{type_folder_name}'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            spec_file_path = f'{folder_path}/{name}.json'
            spec_backup_file_path = self.build_local_backup(folder_path, spec_file_path, name)
            spec_file = open(spec_file_path, mode='w', encoding='utf-8')
            spec_file.write(json_util.dumps(dep, indent=4))
            spec_file.close()
            click.echo(f'Global dependency {name} ({_type}) pulled successfully.')
            if spec_backup_file_path is not None:
                spec_backup_file_paths.append(spec_backup_file_path)
        return spec_backup_file_paths

    @staticmethod
    def build_local_backup(folder_path, spec_file_path, clean_file_name) -> Optional[str]:
        click.echo('Building local backup...')
        suffix = round(time.time())
        backups_folder_path = f'{folder_path}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        if os.path.exists(spec_file_path):
            spec_backup_file_path = f'{backups_folder_path}/{clean_file_name}-local-{suffix}.json'
            copyfile(spec_file_path, spec_backup_file_path)
            return spec_backup_file_path
        return None
