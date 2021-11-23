import click
from cloup import constraint, option, command, pass_context
from cloup.constraints import RequireExactly

from .globaldepscommands import List, Create, Push, Pull, Remove


class GlobalDeps(click.Group):

    def __init__(self):
        super(GlobalDeps, self).__init__()
        self.name = 'global-deps'
        self.add_command(self.list)
        self.add_command(self.create)
        self.add_command(self.remove)
        self.add_command(self.push)
        self.add_command(self.pull)

    @staticmethod
    @command(name='list',
             help='Global deps list.')
    @pass_context
    def list(ctx):
        List(ctx).exec()

    @staticmethod
    @command(name='create', help='Create a new global dependency on your local workspace.')
    @option('--name',
            '-n',
            required=True,
            help='Gobal dependency name. It must be unique, lowercased and it can not contains special characters.')
    @option('--dep-type',
            '-t',
            required=True,
            help=f'Dependency type. It can be text/css application/javascript or module.')
    @pass_context
    def create(ctx, name, dep_type):
        Create(ctx).exec(name, dep_type)

    @staticmethod
    @command(name='push',
             help='Push global dep(s) specs into the CMS database.')
    @option('--all',
            is_flag=True,
            help='Push all global deps.')
    @option('--dep',
            '-d',
            nargs=2,
            multiple=True,
            help='Name and type for the global dep to be pushed. For example: push -d bootstrap text/css')
    @constraint(RequireExactly(1), ['all', 'dep'])
    @pass_context
    def push(ctx, **params):
        if params['all']:
            click.echo('Operation not ready yet.')
            return
        Push(ctx).exec(params['dep'])

    @staticmethod
    @command(name='pull',
             help='Pull dep(s) specs from the CMS database.')
    @option('--all',
            is_flag=True,
            help='Pull all global deps.')
    @option('--dep',
            '-d',
            nargs=2,
            multiple=True,
            help='Name and type for the global dep to be pulled. For example: pull -d bootstrap application/javascript')
    @constraint(RequireExactly(1), ['all', 'dep'])
    @pass_context
    def pull(ctx, **params):
        if params['all']:
            click.echo('Operation not ready yet.')
            return
        Pull(ctx).exec(params['dep'])

    @staticmethod
    @command(name='remove', help='Remove a global dep.')
    @option('--name',
            '-n',
            required=True,
            help='Name of the global dep to be removed.')
    @option('--dep-type',
            '-t',
            required=True,
            help=f'Type to be removed.')
    @pass_context
    def remove(ctx, name, dep_type):
        Remove(ctx).exec(name, dep_type)
