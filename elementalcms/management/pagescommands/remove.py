import os
import time

import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.pages import GetMe, RemoveOne, GetOne


class Remove:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, lang):

        get_page_result = GetMe(self.context.cms_db_context).execute(name, lang, False, False)
        if get_page_result.is_failure():
            if not isinstance(get_page_result, NoResult):
                click.echo('Something went wrong and it was not possible to complete the operation.')
                return

        page = get_page_result.value()
        if page is not None:
            click.echo(f'Page {name} in "{lang}" language has to be unpublished first, in order to be removed.')
            return

        get_draft_result = GetMe(self.context.cms_db_context).execute(name, lang, True, False)
        if get_draft_result.is_failure():
            if not isinstance(get_draft_result, NoResult):
                click.echo('Something went wrong and it was not possible to complete the operation.')
                return
        draft = get_draft_result.value()
        if draft is None:
            click.echo(f'Page {name} in "{lang}" language does not have a draft version.')
            return

        self.build_draft_backup(draft['_id'])

        RemoveOne(self.context.cms_db_context).execute(draft['_id'], True)
        click.echo(f'Page {name} in "{lang}" language removed successfully.')

    def build_draft_backup(self, _id):
        get_one_result = GetOne(self.context.cms_db_context).execute(_id, True)
        if get_one_result.is_failure():
            return
        click.echo('Building backup...')
        page = get_one_result.value()
        html_content = page['content']
        del page['content']
        backups_folder_path = f'{self.context.cms_core_context.PAGES_FOLDER}/{page["language"]}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        sufix = round(time.time())
        spec_file_destination_path = f'{backups_folder_path}/{page["name"]}-draft-{sufix}.json'
        spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
        spec_file.write(json_util.dumps(page, indent=4))
        spec_file.close()
        content_file_destination_path = f'{backups_folder_path}/{page["name"]}-draft-{sufix}.html'
        content_file = open(content_file_destination_path, mode="w", encoding="utf-8")
        content_file.write(html_content)
        content_file.close()
