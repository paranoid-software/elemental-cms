import time
import os
from shutil import copyfile
from typing import Optional, Tuple

import click
from bson import json_util
from elementalcms.core import ElementalContext
from elementalcms.services.snippets import GetMe, GetAll


class Pull:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, snippets):
        if isinstance(snippets, str):
            get_all_result = GetAll(self.context.cms_db_context).execute()
            snippets_tuples = [] if get_all_result.is_failure() else [(item['name'])
                                                                      for item in get_all_result.value()]
            if len(snippets_tuples) == 0:
                click.echo('There are no snippets to pull.')
                return []
        else:
            snippets_tuples = snippets

        backup_paths = []
        for element in snippets_tuples:
            name = element
            get_me_result = GetMe(self.context.cms_db_context).execute(name)
            snippet = get_me_result.value()
            if snippet is None:
                click.echo(f'Snippet {name} does not exist.')
                continue
            folder_path = self.context.cms_core_context.SNIPPETS_FOLDER
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            html_content = snippet['content']
            spec_file_path = f'{folder_path}/{name}.json'
            content_file_path = f'{folder_path}/{name}.html'
            backup_files_paths = self.build_local_backups(folder_path, spec_file_path, content_file_path, name)
            del snippet['content']
            spec_file = open(spec_file_path, mode="w", encoding="utf-8")
            spec_file.write(json_util.dumps(snippet, indent=4))
            spec_file.close()
            content_file = open(content_file_path, mode="w", encoding="utf-8")
            content_file.write(html_content)
            content_file.close()
            click.echo(f'Snippet {name} pulled successfully.')
            if backup_files_paths is not None:
                backup_paths.append(backup_files_paths)
        return backup_paths

    @staticmethod
    def build_local_backups(folder_path, spec_file_path, content_file_path, clean_file_name) -> Optional[Tuple]:
        click.echo('Building local backup...')
        suffix = round(time.time())
        backups_folder_path = f'{folder_path}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        if os.path.exists(spec_file_path) and os.path.exists(content_file_path):
            spec_backup_file_path = f'{backups_folder_path}/{clean_file_name}-{suffix}.json'
            copyfile(spec_file_path, spec_backup_file_path)
            content_backup_file_path = f'{backups_folder_path}/{clean_file_name}-{suffix}.html'
            copyfile(content_file_path, content_backup_file_path)
            return spec_backup_file_path, content_file_path
        return None
