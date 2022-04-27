import click

from elementalcms.core import ElementalContext
from elementalcms.services.snippets import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self):
        result = GetAll(self.context.cms_db_context).execute()
        if result.is_failure():
            click.echo('There are no snippets to list. Create your first one by using the [snippets create] command.')
            return

        # TODO: Add repos difference indicators

        for snippet in result.value():
            click.echo(f'{snippet["name"]}')
