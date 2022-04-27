import datetime
import os
import click
from bson import ObjectId, json_util

from elementalcms import ElementalContext


class Create:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, _type):

        # TODO: Validate naming constraints

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
        spec_filepath = f'{folder_path}/{name}.json'
        if os.path.exists(spec_filepath):
            click.echo(f'{name} ({_type}) global dependency already exist.')
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
        spec_file = open(spec_filepath, mode='w', encoding='utf-8')
        spec_file.write(json_util.dumps(dep, indent=4))
        spec_file.close()
        click.echo(f'{spec_filepath} file has been created successfully.')
