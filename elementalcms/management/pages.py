from typing import Tuple, Optional

import click
from cloup import constraint, option, command, pass_context
from cloup.constraints import RequireExactly

from .pagescommands import Create, Remove, Push, Pull, List, Publish, Unpublish


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

        # TODO: Add command to find differences between local workspace and CMS database

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
    @option('--page',
            '-p',
            nargs=2,
            required=True,
            multiple=True,
            help='Name and language for the page(s) to be published. For example: publish -p home en -p home es')
    @pass_context
    def publish(ctx, page) -> [Tuple]:
        return Publish(ctx).exec(page)

    @staticmethod
    @command(name='unpublish',
             help='Unpublish one or more pages.')
    @option('--page',
            '-p',
            nargs=2,
            required=True,
            multiple=True,
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
            help='Name and language for the page to be pulled. For example: remove -p home es')
    @pass_context
    def remove(ctx, page) -> Optional[Tuple]:
        return Remove(ctx).exec(page)
