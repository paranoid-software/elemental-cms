import time
import os
from typing import Optional
import click
from bson import json_util, ObjectId

from elementalcms.core import ElementalContext
from elementalcms.services.global_deps import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, deps) -> [str]:

        root_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER

        if isinstance(deps, str):
            deps_tuples = []
            for r, d, f in os.walk(root_folder_path):
                if '.bak' in r:
                    continue
                for file in f:
                    if '.json' not in file:
                        continue
                    deps_tuples.append((file.split('.json')[0], r.split('/')[-1].replace('_', '/')))
            if len(deps_tuples) == 0:
                click.echo('There are no global dependencies to push.')
                return
        else:
            deps_tuples = deps
            # TODO: Support file names with paths

        backups_filepaths = []
        for dep_tuple in deps_tuples:
            name = dep_tuple[0]
            _type = dep_tuple[1]
            if _type not in ['application/javascript',
                             'text/css',
                             'module']:
                click.echo(f'"{_type}" type is not supported.')
                continue
            type_folder_name = _type.replace('/', '_')
            folder_path = f'{root_folder_path}/{type_folder_name}'
            spec_filepath = f'{folder_path}/{name}.json'
            if not os.path.exists(spec_filepath):
                click.echo(f'There is no spec file for {name} ({_type}).')
                continue
            with open(spec_filepath, encoding='utf-8') as spec_file:
                try:
                    dep = json_util.loads(spec_file.read())
                except Exception as e:
                    click.echo(f'Invalid spec for dependency {name} ({_type}) - {e}')
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
                backup_filepath = self.build_backup(_id)
                UpdateOne(self.context.cms_db_context).execute(_id, dep)
                click.echo(f'Global dependency {name} ({_type}) pushed successfully.')
                if backup_filepath is not None:
                    backups_filepaths.append(backup_filepath)
        return backups_filepaths

    def build_backup(self, _id) -> Optional[str]:
        get_one_result = GetOne(self.context.cms_db_context).execute(_id)
        if get_one_result.is_failure():
            return None
        click.echo('Building backup...')
        root_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
        dep = get_one_result.value()
        type_folder_name = dep['type'].replace('/', '_')
        folder_path = f'{root_folder_path}/{type_folder_name}'
        suffix = round(time.time())
        backups_folder_path = f'{folder_path}/.bak'
        os.makedirs(backups_folder_path, exist_ok=True)
        spec_backup_filepath = f'{backups_folder_path}/{dep["name"]}-{suffix}.json'
        spec_backup_file = open(spec_backup_filepath, mode='w', encoding='utf-8')
        spec_backup_file.write(json_util.dumps(dep, indent=4))
        spec_backup_file.close()
        return spec_backup_filepath
