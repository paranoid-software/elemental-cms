import click
from cloup import constraint, option, command, pass_context, argument
from cloup.constraints import RequireExactly

from .staticcommands import List, Collect, Delete


class Static(click.Group):

    def __init__(self):
        super(Static, self).__init__()
        self.name = 'static'
        self.add_command(self.list)
        self.add_command(self.collect)
        self.add_command(self.delete)

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
    @command(name='collect')
    @argument('pattern', type=click.STRING)
    @click.option("--ignore-internals",
                  is_flag=True,
                  show_default=True,
                  default=False,
                  help="Do not collect internal static resources.")
    @pass_context
    def collect(ctx, pattern, ignore_internals):
        """Collect static resources.

        You must use a search PATTERN to identify the files to be collected.
        Remember to wrap your patter inside double quotes.

        Samples (assuming static is our local static folder):

        \b
        "static/*.*"
        "static/*.txt"
        "static/*.svg"
        "static/**/images/*"
        """
        Collect(ctx).exec(pattern, ignore_internals)

    @staticmethod
    @command(name='delete')
    @argument('file')
    @pass_context
    def delete(ctx, file):
        """Delete especified file from GCS."""
        Delete(ctx).exec(file)
