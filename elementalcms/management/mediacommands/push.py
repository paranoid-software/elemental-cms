import glob
import os
import click
from google.cloud import storage

from elementalcms.core import ElementalContext


class Push:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, pattern):

        media_folder = self.context.cms_core_context.MEDIA_FOLDER

        if not pattern.startswith(media_folder):
            click.echo(f'We can only push files located at the media folder which right now is {media_folder}')
            return

        if self.context.cms_core_context.MEDIA_BUCKET is None:
            click.echo('MEDIA_BUCKET parameter not found on current settings.')
            return

        files = glob.glob(pattern, recursive=True)
        if len(files) == 0:
            click.echo(f'We found 0 files for {pattern}')
            return

        if self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO:
            client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        else:
            client = storage.Client()

        bucket = client.bucket(self.context.cms_core_context.MEDIA_BUCKET)
        click.echo(f'Pushing {len(files)} files to {bucket.name}')
        for file in files:
            if not os.path.isfile(file):
                continue
            destination_blob_name = file.replace(media_folder, '', 1).lstrip('/')
            click.echo(f'Pushing {file} to {destination_blob_name}')
            blob = bucket.blob(destination_blob_name)
            # TODO: Read media files cache control value from settings
            blob.cache_control = 'private, max-age=180'
            blob.upload_from_filename(file)
            click.echo(f'{file} pushed successfully.')
