import click

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.global_deps import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self):
        result = GetAll(self.context.cms_db_context).execute()
        if result.is_failure():
            if isinstance(result, NoResult):
                click.echo('No dependencies found. Create your first one using the [global-deps create] command.')
                return
            click.echo('Something went wrong and it was not possible to retrieve the global dependencies list.')
            return

        for dep in result.value():
            click.echo(f'{dep["type"]} <-> {dep["name"]}')
