import os
import pathlib
from glob import glob

import click
from google.cloud import storage

from elementalcms import ElementalContext


class Collect:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, pattern, ignore_internals):

        static_folder = self.context.cms_core_context.STATIC_FOLDER

        if not pattern.startswith(static_folder):
            click.echo(f'We can only collect files located at the static folder which right now is {static_folder}')
            return

        if self.context.cms_core_context.STATIC_BUCKET is None:
            click.echo('STATIC_BUCKET parameter not found on current settings.')
            return

        if self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO:
            client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        else:
            client = storage.Client()

        bucket = client.bucket(self.context.cms_core_context.STATIC_BUCKET)
        if not ignore_internals:
            self.collect_platform_files(bucket)
        self.collect_app_files(bucket, pattern)

        click.echo('Collect command excecuted successfully.')

    @staticmethod
    def collect_platform_files(bucket):
        lib_root_path = pathlib.Path(__file__).resolve().parent.parent.parent
        source_folder = f'{lib_root_path}/static'
        for r, d, f in os.walk(source_folder):
            for file in f:
                source_file_name = f'{r}/{file}'
                destination_blob_name = source_file_name.replace(source_folder, '', 1).lstrip('/')
                blob = bucket.blob(destination_blob_name)
                blob.cache_control = 'private, max-age=180'
                try:
                    if file.endswith('.css') or file.endswith('.js'):
                        blob.content_encoding = 'gzip'
                        import gzip
                        with open(source_file_name, "r") as uncompressed:
                            uncompressed_content = uncompressed.read()
                        compresed = gzip.compress(uncompressed_content.encode())
                        blob.upload_from_string(compresed, content_type="text/css" if '.css' in file else 'application/javascript')
                    else:
                        blob.upload_from_filename(source_file_name)
                except Exception as e:
                    print(e)
                click.echo(f'Uploading {source_file_name} to {destination_blob_name}')

    def collect_app_files(self, bucket, pattern):
        files = glob(pattern, recursive=True)
        if len(files) == 0:
            return
        source_folder = self.context.cms_core_context.STATIC_FOLDER
        for file in files:
            if not os.path.isfile(file):
                continue
            destination_blob_name = file.replace(source_folder, '', 1).lstrip('/')
            blob = bucket.blob(destination_blob_name)
            blob.cache_control = 'private, max-age=180'
            if file.endswith('.css') or file.endswith('.js'):
                blob.content_encoding = 'gzip'
                import gzip
                with open(file, "r") as uncompressed:
                    uncompressed_content = uncompressed.read()
                compresed = gzip.compress(uncompressed_content.encode())
                blob.upload_from_string(compresed, content_type="text/css" if '.css' in file else 'application/javascript')
            else:
                blob.upload_from_filename(file)
            click.echo(f'Uploading {file} to {destination_blob_name}')
