import datetime
import os

import click
from bson import ObjectId, json_util

from elementalcms import ElementalContext


class Create:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, lang):
        if lang not in self.context.cms_core_context.LANGUAGES:
            click.echo(f'"{lang}" language is not supported')
            return
        destination_folder = self.context.cms_core_context.PAGES_FOLDER
        destination_path = f'{destination_folder}/{lang}'
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        spec_file_destination_path = f'{destination_path}/{name}.json'
        content_file_destination_path = f'{destination_path}/{name}.html'
        if os.path.exists(spec_file_destination_path):
            click.echo(f'A page with the name "{name}" in "{lang}" language already exists.')
            return
        spec = {
            '_id': ObjectId(),
            'name': name,
            'language': lang,
            'title': f'{name} page',
            'description': '',
            'isHome': False,
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }
        spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
        spec_file.write(json_util.dumps(spec, indent=4))
        spec_file.close()
        content_file = open(content_file_destination_path, mode="w", encoding="utf-8")
        content_file.write('<div></div>')
        content_file.close()
        click.echo(f'{destination_path}/{name}.json|html files has been created successfully.')
