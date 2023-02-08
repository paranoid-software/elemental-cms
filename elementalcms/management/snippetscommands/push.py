import time
import os
from typing import Tuple, Optional
import click
from bson import json_util, ObjectId

from elementalcms.core import ElementalContext
from elementalcms.services.snippets import GetOne, UpdateOne


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, snippets) -> [Tuple]:

        folder_path = self.context.cms_core_context.SNIPPETS_FOLDER

        if isinstance(snippets, str):
            snippets_tuples = []
            for r, d, f in os.walk(folder_path):
                if '.bak' in r:
                    continue
                for file in f:
                    if '.json' not in file:
                        continue
                    snippets_tuples.append((file.split('.json')[0]))
            if len(snippets_tuples) == 0:
                click.echo('There are no snippets to push.')
                return
        else:
            snippets_tuples = snippets
            # TODO: Support file names with paths

        backups_filepaths = []
        for name in snippets_tuples:
            spec_filepath = f'{folder_path}/{name}.json'
            content_filepath = f'{folder_path}/{name}.html'
            if not os.path.exists(spec_filepath):
                click.echo(f'There is no spec file for {name} snippet.')
                return
            if not os.path.exists(content_filepath):
                click.echo(f'There is no content file for {name} snippet.')
                return
            with open(spec_filepath, encoding='utf-8') as spec_file:
                try:
                    snippet = json_util.loads(spec_file.read())
                except Exception as e:
                    click.echo(f'Invalid spec for {name} - {e}')
                    continue
                if '_id' not in snippet:
                    click.echo(f'Missing spec _id for: {name}.')
                    return
                if not ObjectId.is_valid(snippet['_id']):
                    click.echo(f'Invalid spec _id for: {name}.')
                    return
                if 'name' not in snippet:
                    click.echo(f'Missing spec name for: {name}.')
                    return
                if snippet['name'] != name:
                    click.echo(f'Invalid spec name for: {name}.')
                    return
                with open(content_filepath, encoding='utf-8') as content_file:
                    snippet['content'] = content_file.read()
                    _id = snippet['_id']
                    backup_filepaths = self.build_backups(_id)
                    UpdateOne(self.context.cms_db_context).execute(_id, snippet)
                    click.echo(f'Snippet {name} pushed successfully.')
                    if backup_filepaths is not None:
                        backups_filepaths.append(backup_filepaths)
        return backups_filepaths

    def build_backups(self, _id) -> Optional[Tuple]:
        get_one_result = GetOne(self.context.cms_db_context).execute(_id)
        if get_one_result.is_failure():
            return None
        click.echo('Building backups...')
        backups_folder_path = f'{self.context.cms_core_context.SNIPPETS_FOLDER}/.bak'
        os.makedirs(backups_folder_path, exist_ok=True)
        snippet = get_one_result.value()
        html_content = snippet.pop('content', '')
        sufix = round(time.time())
        spec_backup_filepath = f'{backups_folder_path}/{snippet["name"]}-{sufix}.json'
        spec_backup_file = open(spec_backup_filepath, mode='w', encoding='utf-8')
        spec_backup_file.write(json_util.dumps(snippet, indent=4))
        spec_backup_file.close()
        content_backup_filepath = f'{backups_folder_path}/{snippet["name"]}-{sufix}.html'
        content_backup_file = open(content_backup_filepath, mode='w', encoding='utf-8')
        content_backup_file.write(html_content)
        content_backup_file.close()
        return spec_backup_filepath, content_backup_filepath
