import time
import os
from typing import Tuple, Optional

import click
from bson import json_util, ObjectId
from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, pages) -> [Tuple]:

        root_folder_path = self.context.cms_core_context.PAGES_FOLDER

        if isinstance(pages, str):
            pages_tuples = []
            for r, d, f in os.walk(root_folder_path):
                if '.bak' in r:
                    continue
                for file in f:
                    if '.json' not in file:
                        continue
                    pages_tuples.append((file.split('.json')[0].replace('_', '/'), r.split('/')[-1]))
            if len(pages_tuples) == 0:
                click.echo('There are no pages to push.')
                return
        else:
            pages_tuples = pages
            # TODO: Support file names with paths

        backups_filepaths = []
        for page_tuple in pages_tuples:
            name = page_tuple[0]
            lang = page_tuple[1]
            if lang not in self.context.cms_core_context.LANGUAGES:
                click.echo(f'"{lang}" language not supported.')
                continue
            folder_path = f'{root_folder_path}/{lang}'
            spec_filepath = f'{folder_path}/{name.replace("/", "_")}.json'
            content_filepath = f'{folder_path}/{name.replace("/", "_")}.html'
            if not os.path.exists(spec_filepath):
                click.echo(f'There is no spec file for page {name} ({lang})')
                continue
            if not os.path.exists(content_filepath):
                click.echo(f'There is no content file for page {name} ({lang})')
                continue
            with open(spec_filepath, encoding='utf-8') as spec_file:
                try:
                    page = json_util.loads(spec_file.read())
                except Exception as e:
                    click.echo(f'Invalid spec for page {name} ({lang}) - {e}')
                    continue
                if '_id' not in page:
                    click.echo(f'Missing spec _id for: {name} ({lang})')
                    continue
                if not ObjectId.is_valid(page['_id']):
                    click.echo(f'Invalid spec _id for: {name} ({lang})')
                    continue
                if 'name' not in page:
                    click.echo(f'Missing spec name for: {name} ({lang})')
                    continue
                if page['name'] != name:
                    click.echo(f'Invalid spec name for: {name} ({lang})')
                    continue
                with open(content_filepath, encoding='utf-8') as content_file:
                    _id = page['_id']
                    page['content'] = content_file.read()
                    backup_filepaths = self.build_draft_backups(_id)
                    UpdateOne(self.context.cms_db_context).execute(_id, page, True)
                    click.echo(f'Page {name} ({lang}) pushed successfully.')
                    if backup_filepaths is not None:
                        backups_filepaths.append(backup_filepaths)
        return backups_filepaths

    def build_draft_backups(self, _id) -> Optional[Tuple]:
        get_one_result = GetOne(self.context.cms_db_context).execute(_id, True)
        if get_one_result.is_failure():
            return None
        click.echo('Building backups...')
        page = get_one_result.value()
        backups_folder_path = f'{self.context.cms_core_context.PAGES_FOLDER}/{page["language"]}/.bak'
        os.makedirs(backups_folder_path, exist_ok=True)
        html_content = page.pop('content', '')
        sufix = round(time.time())
        spec_backup_filepath = f'{backups_folder_path}/{page["name"].replace("/", "_")}-draft-{sufix}.json'
        spec_backup_file = open(spec_backup_filepath, mode='w', encoding='utf-8')
        spec_backup_file.write(json_util.dumps(page, indent=4))
        spec_backup_file.close()
        content_backup_filepath = f'{backups_folder_path}/{page["name"].replace("/", "_")}-draft-{sufix}.html'
        content_backup_file = open(content_backup_filepath, mode='w', encoding='utf-8')
        content_backup_file.write(html_content)
        content_backup_file.close()
        return spec_backup_filepath, content_backup_filepath
