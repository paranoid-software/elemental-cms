import time
import os
import click
from bson import json_util, ObjectId

from elementalcms.core import ElementalContext
from elementalcms.services.global_deps import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, deps):

        root_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER

        if isinstance(deps, str):
            deps_tuples = []
            for r, d, f in os.walk(root_folder_path):
                for file in f:
                    deps_tuples.append((file.split('.')[0], r.split('/')[-1].replace('_', '/')))
            if len(deps_tuples) == 0:
                click.echo('There are no global dependencies to push.')
                return
        else:
            deps_tuples = deps

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
                    continue
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
                UpdateOne(self.context.cms_db_context).execute(_id, dep)
                click.echo(f'Global dependency {name} ({_type}) pushed successfully.')

    def build_backup(self, _id):
        get_one_result = GetOne(self.context.cms_db_context).execute(_id)
        if get_one_result.is_failure():
            return
        click.echo('Building backup...')
        root_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
        dep = get_one_result.value()
        type_folder_name = dep['type'].replace('/', '_')
        folder_path = f'{root_folder_path}/{type_folder_name}'
        sufix = round(time.time())
        backups_folder_path = f'{folder_path}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        spec_backup_file_path = f'{backups_folder_path}/{dep["name"]}-{sufix}.json'
        spec_backup_file = open(spec_backup_file_path, mode='w', encoding='utf-8')
        spec_backup_file.write(json_util.dumps(dep, indent=4))
        spec_backup_file.close()
