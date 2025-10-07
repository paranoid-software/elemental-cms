from typing import Tuple
import os
import json

import click
from cloup import constraint, option, command, pass_context
from cloup.constraints import RequireExactly

from .snippetscommands import Create, List, Push, Pull, Remove, Diff


def complete_snippet_name(ctx, param, incomplete):
    """
    Shell completion function for snippet names (Click 8.0+ compatible).
    Returns a list of snippet names that match the incomplete input.
    
    Args:
        ctx: Click context
        param: The parameter being completed
        incomplete: The partial value being completed
        
    Returns:
        List of matching snippet names
    """
    from click.shell_completion import CompletionItem
    
    snippets = []
    
    try:
        # Try to read the .elemental file to get config
        if not os.path.exists('.elemental'):
            return snippets
            
        with open('.elemental', encoding='utf-8') as init_file:
            init_metadata = json.load(init_file)
            config_filepath = init_metadata.get('configFilePath')
            
        if not config_filepath or not os.path.exists(config_filepath):
            return snippets
            
        with open(config_filepath, encoding='utf-8') as config_file:
            config = json.load(config_file)
            snippets_folder = config.get('cmsCoreContext', {}).get('SNIPPETS_FOLDER', 'snippets')
        
        # Get all snippet names from the snippets folder
        if os.path.exists(snippets_folder):
            files = os.listdir(snippets_folder)
            # Extract unique snippet names (files without extensions)
            snippet_names = set()
            for file in files:
                if file.endswith('.json') or file.endswith('.html'):
                    snippet_names.add(os.path.splitext(file)[0])
            
            # Filter by incomplete text and return as CompletionItem objects
            snippets = [
                CompletionItem(name)
                for name in sorted(snippet_names)
                if name.startswith(incomplete)
            ]
    except Exception:
        # If anything fails, just return empty list
        pass
    
    return snippets


class Snippets(click.Group):

    def __init__(self):
        super(Snippets, self).__init__()
        self.name = 'snippets'
        self.add_command(self.list)
        self.add_command(self.create)
        self.add_command(self.remove)
        self.add_command(self.push)
        self.add_command(self.pull)
        self.add_command(self.diff)

        # TODO: Add command to find differences between local workspace and CMS database

    @staticmethod
    @command(name='list',
             help='Display snippets list. An asterisk (*) indicates snippets that: have local changes, are missing local files, or exist locally but not in the database.')
    @pass_context
    def list(ctx):
        List(ctx).exec()

    @staticmethod
    @command(name='create', help='Create a new snippet at local workspace.')
    @option('--snippet',
            '-s',
            required=True,
            help='Snippet name. Must be: lowercase, start with a letter, and contain only letters, numbers and hyphens (e.g., nav-bar, footer-2).')
    @pass_context
    def create(ctx, snippet):
        Create(ctx).exec(snippet)

    @staticmethod
    @command(name='push',
             help='Push snippet(s) specs to the CMS database.')
    @option('--all',
            is_flag=True,
            help='Push all snippets.')
    @option('--snippet',
            '-s',
            multiple=True,
            shell_complete=complete_snippet_name,
            help='Name for the snippet(s) to be pushed. For example: push -s nav-bar-plugster')
    @constraint(RequireExactly(1), ['all', 'snippet'])
    @pass_context
    def push(ctx, **params) -> [Tuple]:
        if params['all']:
            return Push(ctx).exec('*')
        return Push(ctx).exec(params['snippet'])

    @staticmethod
    @command(name='pull',
             help='Pull snippet(s) specs from the CMS database.')
    @option('--all',
            is_flag=True,
            help='Pull all snippets.')
    @option('--snippet',
            '-s',
            multiple=True,
            shell_complete=complete_snippet_name,
            help='Name for the snippet(s) to be pulled. For example: pull -s header -s nav-bar')
    @constraint(RequireExactly(1), ['all', 'snippet'])
    @pass_context
    def pull(ctx, **params) -> [Tuple]:
        if params['all']:
            return Pull(ctx).exec('*')
        return Pull(ctx).exec(params['snippet'])

    @staticmethod
    @command(name='remove', help='Remove snippet from the CMS database.')
    @option('--snippet',
            '-s',
            required=True,
            shell_complete=complete_snippet_name,
            help='Name for the snippet to be removed. For example: remove -s header')
    @pass_context
    def remove(ctx, snippet) -> Tuple:
        return Remove(ctx).exec(snippet)

    @staticmethod
    @command(name='diff', help='Compare local and database versions of a snippet.')
    @option('--snippet',
            '-s',
            required=True,
            shell_complete=complete_snippet_name,
            help='Name of the snippet to compare.')
    @pass_context
    def diff(ctx, snippet) -> Tuple:
        return Diff(ctx).exec(snippet)
