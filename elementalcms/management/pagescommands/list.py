import click

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.pages import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, drafts=False):
        result = GetAll(self.context.cms_db_context).execute(drafts)
        if result.is_failure():
            if isinstance(result, NoResult):
                click.echo('No pages yet, create your first page running the [pages create] command.')
                return
            click.echo('Something went wrong and it was not possible to retreive the pages information list.')
            return

        for spec in result.value():
            click.echo(f'{spec["name"]} -> {spec["title"]}')
