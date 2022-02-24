import time
import os
import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.global_deps import GetMe, RemoveOne, GetOne


class Remove:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, _type):
        get_me_result = GetMe(self.context.cms_db_context).execute(name, _type)
        if get_me_result.is_failure():
            if not isinstance(get_me_result, NoResult):
                click.echo('Something went wrong and it was not possible to complete the operation.')
                return
        dep = get_me_result.value()
        if dep is None:
            click.echo(f'Global dependency {name} ({_type}) does not exist.')
            return
        self.build_backup(dep['_id'])
        RemoveOne(self.context.cms_db_context).execute(dep['_id'])
        click.echo(f'Global dependency {name} ({_type}) removed successfully.')

    def build_backup(self, _id):
        get_one_result = GetOne(self.context.cms_db_context).execute(_id)
        if get_one_result.is_failure():
            return
        click.echo('Building backup...')
        folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
        dep = get_one_result.value()
        type_folder_name = dep['type'].replace('/', '_')
        sufix = round(time.time())
        backups_folder_path = f'{folder_path}/{type_folder_name}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        spec_file_destination_path = f'{backups_folder_path}/{dep["name"]}-{sufix}.json'
        spec_file = open(spec_file_destination_path, mode='w', encoding='utf-8')
        spec_file.write(json_util.dumps(dep, indent=4))
        spec_file.close()
