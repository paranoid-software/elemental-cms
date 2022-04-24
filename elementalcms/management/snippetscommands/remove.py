import os
import time
from typing import Optional, Tuple
import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.snippets import GetMe, RemoveOne


class Remove:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name) -> Optional[Tuple]:

        get_me_result = GetMe(self.context.cms_db_context).execute(name)
        if get_me_result.is_failure():
            if isinstance(get_me_result, NoResult):
                click.echo(f'Snippet {name} does not exist.')
                return None
            click.echo('Something went wrong and it was not possible to complete the operation.')
            return None

        snippet = get_me_result.value()

        backup_filepaths = self.build_backup(snippet)

        RemoveOne(self.context.cms_db_context).execute(snippet['_id'])
        click.echo(f'Snippet {name} removed successfully.')
        return backup_filepaths

    def build_backup(self, snippet) -> Optional[Tuple]:
        click.echo('Building backup...')
        html_content = snippet.pop('content', '')
        backups_folder_path = f'{self.context.cms_core_context.SNIPPETS_FOLDER}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        sufix = round(time.time())
        spec_backup_filepath = f'{backups_folder_path}/{snippet["name"]}-{sufix}.json'
        spec_backup_file = open(spec_backup_filepath, mode='w', encoding='utf-8')
        spec_backup_file.write(json_util.dumps(snippet, indent=4))
        spec_backup_file.close()
        content_backup_filepath = f'{backups_folder_path}/{snippet["name"]}-{sufix}.html'
        content_backup_file = open(content_backup_filepath, mode='w', encoding='utf-8')
        content_backup_file.write(html_content)
        content_backup_file.close()
        return spec_backup_filepath, content_backup_filepath
