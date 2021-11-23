import time
import os

import click
from bson import json_util, ObjectId
from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, names_tuples):
        for name_tuple in names_tuples:
            name = name_tuple[0]
            lang = name_tuple[1]
            if lang not in self.context.cms_core_context.LANGUAGES:
                click.echo(f'"{lang}" language not supported.')
                continue
            pages_folder_path = self.context.cms_core_context.PAGES_FOLDER
            spec_file_path = f'{pages_folder_path}/{lang}/{name}.json'
            content_file_path = f'{pages_folder_path}/{lang}/{name}.html'
            if not os.path.exists(content_file_path):
                click.echo(f'There is no content file for page {name} in {lang} language.')
                continue
            with open(spec_file_path) as page_spec_content:
                try:
                    page_spec = json_util.loads(page_spec_content.read())
                    if '_id' not in page_spec:
                        click.echo(f'Spec invalid for page {name} in {lang} language.')
                        continue
                    if not ObjectId.is_valid(page_spec['_id']):
                        click.echo(f'Spec invalid for page {name} in {lang} language.')
                        continue
                    if 'name' not in page_spec:
                        click.echo(f'Spec invalid for page {name} in {lang} language.')
                        continue
                    if page_spec['name'] != name:
                        click.echo(f'Spec invalid for page {name} in {lang} language.')
                        continue
                    with open(content_file_path) as page_content:
                        page_spec['content'] = page_content.read()
                        _id = page_spec['_id']
                        self.build_draft_backup(_id)
                        update_me_result = UpdateOne(self.context.cms_db_context).execute(_id, page_spec, True)
                        if update_me_result.is_failure():
                            click.echo(f'Something went wrong and it was not possible to push page {name} into {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')
                            continue
                        click.echo(f'Page {name} pushed successfully into {self.context.cms_db_context.host_name}/{self.context.cms_db_context.database_name}.')
                except Exception as e:
                    click.echo(e)
                    click.echo(f'Spec invalid for page {name} in {lang} language.')

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
