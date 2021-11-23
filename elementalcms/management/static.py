import click
from cloup import constraint, option, command, pass_context
from cloup.constraints import RequireExactly

from .staticcommands import Collect


class Static(click.Group):

    def __init__(self):
        super(Static, self).__init__()
        self.name = 'static'
        self.add_command(self.collect)

    @staticmethod
    @command(name='collect',
             help='Collect static resources.')
    @pass_context
    def collect(ctx):
        Collect(ctx).exec()
