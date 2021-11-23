import datetime
import os

import click
from bson import ObjectId, json_util

from elementalcms import ElementalContext


class Create:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name):
        destination_folder = self.context.cms_core_context.SNIPPETS_FOLDER
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        spec_file_destination_path = f'{destination_folder}/{name}.json'
        content_file_destination_path = f'{destination_folder}/{name}.html'
        if os.path.exists(spec_file_destination_path):
            click.echo(f'A snippet with the name "{name}" already exists.')
            return
        spec = {
            '_id': ObjectId(),
            'name': name,
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }
        spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
        spec_file.write(json_util.dumps(spec, indent=4))
        spec_file.close()
        content_file = open(content_file_destination_path, mode="w", encoding="utf-8")
        content_file.write('<div>_("This a new snippet.")</div>')
        content_file.close()
        click.echo(f'{destination_folder}/{name}.json|html files has been created successfully.')
