import json
import os
import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def has_local_changes(self, db_page) -> bool:
        folder_path = f'{self.context.cms_core_context.PAGES_FOLDER}/{db_page["language"]}'
        name = db_page['name']
        
        # Check if local files exist
        spec_path = f'{folder_path}/{name.replace("/", "_")}.json'
        content_path = f'{folder_path}/{name.replace("/", "_")}.html'
        if not os.path.exists(spec_path) or not os.path.exists(content_path):
            return True  # Missing local files is a difference!
            
        # Compare spec (excluding content and timestamps)
        with open(spec_path, encoding='utf-8') as f:
            local_spec = json_util.loads(f.read())
            db_spec = json_util.loads(json_util.dumps(db_page))  # Clone to avoid modifying original
            
            # Remove fields we don't want to compare
            for spec in [local_spec, db_spec]:
                spec.pop('content', None)
                spec.pop('createdAt', None)
                spec.pop('lastModifiedAt', None)
            
            if local_spec != db_spec:
                return True
                
        # Compare content
        with open(content_path, encoding='utf-8') as f:
            local_content = f.read()
            if local_content != db_page.get('content', ''):
                return True
                
        return False

    def get_local_pages(self):
        root_folder_path = self.context.cms_core_context.PAGES_FOLDER
        if not os.path.exists(root_folder_path):
            os.makedirs(root_folder_path)
        
        local_pages = set()
        for lang in self.context.cms_core_context.LANGUAGES:
            folder_path = f'{root_folder_path}/{lang}'
            if not os.path.exists(folder_path):
                continue
            for file in os.listdir(folder_path):
                if file.endswith('.json'):
                    name = file[:-5].replace('_', '/')  # Remove .json and restore slashes
                    local_pages.add((name, lang))
        return local_pages

    def exec(self, drafts=False):
        result = GetAll(self.context.cms_db_context).execute(drafts)
        db_pages = result.value() if not result.is_failure() else []
        db_tuples = {(p['name'], p['language']) for p in db_pages}
        local_tuples = self.get_local_pages()
        all_tuples = sorted(db_tuples | local_tuples)
        
        if not all_tuples:
            click.echo('There are no pages to list. Create your first one by using the [pages create] command.')
            return
            
        for name, lang in all_tuples:
            if (name, lang) in db_tuples:
                # Page exists in DB
                page = next(p for p in db_pages if p['name'] == name and p['language'] == lang)
                indicator = '*' if self.has_local_changes(page) else ' '
                title = page.get('title', '')
            else:
                # Page only exists locally
                indicator = '*'  # Local-only is a difference
                title = 'Local only'
            click.echo(f'{indicator} {name} ({lang}) -> {title}')
