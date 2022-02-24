import datetime
import os
import click
from bson import ObjectId, json_util

from elementalcms import ElementalContext


class Create:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, _type):
        if _type not in ['application/javascript',
                         'text/css',
                         'module']:
            click.echo(f'{_type} type is not supported.')
            return
        root_folder_path = self.context.cms_core_context.GLOBAL_DEPS_FOLDER
        type_folder_name = _type.replace('/', '_')
        folder_path = f'{root_folder_path}/{type_folder_name}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        spec_file_path = f'{folder_path}/{name}.json'
        if os.path.exists(spec_file_path):
            click.echo(f'The global dependency {name} ({_type}) already exist.')
            return
        dep = {
            '_id': ObjectId(),
            'order': -1,
            'name': name,
            'type': _type,
            'url': '',
            'meta': {},
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }
        spec_file = open(spec_file_path, mode='w', encoding='utf-8')
        spec_file.write(json_util.dumps(dep, indent=4))
        spec_file.close()
        click.echo(f'{spec_file_path} file has been created successfully.')
