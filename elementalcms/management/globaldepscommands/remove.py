import os
import time

import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.global_deps import GetMe, RemoveOne, GetOne


class Remove:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, _type):

        get_dep_result = GetMe(self.context.cms_db_context).execute(name, _type)
        if get_dep_result.is_failure():
            if not isinstance(get_dep_result, NoResult):
                click.echo('Something went wrong and it was not possible to complete the operation.')
                return
        dep = get_dep_result.value()
        if dep is None:
            click.echo(f'Global dep {name} of "{_type}" type does not exists.')
            return

        self.build_backup(dep['_id'])

        RemoveOne(self.context.cms_db_context).execute(dep['_id'])
        click.echo(f'Global dep {name} of {_type}" type removed successfully.')

    def build_backup(self, _id):
        get_one_result = GetOne(self.context.cms_db_context).execute(_id)
        if get_one_result.is_failure():
            return
        click.echo('Building backup...')
        dep = get_one_result.value()
        backups_folder_path = f'{self.context.cms_core_context.GLOBAL_DEPS_FOLDER}/{dep["type"].replace("/", "_")}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        sufix = round(time.time())
        spec_file_destination_path = f'{backups_folder_path}/{dep["name"]}-{sufix}.json'
        spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
        spec_file.write(json_util.dumps(dep, indent=4))
        spec_file.close()
