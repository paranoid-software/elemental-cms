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
        destination_path = f'{self.context.cms_core_context.GLOBAL_DEPS_FOLDER}/{_type.replace("/", "_")}'
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        spec_file_destination_path = f'{destination_path}/{name}.json'
        if os.path.exists(spec_file_destination_path):
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
        spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
        spec_file.write(json_util.dumps(dep, indent=4))
        spec_file.close()
        click.echo(f'{destination_path}/{name}.json file has been created successfully.')
