import time
import os
from typing import Optional, Tuple

import click
from bson import json_util
from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetMeForLanguage, UpdateOne, RemoveOne


class Unpublish:
    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, pages_tuples) -> [Tuple]:

        backups_filepaths = []
        for page_tuple in pages_tuples:

            name = page_tuple[0]
            lang = page_tuple[1]

            get_page_result = GetMeForLanguage(self.context.cms_db_context).execute(name, lang, False, False)
            page = get_page_result.value()

            if page is None:
                click.echo(f'{name} ({lang}) is not published yet.')
                return None

            _id = page['_id']

            get_draft_result = GetMeForLanguage(self.context.cms_db_context).execute(name, lang, True, False)
            draft = get_draft_result.value()

            if draft is None:
                UpdateOne(self.context.cms_db_context).execute(_id, page, True)

            RemoveOne(self.context.cms_db_context).execute(_id)
            click.echo(f'{name} ({lang}) unpublished successfully.')
            backups_filepaths.append(self.build_page_backup(page))

        return backups_filepaths

    def build_page_backup(self, page) -> Tuple:
        click.echo('Building backups...')
        backups_folder_path = f'{self.context.cms_core_context.PAGES_FOLDER}/{page["language"]}/.bak'
        os.makedirs(backups_folder_path, exist_ok=True)
        html_content = page.pop('content', '')
        sufix = round(time.time())
        spec_backup_filepath = f'{backups_folder_path}/{page["name"].replace("/", "_")}-{sufix}.json'
        spec_backup_file = open(spec_backup_filepath, mode='w', encoding="utf-8")
        spec_backup_file.write(json_util.dumps(page, indent=4))
        spec_backup_file.close()
        content_backup_filepath = f'{backups_folder_path}/{page["name"].replace("/", "_")}-{sufix}.html'
        content_backup_file = open(content_backup_filepath, mode='w', encoding='utf-8')
        content_backup_file.write(html_content)
        content_backup_file.close()
        return spec_backup_filepath, content_backup_filepath
