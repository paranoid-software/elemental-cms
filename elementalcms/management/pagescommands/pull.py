import time
import os
from shutil import copyfile
from typing import Tuple, Optional

import click
from bson import json_util
from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetMeForLanguage, GetAll


class Pull:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, pages, drafts: bool) -> [Tuple]:

        if isinstance(pages, str):
            get_all_result = GetAll(self.context.cms_db_context).execute(drafts)
            pages_tuples = [] if get_all_result.is_failure() else [(item['name'], item['language'])
                                                                   for item in get_all_result.value()]
            if len(pages_tuples) == 0:
                click.echo('There are no pages to pull.')
                return []
        else:
            pages_tuples = pages
            # TODO: Support file names with paths

        root_folder_path = self.context.cms_core_context.PAGES_FOLDER

        backups_filepaths = []
        for page_tuple in pages_tuples:
            name = page_tuple[0]
            lang = page_tuple[1]
            get_me_result = GetMeForLanguage(self.context.cms_db_context).execute(name, lang, drafts, False)
            page = get_me_result.value()
            if page is None:
                if drafts:
                    click.echo(f'{name} ({lang}) does not have a draft version.')
                    continue
                click.echo(f'{name} ({lang}) has not been published.')
                continue
            backup_filepaths = self.build_local_backups(lang, name)
            html_content = page.pop('content')
            folder_path = f'{root_folder_path}/{lang}'
            os.makedirs(folder_path, exist_ok=True)
            spec_filepath = f'{folder_path}/{name.replace("/", "_")}.json'
            spec_file = open(spec_filepath, mode='w', encoding='utf-8')
            spec_file.write(json_util.dumps(page, indent=4))
            spec_file.close()
            content_filepath = f'{folder_path}/{name.replace("/", "_")}.html'
            content_file = open(content_filepath, mode='w', encoding='utf-8')
            content_file.write(html_content)
            content_file.close()
            click.echo(f'{name} ({lang}) pulled successfully.')
            if backup_filepaths is not None:
                backups_filepaths.append(backup_filepaths)
        return backups_filepaths

    def build_local_backups(self, lang, name) -> Optional[Tuple]:
        click.echo('Building local backups...')
        root_folder_path = self.context.cms_core_context.PAGES_FOLDER
        folder_path = f'{root_folder_path}/{lang}'
        backups_folder_path = f'{root_folder_path}/{lang}/.bak'
        os.makedirs(backups_folder_path, exist_ok=True)
        sufix = round(time.time())
        spec_filepath = f'{folder_path}/{name.replace("/", "_")}.json'
        content_filepath = f'{folder_path}/{name.replace("/", "_")}.html'
        spec_backup_filepath = f'{backups_folder_path}/{name.replace("/", "_")}-local-{sufix}.json'
        content_backup_filepath = f'{backups_folder_path}/{name.replace("/", "_")}-local-{sufix}.html'
        if os.path.exists(spec_filepath):
            copyfile(spec_filepath, spec_backup_filepath)
        if os.path.exists(content_filepath):
            copyfile(content_filepath, content_backup_filepath)
        return spec_backup_filepath, content_backup_filepath
