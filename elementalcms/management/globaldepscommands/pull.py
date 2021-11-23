import time
import os
from shutil import copyfile

import click
from bson import json_util
from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.global_deps import GetMe


class Pull:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, names_tuples):
        deps_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
        for name_tuple in names_tuples:
            name = name_tuple[0]
            _type = name_tuple[1]
            get_dep_result = GetMe(self.context.cms_db_context).execute(name, _type)
            if get_dep_result.is_failure() and not isinstance(get_dep_result, NoResult):
                click.echo('Something went wrong and it was not possible to perform the operation.')
                continue
            dep = get_dep_result.value()
            if dep is None:
                click.echo(f'Global dep {name} of "{_type}" type do not exits.')
                continue
            self.build_local_backup(_type, name)
            if not os.path.exists(f'{deps_folder_path}/{_type.replace("/", "_")}'):
                os.makedirs(f'{deps_folder_path}/{_type.replace("/", "_")}')
            spec_file_destination_path = f'{deps_folder_path}/{_type.replace("/", "_")}/{name}.json'
            spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
            spec_file.write(json_util.dumps(dep, indent=4))
            spec_file.close()
            click.echo(f'Global dep {name} pulled successfully from {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')

    def build_local_backup(self, _type, name):
        click.echo('Building local backup...')
        deps_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
        sufix = round(time.time())
        backups_folder_path = f'{deps_folder_path}/{_type.replace("/", "_")}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        local_spec_file_path = f'{deps_folder_path}/{_type.replace("/", "_")}/{name}.json'
        backup_spec_file_path = f'{deps_folder_path}/{_type.replace("/", "_")}/.bak/{name}-local-{sufix}.json'
        if os.path.exists(local_spec_file_path):
            copyfile(local_spec_file_path, backup_spec_file_path)
