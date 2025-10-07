from typing import Optional
import os
import json

from cloup import constraint, option, command, pass_context, Group
from cloup.constraints import RequireExactly

from .globaldepscommands import List, Create, Push, Pull, Remove


def complete_dep_name_and_type(ctx, param, incomplete):
    """
    Shell completion function for global dep name and type pairs (Click 8.0+ compatible).
    Returns dep names and types based on local global deps folder.
    
    Args:
        ctx: Click context
        param: The parameter being completed
        incomplete: The partial value being completed (tuple of current values)
        
    Returns:
        List of matching dep names or types
    """
    from click.shell_completion import CompletionItem
    
    # Valid types for global dependencies
    VALID_TYPES = ['text/css', 'application/javascript', 'module']
    
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
            global_deps_folder = config.get('cmsCoreContext', {}).get('GLOBAL_DEPS_FOLDER', 'global-deps')
        
        # Check if global deps folder exists
        if not os.path.exists(global_deps_folder):
            return completions
        
        # If incomplete is a tuple, we're completing subsequent values
        if isinstance(incomplete, tuple):
            # If we have one value already (the dep name), complete type
            if len(incomplete) > 0:
                last_value = incomplete[-1] if incomplete[-1] else ""
                completions = [
                    CompletionItem(dep_type)
                    for dep_type in VALID_TYPES
                    if dep_type.startswith(last_value)
                ]
            else:
                # First value - complete dep name
                completions = get_dep_names_completions(global_deps_folder, "")
        else:
            # Single string - complete dep name
            completions = get_dep_names_completions(global_deps_folder, incomplete or "")
            
    except Exception:
        # If anything fails, just return empty list
        pass
    
    return completions


def get_dep_names_completions(global_deps_folder: str, incomplete: str):
    """Get dep name completions from all type folders"""
    from click.shell_completion import CompletionItem
    
    dep_names = set()
    
    try:
        # Map folder names to types
        TYPE_FOLDERS = {
            'text_css': 'text/css',
            'application_javascript': 'application/javascript',
            'module': 'module'
        }
        
        # Scan all type folders
        for folder_name in TYPE_FOLDERS.keys():
            folder_path = os.path.join(global_deps_folder, folder_name)
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                continue
                
            # Get all dep files in this type folder
            for file in os.listdir(folder_path):
                if file.endswith('.json') and not file.startswith('.'):
                    # Read the file to get the name
                    try:
                        with open(os.path.join(folder_path, file), encoding='utf-8') as f:
                            dep_data = json.load(f)
                            if 'name' in dep_data:
                                dep_names.add(dep_data['name'])
                    except Exception:
                        # If file can't be read, just use filename without extension
                        dep_names.add(os.path.splitext(file)[0])
        
        # Filter by incomplete text and return as CompletionItem objects
        return [
            CompletionItem(name)
            for name in sorted(dep_names)
            if name.startswith(incomplete)
        ]
    except Exception:
        return []


class GlobalDeps(Group):

    def __init__(self):
        super(GlobalDeps, self).__init__()
        self.name = 'global-deps'
        self.add_command(self.list)
        self.add_command(self.create)
        self.add_command(self.push)
        self.add_command(self.pull)
        self.add_command(self.remove)

        # TODO: Add command to find differences between local workspace and CMS database

    @staticmethod
    @command(name='list',
             help='Display global dependencies list.')
    @pass_context
    def list(ctx):
        List(ctx).exec()

    @staticmethod
    @command(name='create',
             help='Create a new global dependency at local workspace.')
    @option('--dep',
            '-d',
            required=True,
            nargs=2,
            help='Name and type for the global dep(s) to be created; name must be unique, lowercase and it can not '
                 'contains special characters, and the type can be any of: text/css application/javascript or module. '
                 'For example create --dep jquery application/javascript')
    @pass_context
    def create(ctx, dep):
        Create(ctx).exec(dep[0], dep[1])

    @staticmethod
    @command(name='push',
             help='Push global dep(s) specs to the CMS database.')
    @option('--all',
            is_flag=True,
            help='Push all global dependencies.')
    @option('--dep',
            '-d',
            nargs=2,
            multiple=True,
            shell_complete=complete_dep_name_and_type,
            help='Name and type for the global dep(s) to be pushed. '
                 'For example: push -d bootstrap text/css -d bootstrap application/javascript')
    @constraint(RequireExactly(1), ['all', 'dep'])
    @pass_context
    def push(ctx, **params) -> [str]:
        if params['all']:
            return Push(ctx).exec('*')
        return Push(ctx).exec(params['dep'])

    @staticmethod
    @command(name='pull',
             help='Pull global dep(s) specs from the CMS database.')
    @option('--all',
            is_flag=True,
            help='Pull all global dependencies.')
    @option('--dep',
            '-d',
            nargs=2,
            multiple=True,
            shell_complete=complete_dep_name_and_type,
            help='Name and type for the global dep(s) to be pulled. '
                 'For example: pull -d bootstrap application/javascript')
    @constraint(RequireExactly(1), ['all', 'dep'])
    @pass_context
    def pull(ctx, **params) -> [str]:
        if params['all']:
            return Pull(ctx).exec('*')
        return Pull(ctx).exec(params['dep'])

    @staticmethod
    @command(name='remove', help='Remove global dependency from the CMS database.')
    @option('--dep',
            '-d',
            required=True,
            nargs=2,
            shell_complete=complete_dep_name_and_type,
            help='Name and type for the global dependency to be removed. '
                 'For example: remove --dep bootstrap application/javascript')
    @pass_context
    def remove(ctx, dep) -> Optional[str]:
        return Remove(ctx).exec(dep[0], dep[1])
