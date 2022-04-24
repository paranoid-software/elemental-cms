import click

from elementalcms.core import ElementalContext
from elementalcms.services.global_deps import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self):
        result = GetAll(self.context.cms_db_context).execute()
        if result.is_failure():
            click.echo('There are no global dependencies to list. Create your first one by using the '
                       '[global-deps create] command.')
            return

        for dep in result.value():
            click.echo(f'{dep["type"]} <-> {dep["name"]}')
