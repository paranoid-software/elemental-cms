from typing import Tuple, Optional
import os
import json

import click
from cloup import constraint, option, command, pass_context
from cloup.constraints import RequireExactly

from .pagescommands import Create, Remove, Push, Pull, List, Publish, Unpublish, Diff


def complete_page_name_and_language(ctx, param, incomplete):
    """
    Shell completion function for page name and language pairs (Click 8.0+ compatible).
    Returns page names and languages based on local pages folder.
    
    Args:
        ctx: Click context
        param: The parameter being completed
        incomplete: The partial value being completed (tuple of current values)
        
    Returns:
        List of matching page names or languages
    """
    from click.shell_completion import CompletionItem
    
    completions = []
    
    try:
        # Try to read the .elemental file to get config
        if not os.path.exists('.elemental'):
            return completions
            
        with open('.elemental', encoding='utf-8') as init_file:
            init_metadata = json.load(init_file)
            config_filepath = init_metadata.get('configFilePath')
            
        if not config_filepath or not os.path.exists(config_filepath):
            return completions
            
        with open(config_filepath, encoding='utf-8') as config_file:
            config = json.load(config_file)
            pages_folder = config.get('cmsCoreContext', {}).get('PAGES_FOLDER', 'pages')
        
        # Check if pages folder exists
        if not os.path.exists(pages_folder):
            return completions
        
        # If incomplete is a tuple, we're completing subsequent values
        if isinstance(incomplete, tuple):
            # If we have one value already (the page name), complete language
            if len(incomplete) > 0:
                # Get available languages from folder structure
                languages = [
                    d for d in os.listdir(pages_folder)
                    if os.path.isdir(os.path.join(pages_folder, d)) and not d.startswith('.')
                ]
                last_value = incomplete[-1] if incomplete[-1] else ""
                completions = [
                    CompletionItem(lang)
                    for lang in sorted(languages)
                    if lang.startswith(last_value)
                ]
            else:
                # First value - complete page name
                completions = get_page_names_completions(pages_folder, "")
        else:
            # Single string - complete page name
            completions = get_page_names_completions(pages_folder, incomplete or "")
            
    except Exception:
        # If anything fails, just return empty list
        pass
    
    return completions


def get_page_names_completions(pages_folder: str, incomplete: str):
    """Get page name completions from all language folders"""
    from click.shell_completion import CompletionItem
    
    page_names = set()
    
    try:
        # Scan all language folders
        for lang_dir in os.listdir(pages_folder):
            lang_path = os.path.join(pages_folder, lang_dir)
            if not os.path.isdir(lang_path) or lang_dir.startswith('.'):
                continue
                
            # Get all page files in this language folder
            for file in os.listdir(lang_path):
                if file.endswith('.json') or file.endswith('.html'):
                    page_name = os.path.splitext(file)[0]
                    # Convert back from safe filename (underscores to slashes)
                    page_name = page_name.replace('_', '/')
                    page_names.add(page_name)
        
        # Filter by incomplete text and return as CompletionItem objects
        return [
            CompletionItem(name)
            for name in sorted(page_names)
            if name.startswith(incomplete)
        ]
    except Exception:
        return []


class Pages(click.Group):

    def __init__(self):
        super(Pages, self).__init__()
        self.name = 'pages'
        self.add_command(self.list)
        self.add_command(self.create)
        self.add_command(self.remove)
        self.add_command(self.push)
        self.add_command(self.pull)
        self.add_command(self.publish)
        self.add_command(self.unpublish)
        self.add_command(self.diff)

    @staticmethod
    @command(name='list',
             help='Display pages list.')
    @option('--drafts',
            is_flag=True,
            help='Display the draft pages list (false by default).')
    @pass_context
    def list(ctx, drafts):
        List(ctx).exec(drafts)

    @staticmethod
    @command(name='create', help='Create a new page on your local workspace.')
    @option('--page',
            '-p',
            nargs=2,
            required=True,
            help='Name and language for the page to be created. Name must be unique, lowercased and it can not '
                 'contains special characters but - or _. For example: create -p home en')
    @pass_context
    def create(ctx, page):
        Create(ctx).exec(page)

    @staticmethod
    @command(name='push',
             help='Push page(s) spec(s) and content(s) to the CMS database. '
                  'All pushed pages are stored initially at the draft collection.')
    @option('--all',
            is_flag=True,
            help='Push all pages.')
    @option('--page',
            '-p',
            nargs=2,
            multiple=True,
            shell_complete=complete_page_name_and_language,
            help='Name and language for the page(s) to be pushed. For example: push -p home en -p home es')
    @constraint(RequireExactly(1), ['all', 'page'])
    @pass_context
    def push(ctx, **params) -> [Tuple]:
        if params['all']:
            return Push(ctx).exec('*')
        return Push(ctx).exec(params['page'])

    @staticmethod
    @command(name='publish',
             help='Publish one or more pages.')
    @option('--all',
            is_flag=True,
            help='Publish all pages that have draft versions.')
    @option('--page',
            '-p',
            nargs=2,
            multiple=True,
            shell_complete=complete_page_name_and_language,
            help='Name and language for the page(s) to be published. For example: publish -p home en -p home es')
    @constraint(RequireExactly(1), ['all', 'page'])
    @pass_context
    def publish(ctx, **params) -> [Tuple]:
        if params['all']:
            return Publish(ctx).exec('*')
        return Publish(ctx).exec(params['page'])

    @staticmethod
    @command(name='unpublish',
             help='Unpublish one or more pages.')
    @option('--page',
            '-p',
            nargs=2,
            required=True,
            multiple=True,
            shell_complete=complete_page_name_and_language,
            help='Name and language for the page(s) to be unpublished. For example: unpublish -p home en -p home es')
    @pass_context
    def unpublish(ctx, page) -> [Tuple]:
        return Unpublish(ctx).exec(page)

    @staticmethod
    @command(name='pull',
             help='Pull page(s) spec(s) and content(s) from the CMS database.')
    @option('--all',
            is_flag=True,
            help='Pull all pages.')
    @option('--page',
            '-p',
            nargs=2,
            multiple=True,
            shell_complete=complete_page_name_and_language,
            help='Name and language for the page to be pulled. For example: pull -p home en -p home es')
    @constraint(RequireExactly(1), ['all', 'page'])
    @option('--drafts',
            is_flag=True,
            help='Use this option to pull the page(s) draft version.')
    @pass_context
    def pull(ctx, **params) -> [Tuple]:
        if params['all']:
            return Pull(ctx).exec('*', params['drafts'])
        return Pull(ctx).exec(params['page'], params['drafts'])

    @staticmethod
    @command(name='remove', help='Remove unpublished pages. This command removes the page draft version; if you '
                                 'want to remove the page published version you must use the pages unpublish command.')
    @option('--page',
            '-p',
            nargs=2,
            required=True,
            shell_complete=complete_page_name_and_language,
            help='Name and language for the page to be removed. For example: remove -p home es')
    @pass_context
    def remove(ctx, page) -> Optional[Tuple]:
        return Remove(ctx).exec(page)

    @staticmethod
    @command(name='diff', help='Compare local and database versions of a page.')
    @option('--page',
            '-p',
            nargs=2,
            required=True,
            shell_complete=complete_page_name_and_language,
            help='Name and language for the page to compare. For example: diff -p home en')
    @option('--drafts',
            is_flag=True,
            help='Compare against the draft version instead of the published version.')
    @pass_context
    def diff(ctx, page, drafts) -> Tuple:
        return Diff(ctx).exec(page, drafts)
