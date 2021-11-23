import time
import os
from shutil import copyfile

import click
from bson import json_util
from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.snippets import GetMe


class Pull:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, names):
        snippets_folder = self.context.cms_core_context.SNIPPETS_FOLDER
        for name in names:
            get_me_result = GetMe(self.context.cms_db_context).execute(name)
            if get_me_result.is_failure() and not isinstance(get_me_result, NoResult):
                click.echo('Something went wrong and it was not possible to perform the operation.')
                continue
            snippet = get_me_result.value()
            if snippet is None:
                click.echo(f'Snippet {name} does not exists.')
                continue
            self.build_local_backup(name)
            html_content = snippet['content']
            del snippet['content']
            if not os.path.exists(snippets_folder):
                os.makedirs(snippets_folder)
            spec_file_destination_path = f'{snippets_folder}/{name}.json'
            spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
            spec_file.write(json_util.dumps(snippet, indent=4))
            spec_file.close()
            content_file_destination_path = f'{snippets_folder}/{name}.html'
            content_file = open(content_file_destination_path, mode="w", encoding="utf-8")
            content_file.write(html_content)
            content_file.close()
            click.echo(f'Snippet {name} pulled successfully from {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')

    def build_local_backup(self, name):
        click.echo('Building local backup...')
        snippets_folder = self.context.cms_core_context.SNIPPETS_FOLDER
        backups_folder_path = f'{snippets_folder}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        sufix = round(time.time())
        local_spec_file_path = f'{snippets_folder}/{name}.json'
        local_content_file_path = f'{snippets_folder}/{name}.html'
        backup_spec_file_path = f'{snippets_folder}/.bak/{name}-local-{sufix}.json'
        backup_content_file_path = f'{snippets_folder}/.bak/{name}-local-{sufix}.html'
        if os.path.exists(local_spec_file_path):
            copyfile(local_spec_file_path, backup_spec_file_path)
        if os.path.exists(local_content_file_path):
            copyfile(local_content_file_path, backup_content_file_path)
