import time
import os
import click
from bson import json_util
from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.pages import GetMe, UpdateOne, RemoveOne


class Unpublish:
    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, name, lang):
        get_page_result = GetMe(self.context.cms_db_context).execute(name, lang, False, False)
        if get_page_result.is_failure():
            if not isinstance(get_page_result, NoResult):
                click.echo('Something went wrong and it was not possible to complete the operation.')
                return
        page = get_page_result.value()
        if page is None:
            click.echo(f'Page {name} in "{lang}" language is not published yet.')
            return
        get_draft_result = GetMe(self.context.cms_db_context).execute(name, lang, True, False)
        if get_draft_result.is_failure():
            if not isinstance(get_draft_result, NoResult):
                click.echo('Something went wrong and it was not possible to complete the operation.')
                return
        _id = page['_id']
        draft = get_draft_result.value()
        if draft is None:
            update_draft_result = UpdateOne(self.context.cms_db_context).execute(_id, page, True)
            if update_draft_result.is_failure():
                click.echo(
                    f'Something went wrong and it was not possible to publish page {name} into {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')
                return
        self.build_page_backup(page)
        RemoveOne(self.context.cms_db_context).execute(_id)
        click.echo(f'Page {name} unpublished successfully from {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')

    def build_page_backup(self, page):
        click.echo('Building backup...')
        html_content = page['content']
        del page['content']
        backups_folder_path = f'{self.context.cms_core_context.PAGES_FOLDER}/{page["language"]}/.bak'
        if not os.path.exists(backups_folder_path):
            os.makedirs(backups_folder_path)
        sufix = round(time.time())
        spec_file_destination_path = f'{backups_folder_path}/{page["name"]}-{sufix}.json'
        spec_file = open(spec_file_destination_path, mode="w", encoding="utf-8")
        spec_file.write(json_util.dumps(page, indent=4))
        spec_file.close()
        content_file_destination_path = f'{backups_folder_path}/{page["name"]}-{sufix}.html'
        content_file = open(content_file_destination_path, mode="w", encoding="utf-8")
        content_file.write(html_content)
        content_file.close()
