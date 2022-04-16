import click
from cloup import constraint, option, command, pass_context
from cloup.constraints import RequireExactly

from .staticcommands import List, Collect


class Static(click.Group):

    def __init__(self):
        super(Static, self).__init__()
        self.name = 'static'
        self.add_command(self.list)
        self.add_command(self.collect)

    @staticmethod
    @command(name='list',
             help='List static resources.')
    @option('--all',
            is_flag=True,
            help='List all static resources.')
    @option('--folder',
            '-f',
            nargs=1,
            multiple=True,
            help='Name of the folder to be listed. For example: list -f app/client-stack')
    @constraint(RequireExactly(1), ['all', 'folder'])
    @pass_context
    def list(ctx, **params):
        if params['all']:
            List(ctx).exec(None)
            return
        List(ctx).exec(params['folder'][0])

    @staticmethod
    @command(name='collect',
             help='Collect static resources.')
    @pass_context
    def collect(ctx):
        Collect(ctx).exec()
