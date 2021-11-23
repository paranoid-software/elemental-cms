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

    @staticmethod
    @command(name='list',
             help='Snippets list.')
    @pass_context
    def list(ctx):
        List(ctx).exec()

    @staticmethod
    @command(name='create', help='Create a new snippet on your local workspace.')
    @option('--name',
            '-n',
            required=True,
            help='Snippet name. It must be unique, lowercased and it can not contains special characters.')
    @pass_context
    def create(ctx, name):
        Create(ctx).exec(name)

    @staticmethod
    @command(name='push',
             help='Push snippet(s) specs into the CMS database.')
    @option('--all',
            is_flag=True,
            help='Push all snippets.')
    @option('--snippet',
            '-s',
            multiple=True,
            help='Name for the spec to be pushed. For example: push -s nav-bar')
    @constraint(RequireExactly(1), ['all', 'snippet'])
    @pass_context
    def push(ctx, **params):
        if params['all']:
            click.echo('Operation not ready yet.')
            return
        Push(ctx).exec(params['snippet'])

    @staticmethod
    @command(name='pull',
             help='Pull snippet(s) specs from the CMS database.')
    @option('--all',
            is_flag=True,
            help='Pull all snippets.')
    @option('--snippet',
            '-s',
            multiple=True,
            help='Name for the snippet to be pulled. For example: pull -d bootstrap application/javascript')
    @constraint(RequireExactly(1), ['all', 'snippet'])
    @pass_context
    def pull(ctx, **params):
        if params['all']:
            click.echo('Operation not ready yet.')
            return
        Pull(ctx).exec(params['snippet'])

    @staticmethod
    @command(name='remove', help='Remove an snippet.')
    @option('--name',
            '-n',
            required=True,
            help='Name of snippet to be removed.')
    @pass_context
    def remove(ctx, name):
        pass
        Remove(ctx).exec(name)
