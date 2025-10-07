import os
import json
from typing import Tuple
import difflib

import click
from bson import json_util
from rich.console import Console
from rich.text import Text

from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetMeForLanguage


class Diff:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']
        self.console = Console()

    def get_local_files(self, name: str, language: str) -> Tuple[str, str]:
        """Get local spec and content files. Returns (spec_json, content_html)"""
        folder_path = self.context.cms_core_context.PAGES_FOLDER
        page_name_safe = name.replace("/", "_")
        spec_path = f'{folder_path}/{language}/{page_name_safe}.json'
        content_path = f'{folder_path}/{language}/{page_name_safe}.html'

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
                        if len(file_parts) >= 2:
                            diff_text.append(file_parts[0], style="red")  # --- line
                            diff_text.append('+++' + file_parts[1], style="green")  # +++ line
                            diff_text.append('@@' + parts[1] + '@@\n', style="blue")  # @@ line
                        else:
                            # Fallback if header format is unexpected
                            diff_text.append(header_line + '\n', style="blue")
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

    def exec(self, page_tuple: Tuple[str, str], drafts: bool = False) -> Tuple:
        page_name = page_tuple[0]
        language = page_tuple[1]

        result = GetMeForLanguage(self.context.cms_db_context).execute(page_name, language, drafts, False)
        
        if result.is_failure():
            if drafts:
                click.echo(f'Page {page_name} ({language}) draft version not found in database.')
            else:
                click.echo(f'Page {page_name} ({language}) not found in database.')
            return 1, None

        db_page = result.value()
        if db_page is None:
            if drafts:
                click.echo(f'Page {page_name} ({language}) does not have a draft version.')
            else:
                click.echo(f'Page {page_name} ({language}) has not been published.')
            return 1, None

        db_spec = self.format_spec(db_page)
        db_content = db_page.get('content', '')

        local_spec_json, local_content = self.get_local_files(page_name, language)
        
        if local_spec_json is None and local_content is None:
            click.echo(f'No local files found for page {page_name} ({language}).')
            return 1, None

        local_spec = None
        if local_spec_json:
            try:
                local_spec = self.format_spec(json_util.loads(local_spec_json))
            except json.JSONDecodeError:
                local_spec = local_spec_json  # Show raw if invalid JSON

        self.console.print(f"\n[bold]Page: {page_name} ({language}){' [DRAFT]' if drafts else ''}[/bold]")

        has_spec_diff = self.show_diff("Spec Changes", db_spec, local_spec, "json", page_name)
        has_content_diff = self.show_diff("Content Changes", db_content, local_content, "html", page_name)

        if not has_spec_diff and not has_content_diff:
            self.console.print("\n[bold green]No differences found[/bold green]")

        return 0, None

