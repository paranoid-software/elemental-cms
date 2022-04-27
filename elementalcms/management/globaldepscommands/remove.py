import time
import os
from typing import Optional
import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.global_deps import GetMe, RemoveOne


class Remove:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, _type) -> Optional[str]:
        get_me_result = GetMe(self.context.cms_db_context).execute(name, _type)
        if get_me_result.is_failure():
            if isinstance(get_me_result, NoResult):
                click.echo(f'Global dependency {name} ({_type}) does not exist.')
                return None
            click.echo('Something went wrong and it was not possible to complete the operation.')
            return None

        dep = get_me_result.value()
        spec_backup_filepath = self.build_backup(dep)
        RemoveOne(self.context.cms_db_context).execute(dep['_id'])
        click.echo(f'Global dependency {name} ({_type}) removed successfully.')
        return spec_backup_filepath

    def build_backup(self, dep) -> str:
        click.echo('Building backup...')
        root_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
        type_folder_name = dep['type'].replace('/', '_')
        backups_folder_path = f'{root_folder_path}/{type_folder_name}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        suffix = round(time.time())
        spec_backup_filepath = f'{backups_folder_path}/{dep["name"]}-{suffix}.json'
        spec_backup_file = open(spec_backup_filepath, mode='w', encoding='utf-8')
        spec_backup_file.write(json_util.dumps(dep, indent=4))
        spec_backup_file.close()
        click.echo(f'{dep["name"]} backup built successfully.')
        return spec_backup_filepath
