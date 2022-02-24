import time
import os
import click
from bson import json_util, ObjectId

from elementalcms.core import ElementalContext
from elementalcms.services.global_deps import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, deps_tuples):
        for element in deps_tuples:
            name = element[0]
            _type = element[1]
            if _type not in ['application/javascript',
                             'text/css',
                             'module']:
                click.echo(f'"{_type}" type is not supported.')
                continue
            deps_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
            dep_typed_folder_name = _type.replace('/', '_')
            spec_file_path = f'{deps_folder_path}/{dep_typed_folder_name}/{name}.json'
            if not os.path.exists(spec_file_path):
                click.echo(f'There is no spec file for {name} ({_type}).')
                continue
            with open(spec_file_path) as spec_content:
                try:
                    dep = json_util.loads(spec_content.read())
                except Exception as e:
                    click.echo(e)
                    click.echo(f'Invalid spec for dependency {name} ({_type}).')
                if '_id' not in dep:
                    click.echo(f'Missing spec _id for: {name} ({_type})')
                    continue
                if not ObjectId.is_valid(dep['_id']):
                    click.echo(f'Invalid spec _id for: {name} ({_type})')
                    continue
                if 'name' not in dep:
                    click.echo(f'Missing spec name for: {name} ({_type})')
                    continue
                if dep['name'] != name:
                    click.echo(f'Invalid spec name for: {name} ({_type})')
                    continue
                _id = dep['_id']
                self.build_backup(_id)
                update_one_result = UpdateOne(self.context.cms_db_context).execute(_id, dep)
                if update_one_result.is_failure():
                    click.echo('Something went wrong and it was not possible to perform the operation.')
                    continue
                click.echo(f'Global dependency {name} ({_type}) pushed successfully.')

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
