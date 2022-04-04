import glob
import json

import click
from google.cloud import storage

from elementalcms.core import ElementalContext
from elementalcms.services.media import UpsertMe


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
            upsert_me_result = UpsertMe(self.context.cms_db_context).execute(destination_blob_name)
            if upsert_me_result.is_failure():
                click.echo(f'{destination_blob_name} was pushed successfully, but no log was created.')
                click.echo(f'Failure reason: {json.dumps(upsert_me_result.value())}')
                continue
            if not upsert_me_result.value():
                click.echo(f'{destination_blob_name} was pushed successfully, but no log was created.')
                continue
            click.echo(f'{file} pushed successfully.')
