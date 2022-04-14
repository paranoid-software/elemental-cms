import click
from cloup import constraint, option, command, pass_context, argument
from cloup.constraints import RequireExactly

from .mediacommands import List, Push


class Media(click.Group):

    def __init__(self):
        super(Media, self).__init__()
        self.name = 'media'
        self.add_command(self.list)
        self.add_command(self.push)

    @staticmethod
    @command(name='list',
             help='List media files.')
    @argument('path')
    @pass_context
    def list(ctx, path):
        List(ctx).exec(path)

    @staticmethod
    @command(name='push')
    @argument('pattern')
    @pass_context
    def push(ctx, pattern):
        """Push media file(s) into the media file's repository.

        You must use a search PATTERN to identify the files to be pushed.

        Samples:

        \b
        *.*
        *.txt
        *.svg
        **/images
        """
        Push(ctx).exec(pattern)
