import datetime
import os

import click
from bson import ObjectId, json_util

from elementalcms import ElementalContext


class Create:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, page_tuple):

        # TODO: Validate naming constraints

        name = page_tuple[0]
        lang = page_tuple[1]
        if lang not in self.context.cms_core_context.LANGUAGES:
            click.echo(f'"{lang}" language is not supported')
            return
        root_folder_path = self.context.cms_core_context.PAGES_FOLDER
        folder_path = f'{root_folder_path}/{lang}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        spec_filepath = f'{folder_path}/{name.replace("/", "_")}.json'
        content_filepath = f'{folder_path}/{name.replace("/", "_")}.html'
        if os.path.exists(spec_filepath):
            click.echo(f'{name} ({lang}) already exist.')
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
        spec_file = open(spec_filepath, mode='w', encoding='utf-8')
        spec_file.write(json_util.dumps(spec, indent=4))
        spec_file.close()
        content_file = open(content_filepath, mode='w', encoding='utf-8')
        content_file.write('<div></div>')
        content_file.close()
        click.echo(f'{folder_path}/{name}.json|html files has been created successfully.')
