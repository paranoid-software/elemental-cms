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

    def exec(self, snippets) -> [Tuple]:
        if isinstance(snippets, str):
            get_all_result = GetAll(self.context.cms_db_context).execute()
            snippets_tuples = [] if get_all_result.is_failure() else [(item['name'])
                                                                      for item in get_all_result.value()]
            if len(snippets_tuples) == 0:
                click.echo('There are no snippets to pull.')
                return []
        else:
            snippets_tuples = snippets
            # TODO: Support file names with paths

        backups_filepaths = []
        for name in snippets_tuples:
            get_me_result = GetMe(self.context.cms_db_context).execute(name)
            snippet = get_me_result.value()
            if snippet is None:
                click.echo(f'Snippet {name} does not exist.')
                continue
            folder_path = self.context.cms_core_context.SNIPPETS_FOLDER
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            spec_filepath = f'{folder_path}/{name}.json'
            content_filepath = f'{folder_path}/{name}.html'
            backup_filespaths = self.build_local_backups(folder_path, spec_filepath, content_filepath, name)
            html_content = snippet.pop('content', '')
            spec_file = open(spec_filepath, mode='w', encoding='utf-8')
            spec_file.write(json_util.dumps(snippet, indent=4))
            spec_file.close()
            content_file = open(content_filepath, mode='w', encoding='utf-8')
            content_file.write(html_content)
            content_file.close()
            click.echo(f'Snippet {name} pulled successfully.')
            if backup_filespaths is not None:
                backups_filepaths.append(backup_filespaths)
        return backups_filepaths

    @staticmethod
    def build_local_backups(folder_path, spec_filepath, content_filepath, clean_file_name) -> Optional[Tuple]:
        click.echo('Building local backups...')
        suffix = round(time.time())
        backups_folder_path = f'{folder_path}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        if os.path.exists(spec_filepath) and os.path.exists(content_filepath):
            spec_backup_filepath = f'{backups_folder_path}/{clean_file_name}-{suffix}.json'
            copyfile(spec_filepath, spec_backup_filepath)
            content_backup_filepath = f'{backups_folder_path}/{clean_file_name}-{suffix}.html'
            copyfile(content_filepath, content_backup_filepath)
            return spec_backup_filepath, content_backup_filepath
        return None
