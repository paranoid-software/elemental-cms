import click
from cloup import constraint, option, command, pass_context, argument
from cloup.constraints import RequireExactly

from .mediacommands import List, Pull, Push


class Media(click.Group):

    def __init__(self):
        super(Media, self).__init__()
        self.name = 'media'
        self.add_command(self.list)
        self.add_command(self.push)

    @staticmethod
    @command(name='list',
             help='List media files.')
    @argument('path', required=False)
    @pass_context
    def list(ctx, path):
        List(ctx).exec(path)

    @staticmethod
    @command(name='pull',
             help='Pull media files from remote repository.')
    @option('--all',
            is_flag=True,
            help='Pull all media files into the local media folder.')
    @option('--folder',
            '-f',
            nargs=1,
            multiple=True,
            help='Name of the folder to be pulled. '
                 'For example: pull -f default/')
    @constraint(RequireExactly(1), ['all', 'folder'])
    @pass_context
    def list(ctx, **params):
        if params['all']:
            return Pull(ctx).exec('*')
        return Pull(ctx).exec(params['folder'])

    @staticmethod
    @command(name='push',
             help='Push local files to the remote repository.')
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
