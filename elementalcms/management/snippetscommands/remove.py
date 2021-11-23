import os
import time

import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.snippets import GetMe, RemoveOne, GetOne


class Remove:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name):

        get_me_result = GetMe(self.context.cms_db_context).execute(name)
        if get_me_result.is_failure():
            if not isinstance(get_me_result, NoResult):
                click.echo('Something went wrong and it was not possible to complete the operation.')
                return
        snippet = get_me_result.value()
        if snippet is None:
            click.echo(f'Snippet {name} does not exists.')
            return

        self.build_backup(snippet['_id'])

        RemoveOne(self.context.cms_db_context).execute(snippet['_id'])
        click.echo(f'Snippet {name} removed successfully.')

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
