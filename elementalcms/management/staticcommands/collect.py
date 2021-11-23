import os
import pathlib

import click
from google.cloud import storage

from elementalcms import ElementalContext


class Collect:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self):
        if self.context.cms_core_context.STATIC_BUCKET is None:
            click.echo('STATIC_BICKET parameter not found on current settings.')
            return
        client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        bucket = client.bucket(self.context.cms_core_context.STATIC_BUCKET)
        self.collect_platform_files(bucket)
        self.collect_app_files(bucket)
        click.echo('Collect command excecuted successfully.')

    @staticmethod
    def collect_platform_files(bucket):
        lib_root_path = pathlib.Path(__file__).resolve().parent.parent.parent
        source_folder = f'{lib_root_path}/static'
        for r, d, f in os.walk(source_folder):
            for file in f:
                source_file_name = f'{r}/{file}'
                destination_blob_name = source_file_name.replace(source_folder, '')[1:]
                blob = bucket.blob(destination_blob_name)
                blob.cache_control = 'private, max-age=180'
                blob.upload_from_filename(source_file_name)
                click.echo(f'Uploading {source_file_name} > {destination_blob_name}')

    def collect_app_files(self, bucket):
        source_folder = self.context.cms_core_context.STATIC_FOLDER
        for r, d, f in os.walk(source_folder):
            for file in f:
                source_file_name = f'{r}/{file}'
                destination_blob_name = source_file_name.replace(source_folder, '')[1:]
                blob = bucket.blob(destination_blob_name)
                blob.cache_control = 'private, max-age=180'
                blob.upload_from_filename(source_file_name)
                click.echo(f'Uploading {source_file_name} > {destination_blob_name}')
