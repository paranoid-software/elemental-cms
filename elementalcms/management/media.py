import click
from cloup import constraint, option, command, pass_context, argument
from cloup.constraints import RequireExactly

from .mediacommands import List, Pull, Push, Delete


class Media(click.Group):

    def __init__(self):
        super(Media, self).__init__()
        self.name = 'media'
        self.add_command(self.list)
        self.add_command(self.pull)
        self.add_command(self.push)
        self.add_command(self.delete)

    @staticmethod
    @command(name='list',
             help='List media files.')
    @option('--all',
            is_flag=True,
            help='List all media files.')
    @option('--folder',
            '-f',
            nargs=1,
            multiple=True,
            help='Name of the folder to be listed. For example: list -f default/')
    @constraint(RequireExactly(1), ['all', 'folder'])
    @pass_context
    def list(ctx, **params):
        if params['all']:
            List(ctx).exec(None)
            return
        List(ctx).exec(params['folder'][0])

    @staticmethod
    @command(name='pull',
             help='Pull media file(s) from GCS.')
    @option('--all',
            is_flag=True,
            help='Pull all media files into the local media folder.')
    @option('--folder',
            '-f',
            nargs=1,
            multiple=True,
            help='Name of the folder to be pulled. For example: pull -f default/')
    @constraint(RequireExactly(1), ['all', 'folder'])
    @pass_context
    def pull(ctx, **params):
        if params['all']:
            return Pull(ctx).exec('*')
        return Pull(ctx).exec(params['folder'])

    @staticmethod
    @command(name='push')
    @argument('pattern')
    @pass_context
    def push(ctx, pattern):
        """Push media file(s) to GCS.

        You must use a search PATTERN to identify the files to be pushed.
        Remember to wrap your patter inside double quotes.

        Samples (assuming media is our local media folder):

        \b
        "media/*.*"
        "media/*.txt"
        "media/*.svg"
        "media/**/images/*"
        """
        Push(ctx).exec(pattern)

    @staticmethod
    @command(name='delete')
    @argument('file')
    @pass_context
    def delete(ctx, file):
        """Delete especified file from GCS."""
        Delete(ctx).exec(file)
