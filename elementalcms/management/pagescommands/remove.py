import os
import time
from typing import Optional, Tuple

import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetMeForLanguage, RemoveOne


class Remove:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, page_tuple) -> Optional[Tuple]:

        name = page_tuple[0]
        lang = page_tuple[1]

        get_page_result = GetMeForLanguage(self.context.cms_db_context).execute(name, lang, False, False)
        page = get_page_result.value()

        if page is not None:
            click.echo(f'{name} ({lang}) has to be unpublished first, in order to be removed.')
            return None

        get_draft_result = GetMeForLanguage(self.context.cms_db_context).execute(name, lang, True, False)
        draft = get_draft_result.value()

        if draft is None:
            click.echo(f'{name} ({lang}) does not have a draft version.')
            return None

        RemoveOne(self.context.cms_db_context).execute(draft['_id'], True)
        click.echo(f'{name} ({lang}) removed successfully.')
        return self.build_draft_backups(draft)

    def build_draft_backups(self, draft) -> Tuple:
        click.echo('Building backup...')
        html_content = draft.pop('content', '')
        backups_folder_path = f'{self.context.cms_core_context.PAGES_FOLDER}/{draft["language"]}/.bak'
        os.makedirs(backups_folder_path, exist_ok=True)
        sufix = round(time.time())
        spec_backup_filepath = f'{backups_folder_path}/{draft["name"].replace("/", "_")}-draft-{sufix}.json'
        spec_backup_file = open(spec_backup_filepath, mode='w', encoding='utf-8')
        spec_backup_file.write(json_util.dumps(draft, indent=4))
        spec_backup_file.close()
        content_backup_filepath = f'{backups_folder_path}/{draft["name"].replace("/", "_")}-draft-{sufix}.html'
        content_backup_file = open(content_backup_filepath, mode='w', encoding='utf-8')
        content_backup_file.write(html_content)
        content_backup_file.close()
        return spec_backup_filepath, content_backup_filepath
