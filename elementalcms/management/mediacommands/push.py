import glob

import click
from google.cloud import storage

from elementalcms.core import ElementalContext


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, pattern):
        if self.context.cms_core_context.MEDIA_BUCKET is None:
            click.echo('MEDIA_BUCKET parameter not found on current settings.')
            return
        media_folder = self.context.cms_core_context.MEDIA_FOLDER
        files = glob.glob(f'{media_folder}/{pattern}')
        if len(files) == 0:
            click.echo(f'We found 0 files for the search pattern {pattern}')
            return
        client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        bucket = client.bucket(self.context.cms_core_context.MEDIA_BUCKET)
        click.echo(f'Pushing {len(files)} files to {bucket.name}')
        for file in files:
            destination_blob_name = file.replace(media_folder, '', 1).lstrip('/')
            click.echo(f'Pushing {file} to {destination_blob_name}')
            blob = bucket.blob(destination_blob_name)
            # TODO: Store cache control value on settings
            blob.cache_control = 'private, max-age=180'
            blob.upload_from_filename(file)
            click.echo(f'{file} pushed successfully.')
