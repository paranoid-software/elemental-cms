import datetime
import os
import click
from bson import ObjectId, json_util

from elementalcms import ElementalContext


class Create:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name):

        # TODO: Validate naming constraints

        folder_path = self.context.cms_core_context.SNIPPETS_FOLDER
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        spec_filepath = f'{folder_path}/{name}.json'
        content_filepath = f'{folder_path}/{name}.html'
        if os.path.exists(spec_filepath):
            click.echo(f'{name} snippet already exist.')
            return
        spec = {
            '_id': ObjectId(),
            'name': name,
            'cssDeps': [],
            'jsDeps': [],
            'createdAt': datetime.datetime.utcnow(),
            'lastModifiedAt': datetime.datetime.utcnow()
        }
        spec_file = open(spec_filepath, mode='w', encoding='utf-8')
        spec_file.write(json_util.dumps(spec, indent=4))
        spec_file.close()
        content_file = open(content_filepath, mode='w', encoding='utf-8')
        content_file.write('<div>_("This a new snippet.")</div>')
        content_file.close()
        click.echo(f'{folder_path}/{name}.json|html files has been created successfully.')
