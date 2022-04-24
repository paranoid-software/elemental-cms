from typing import Tuple

import click
from cloup import constraint, option, command, pass_context
from cloup.constraints import RequireExactly

from .snippetscommands import Create, List, Push, Pull, Remove


class Snippets(click.Group):

    def __init__(self):
        super(Snippets, self).__init__()
        self.name = 'snippets'
        self.add_command(self.list)
        self.add_command(self.create)
        self.add_command(self.remove)
        self.add_command(self.push)
        self.add_command(self.pull)

        # TODO: Add command to find differences between local workspace and CMS database

    @staticmethod
    @command(name='list',
             help='Display snippets list.')
    @pass_context
    def list(ctx):
        List(ctx).exec()

    @staticmethod
    @command(name='create', help='Create a new snippet at local workspace.')
    @option('--snippet',
            '-s',
            required=True,
            help='Snippet name. It must be unique, lowercased and it can not contains special characters.')
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
            help='Name for the snippet to be removed. For example: remove -s header')
    @pass_context
    def remove(ctx, snippet) -> Tuple:
        return Remove(ctx).exec(snippet)
