from typing import Optional

from cloup import constraint, option, command, pass_context, Group
from cloup.constraints import RequireExactly

from .globaldepscommands import List, Create, Push, Pull, Remove


class GlobalDeps(Group):

    def __init__(self):
        super(GlobalDeps, self).__init__()
        self.name = 'global-deps'
        self.add_command(self.list)
        self.add_command(self.create)
        self.add_command(self.push)
        self.add_command(self.pull)
        self.add_command(self.remove)

        # TODO: Add command to find differences between local workspace and CMS database

    @staticmethod
    @command(name='list',
             help='Display global dependencies list.')
    @pass_context
    def list(ctx):
        List(ctx).exec()

    @staticmethod
    @command(name='create',
             help='Create a new global dependency at local workspace.')
    @option('--dep',
            '-d',
            required=True,
            nargs=2,
            help='Name and type for the global dep(s) to be created; name must be unique, lowercase and it can not '
                 'contains special characters, and the type can be any of: text/css application/javascript or module. '
                 'For example create --dep jquery application/javascript')
    @pass_context
    def create(ctx, dep):
        Create(ctx).exec(dep[0], dep[1])

    @staticmethod
    @command(name='push',
             help='Push global dep(s) specs to the CMS database.')
    @option('--all',
            is_flag=True,
            help='Push all global dependencies.')
    @option('--dep',
            '-d',
            nargs=2,
            multiple=True,
            help='Name and type for the global dep(s) to be pushed. '
                 'For example: push -d bootstrap text/css -d bootstrap application/javascript')
    @constraint(RequireExactly(1), ['all', 'dep'])
    @pass_context
    def push(ctx, **params) -> [str]:
        if params['all']:
            return Push(ctx).exec('*')
        return Push(ctx).exec(params['dep'])

    @staticmethod
    @command(name='pull',
             help='Pull global dep(s) specs from the CMS database.')
    @option('--all',
            is_flag=True,
            help='Pull all global dependencies.')
    @option('--dep',
            '-d',
            nargs=2,
            multiple=True,
            help='Name and type for the global dep(s) to be pulled. '
                 'For example: pull -d bootstrap application/javascript')
    @constraint(RequireExactly(1), ['all', 'dep'])
    @pass_context
    def pull(ctx, **params) -> [str]:
        if params['all']:
            return Pull(ctx).exec('*')
        return Pull(ctx).exec(params['dep'])

    @staticmethod
    @command(name='remove', help='Remove global dependency from the CMS database.')
    @option('--dep',
            '-d',
            required=True,
            nargs=2,
            help='Name and type for the global dependency to be removed. '
                 'For example: remove --dep bootstrap application/javascript')
    @pass_context
    def remove(ctx, dep) -> Optional[str]:
        return Remove(ctx).exec(dep[0], dep[1])
