from typing import Tuple

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
            help='Name and language for the page to be pushed. For example: push -p home en -p home es')
    @constraint(RequireExactly(1), ['all', 'page'])
    @pass_context
    def push(ctx, **params) -> [Tuple]:
        if params['all']:
            return Push(ctx).exec('*')
        return Push(ctx).exec(params['page'])

    @staticmethod
    @command(name='publish',
             help='Publish one especific localized page.')
    @option('--page',
            '-p',
            nargs=2,
            required=True,
            help='Page name and language. For example: publish -p home es')
    @pass_context
    def publish(ctx, page) -> [Tuple]:
        return Publish(ctx).exec(page)

    @staticmethod
    @command(name='unpublish',
             help='Unpublish an especific page.')
    @option('--name',
            '-n',
            required=True,
            help='Page name.')
    @option('--lang',
            '-l',
            required=True,
            help='Page language.')
    @pass_context
    def unpublish(ctx, name, lang):
        Unpublish(ctx).exec(name, lang)

    @staticmethod
    @command(name='pull',
             help='Pull page(s) specs and contents from the CMS database.')
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
            help='Use this option to pull the pages draft version.')
    @pass_context
    def pull(ctx, **params):
        if params['all']:
            click.echo('Operation not ready yet.')
            return
        Pull(ctx).exec(params['page'], params['drafts'])

    @staticmethod
    @command(name='remove', help='Remove an unpublished page. This command removes the page draft version; if you '
                                 'want to remove the page published version you must use the pages unpublish command.')
    @option('--name',
            '-n',
            required=True,
            help='Name of the page to be removed.')
    @option('--lang',
            '-l',
            required=True,
            help=f'Language version to be removed.')
    @pass_context
    def remove(ctx, name, lang):
        Remove(ctx).exec(name, lang)
