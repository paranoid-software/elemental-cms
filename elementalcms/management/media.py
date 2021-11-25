import click
from cloup import constraint, option, command, pass_context, argument
from cloup.constraints import RequireExactly

from .mediacommands import Push


class Media(click.Group):

    def __init__(self):
        super(Media, self).__init__()
        self.name = 'media'
        self.add_command(self.push)

    @staticmethod
    @command(name='push',
             help='Push media file(s) to the media repository.')
    @argument('pattern')
    @pass_context
    def push(ctx, pattern):
        """Print PATTERN.
        PATTERN is a search pattern for files to be pushed, like:

        *
        *.txt
        *.svg
        **/images

        """
        Push(ctx).exec(pattern)
