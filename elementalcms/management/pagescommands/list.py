import click

from elementalcms.core import ElementalContext
from elementalcms.services.pages import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, drafts=False):
        result = GetAll(self.context.cms_db_context).execute(drafts)
        if result.is_failure():
            click.echo('There are no pages to list. Create your first one by using the [pages create] command.')
            return

        # TODO: Add repos difference indicators

        for spec in result.value():
            click.echo(f'{spec["name"]} -> {spec["title"]}')
