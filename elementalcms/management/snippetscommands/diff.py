import os
import json
from typing import Tuple
import difflib

import click
from bson import json_util
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from elementalcms.core import ElementalContext
from elementalcms.services.snippets import GetMe


class Diff:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']
        self.console = Console()

    def get_local_files(self, name: str) -> Tuple[str, str]:
        """Get local spec and content files. Returns (spec_json, content_html)"""
        folder_path = self.context.cms_core_context.SNIPPETS_FOLDER
        spec_path = f'{folder_path}/{name}.json'
        content_path = f'{folder_path}/{name}.html'

        spec_json = None
        content_html = None

        if os.path.exists(spec_path):
            with open(spec_path, encoding='utf-8') as f:
                spec_json = f.read()

        if os.path.exists(content_path):
            with open(content_path, encoding='utf-8') as f:
                content_html = f.read()

        return spec_json, content_html

    def format_spec(self, spec: dict) -> str:
        """Format spec for display, removing timestamps and content"""
        display_spec = spec.copy()
        display_spec.pop('createdAt', None)
        display_spec.pop('lastModifiedAt', None)
        display_spec.pop('content', None)
        # Convert ObjectId to string format
        if '_id' in display_spec:
            display_spec['_id'] = {'$oid': str(display_spec['_id'])}
        return json.dumps(display_spec, indent=2)

    def show_diff(self, title: str, db_version: str, local_version: str, file_type: str, name: str):
        """Show unified diff between two versions"""
        if not db_version and not local_version:
            return False
            
        db_lines = db_version.splitlines(keepends=True) if db_version else []
        local_lines = local_version.splitlines(keepends=True) if local_version else []
        
        diff = list(difflib.unified_diff(
            db_lines, local_lines,
            fromfile=f"database/{name}.{file_type}",
            tofile=f"local/{name}.{file_type}",
            lineterm=""
        ))
        
        if not diff:
            return False
            
        diff_text = Text()
        diff_text.append(f"\n{title}:\n", style="bold")
        
        header_line = ""
        for line in diff:
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                header_line += line.rstrip('\n')
            else:
                if header_line:
                    # Split and color each part of the header
                    parts = header_line.split('@@')
                    if len(parts) > 1:
                        file_parts = parts[0].split('+++')
                        diff_text.append(file_parts[0], style="red")  # --- line
                        diff_text.append('+++' + file_parts[1], style="green")  # +++ line
                        diff_text.append('@@' + parts[1] + '@@\n', style="blue")  # @@ line
                    header_line = ""
                    diff_text.append('\n')  # Start content on new line
                
                # Style and append content lines
                if line.startswith('+'):
                    diff_text.append(line, style="green")
                elif line.startswith('-'):
                    diff_text.append(line, style="red")
                else:
                    diff_text.append(line)
                    
        if header_line:  # Handle case where there's only header
            diff_text.append(header_line + '\n', style="blue")
        
        self.console.print(diff_text)
        return True

    def exec(self, snippet_name: str) -> Tuple:
        # Handle path if SNIPPETS_FOLDER is provided
        folder_path = self.context.cms_core_context.SNIPPETS_FOLDER
        if snippet_name.startswith(folder_path + '/'):
            snippet_name = snippet_name[len(folder_path) + 1:]

        result = GetMe(self.context.cms_db_context).execute(snippet_name)
        if result.is_failure():
            click.echo(f'Snippet {snippet_name} not found in database.')
            return 1, None

        db_snippet = result.value()
        db_spec = self.format_spec(db_snippet)
        db_content = db_snippet.get('content', '')

        local_spec_json, local_content = self.get_local_files(snippet_name)
        
        if local_spec_json is None and local_content is None:
            click.echo(f'No local files found for snippet {snippet_name}.')
            return 1, None

        local_spec = None
        if local_spec_json:
            try:
                local_spec = self.format_spec(json_util.loads(local_spec_json))
            except json.JSONDecodeError:
                local_spec = local_spec_json  # Show raw if invalid JSON

        self.console.print(f"\n[bold]Snippet: {snippet_name}[/bold]")

        has_spec_diff = self.show_diff("Spec Changes", db_spec, local_spec, "json", snippet_name)
        has_content_diff = self.show_diff("Content Changes", db_content, local_content, "html", snippet_name)

        if not has_spec_diff and not has_content_diff:
            self.console.print("\n[bold green]No differences found[/bold green]")

        return 0, None
