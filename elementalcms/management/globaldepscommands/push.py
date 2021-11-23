import time
import os

import click
from bson import json_util, ObjectId
from elementalcms.core import ElementalContext
from elementalcms.services.global_deps import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, names_tuples):
        for name_tuple in names_tuples:
            name = name_tuple[0]
            _type = name_tuple[1]
            if _type not in ['application/javascript',
                             'text/css',
                             'module']:
                click.echo(f'"{_type}" type not supported.')
                continue
            deps_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
            spec_file_path = f'{deps_folder_path}/{_type.replace("/", "_")}/{name}.json'
            if not os.path.exists(spec_file_path):
                click.echo(f'There is no file for dep {name} of {_type} type.')
                continue
            with open(spec_file_path) as spec_content:
                try:
                    spec = json_util.loads(spec_content.read())
                    if '_id' not in spec:
                        click.echo(f'Spec invalid for dep {name} of {_type} type.')
                        continue
                    if not ObjectId.is_valid(spec['_id']):
                        click.echo(f'Spec invalid for dep {name} of {_type} type.')
                        continue
                    if 'name' not in spec:
                        click.echo(f'Spec invalid for dep {name} of {_type} type.')
                        continue
                    if spec['name'] != name:
                        click.echo(f'Spec invalid for dep {name} of {_type} type.')
                        continue
                    _id = spec['_id']
                    self.build_draft_backup(_id)
                    update_me_result = UpdateOne(self.context.cms_db_context).execute(_id, spec)
                    if update_me_result.is_failure():
                        click.echo(f'Something went wrong and it was not possible to push dep {name} into {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')
                        continue
                    click.echo(f'Global dep {name} pushed successfully into {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')
                except Exception as e:
                    click.echo(e)
                    click.echo(f'Spec invalid for dep {name} of {_type} type.')

    def build_draft_backup(self, _id):
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
