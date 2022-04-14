import os

import click
from google.cloud import storage
from google.cloud.storage import Bucket

from elementalcms.core import ElementalContext


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, path):

        if self.context.cms_core_context.MEDIA_BUCKET is None:
            click.echo('MEDIA_BUCKET parameter not found on current settings.')
            return

        if path == '':
            click.echo('Empty string is not a valid list command argument, specify either / for root folder or '
                       'folder_name/ for any folder or sub-folder path.')
            return

        prefix = path
        delimiter = '/'

        if path == '*':
            prefix = None
            delimiter = None

        elif not path[-1] == '/':
            click.echo('Remember to end your folder and/or sub-folder path with a /')
            return

        if path == '/':
            prefix = ''

        media_folder = self.context.cms_core_context.MEDIA_FOLDER
        local_files = []
        for root, directories, files in os.walk(media_folder):
            for file in files:
                local_files.append(os.path.join(root, file).replace(f'{media_folder}/', ''))

        client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        bucket: Bucket = client.bucket(self.context.cms_core_context.MEDIA_BUCKET)

        objects = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        objects_map = {}
        folders_paths = set()
        number_of_files = 0

        for obj in objects:
            obj_name_parts = obj.name.split('/')
            folder_path = f'{"/".join(obj_name_parts[:-1])}/'
            folders_paths.add(folder_path)
            if folder_path not in objects_map:
                objects_map[folder_path] = []
            if obj.name != folder_path:
                objects_map[folder_path].append(obj)
                click.echo(f'{obj.name}{" * " if obj.name not in local_files else ""}')
                number_of_files += 1

        if number_of_files == 0:
            click.echo(f'\nNo media files found at {path if path != "*" else "bucket"}')
            click.echo('Files with * are not present on your local media folder.')
            return
        click.echo(f'\n{number_of_files} media files found at {path if path != "*" else "bucket"}')
        click.echo('Files with * are not present on your local media folder.')
