import time
import os
from shutil import copyfile

import click
from bson import json_util
from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.pages import GetMe


class Pull:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, names_tuples, drafts):
        pages_folder_path = self.context.cms_core_context.PAGES_FOLDER
        for name_tuple in names_tuples:
            name = name_tuple[0]
            lang = name_tuple[1]
            get_pages_result = GetMe(self.context.cms_db_context).execute(name, lang, drafts, False)
            if get_pages_result.is_failure() and not isinstance(get_pages_result, NoResult):
                click.echo('Something went wrong and it was not possible to perform the operation.')
                continue
            page = get_pages_result.value()
            if page is None:
                if drafts:
                    click.echo(f'Page {name} in "{lang}" language do not have draft version.')
                    continue
                click.echo(f'Page {name} in "{lang}" language has not been published.')
                continue
            self.build_local_backup(lang, name)
            html_content = page['content']
            del page['content']
            if not os.path.exists(f'{pages_folder_path}/{lang}'):
                os.makedirs(f'{pages_folder_path}/{lang}')
            spec_file_destination_path = f'{pages_folder_path}/{lang}/{name}.json'
            spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
            spec_file.write(json_util.dumps(page, indent=4))
            spec_file.close()
            content_file_destination_path = f'{pages_folder_path}/{lang}/{name}.html'
            content_file = open(content_file_destination_path, mode="w", encoding="utf-8")
            content_file.write(html_content)
            content_file.close()
            click.echo(f'Page {name} pulled successfully from {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')

    def build_local_backup(self, lang, name):
        click.echo('Building local backup...')
        pages_folder_path = self.context.cms_core_context.PAGES_FOLDER
        backups_folder_path = f'{pages_folder_path}/{lang}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        sufix = round(time.time())
        local_spec_file_path = f'{pages_folder_path}/{lang}/{name}.json'
        local_content_file_path = f'{pages_folder_path}/{lang}/{name}.html'
        backup_spec_file_path = f'{pages_folder_path}/{lang}/.bak/{name}-local-{sufix}.json'
        backup_content_file_path = f'{pages_folder_path}/{lang}/.bak/{name}-local-{sufix}.html'
        if os.path.exists(local_spec_file_path):
            copyfile(local_spec_file_path, backup_spec_file_path)
        if os.path.exists(local_content_file_path):
            copyfile(local_content_file_path, backup_content_file_path)
