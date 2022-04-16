import click
from google.cloud import storage
from google.cloud.storage import Bucket

from elementalcms.core import ElementalContext


class Delete:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, file_name):

        if self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO:
            client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        else:
            client = storage.Client()

        bucket: Bucket = client.bucket(self.context.cms_core_context.STATIC_BUCKET)
        blob = bucket.blob(file_name)
        blob.delete()
        click.echo(f'{file_name} removed successfuly.')
