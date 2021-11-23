import time
import os

import click
from bson import json_util, ObjectId
from elementalcms.core import ElementalContext
from elementalcms.services.snippets import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, names):
        for name in names:
            snippets_folder = self.context.cms_core_context.SNIPPETS_FOLDER
            spec_file_path = f'{snippets_folder}/{name}.json'
            content_file_path = f'{snippets_folder}/{name}.html'
            if not os.path.exists(content_file_path):
                click.echo(f'There is no content file for snippet {name}.')
                return
            with open(spec_file_path) as spec_file_content:
                try:
                    spec = json_util.loads(spec_file_content.read())
                    if '_id' not in spec:
                        click.echo(f'Spec invalid for snippet {name}.')
                        return
                    if not ObjectId.is_valid(spec['_id']):
                        click.echo(f'Spec invalid for snippet {name}.')
                        return
                    if 'name' not in spec:
                        click.echo(f'Spec invalid for snippet {name}.')
                        return
                    if spec['name'] != name:
                        click.echo(f'Spec invalid for snippet {name}.')
                        return
                    with open(content_file_path) as content:
                        spec['content'] = content.read()
                        _id = spec['_id']
                        self.build_backup(_id)
                        update_me_result = UpdateOne(self.context.cms_db_context).execute(_id, spec)
                        if update_me_result.is_failure():
                            click.echo(f'Something went wrong and it was not possible to push snippet {name} into {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')
                            return
                        click.echo(f'Snippet {name} pushed successfully into {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')
                except Exception as e:
                    click.echo(e)
                    click.echo(f'Spec invalid for snippet {name}.')

    def build_backup(self, _id):
        get_one_result = GetOne(self.context.cms_db_context).execute(_id)
        if get_one_result.is_failure():
            return
        click.echo('Building backup...')
        snippet = get_one_result.value()
        html_content = snippet['content']
        del snippet['content']
        backups_folder_path = f'{self.context.cms_core_context.SNIPPETS_FOLDER}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        sufix = round(time.time())
        spec_file_destination_path = f'{backups_folder_path}/{snippet["name"]}-{sufix}.json'
        spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
        spec_file.write(json_util.dumps(snippet, indent=4))
        spec_file.close()
        content_file_destination_path = f'{backups_folder_path}/{snippet["name"]}-{sufix}.html'
        content_file = open(content_file_destination_path, mode="w", encoding="utf-8")
        content_file.write(html_content)
        content_file.close()
