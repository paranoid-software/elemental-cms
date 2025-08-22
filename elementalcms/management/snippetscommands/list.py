import json
import os
import click
from bson import json_util

from elementalcms.core import ElementalContext
from elementalcms.services.snippets import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def has_local_changes(self, db_snippet) -> bool:
        folder_path = self.context.cms_core_context.SNIPPETS_FOLDER
        name = db_snippet['name']
        
        # Check if local files exist
        spec_path = f'{folder_path}/{name}.json'
        content_path = f'{folder_path}/{name}.html'
        if not os.path.exists(spec_path) or not os.path.exists(content_path):
            return True  # Missing local files is a difference!
            
        # Compare spec (excluding content and timestamps)
        with open(spec_path, encoding='utf-8') as f:
            local_spec = json_util.loads(f.read())
            db_spec = json_util.loads(json_util.dumps(db_snippet))  # Clone to avoid modifying original
            
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
            if local_content != db_snippet.get('content', ''):
                return True
                
        return False

    def get_local_snippets(self):
        folder_path = self.context.cms_core_context.SNIPPETS_FOLDER
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        local_snippets = set()
        for file in os.listdir(folder_path):
            if file.endswith('.json'):
                local_snippets.add(file[:-5])  # Remove .json extension
        return local_snippets

    def exec(self):
        result = GetAll(self.context.cms_db_context).execute()
        db_snippets = result.value() if not result.is_failure() else []
        db_names = {s['name'] for s in db_snippets}
        local_names = self.get_local_snippets()
        all_names = sorted(db_names | local_names)
        
        if not all_names:
            click.echo('There are no snippets to list. Create your first one by using the [snippets create] command.')
            return
            
        for name in all_names:
            if name in db_names:
                # Snippet exists in DB
                snippet = next(s for s in db_snippets if s['name'] == name)
                indicator = '*' if self.has_local_changes(snippet) else ' '
            else:
                # Snippet only exists locally
                indicator = '*'  # Local-only is a difference
            click.echo(f'{indicator} {name}')
