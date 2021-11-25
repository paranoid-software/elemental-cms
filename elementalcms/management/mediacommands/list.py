import click

from elementalcms.core import ElementalContext
from elementalcms.services import NoResult
from elementalcms.services.media import GetAll


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self):
        result = GetAll(self.context.cms_db_context).execute()
        if result.is_failure():
            if isinstance(result, NoResult):
                click.echo('No media files yet, create your first media file running the [media push] command.')
                return
            click.echo('Something went wrong and it was not possible to retreive the media information list.')
            return

        for spec in result.value():
            click.echo(spec["filePath"])
