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
            click.echo('Empty string is not a valid folder, specify either / for root folder or '
                       'folder_name/ for any folder or sub-folder path.')
            return

        prefix = path
        delimiter = '/'

        if path is None:
            prefix = None
            delimiter = None
        elif not path[-1] == '/':
            click.echo('Remember to end your folder and/or sub-folder path with a /')
            return

        if path == '/':
            prefix = ''

        if self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO:
            client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        else:
            client = storage.Client()
        bucket: Bucket = client.bucket(self.context.cms_core_context.MEDIA_BUCKET)

        objects = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        remote_files = []

        folders_paths = set()

        for obj in objects:
            obj_name_parts = obj.name.split('/')
            folder_path = f'{"/".join(obj_name_parts[:-1])}/'
            folders_paths.add(folder_path if folder_path == '/' else folder_path[:-1])
            if obj.name != folder_path:
                remote_files.append(obj.name)

        media_folder = self.context.cms_core_context.MEDIA_FOLDER
        local_files = []
        for root, directories, files in os.walk(media_folder):
            clean_root = root.replace(f'{media_folder}', '') or '/'
            clean_root = clean_root if clean_root == '/' else clean_root[1:]
            if clean_root not in folders_paths:
                continue
            for file in files:
                local_files.append(os.path.join(root, file).replace(f'{media_folder}/', ''))
        all_files = set(local_files + remote_files)

        for file in sorted(all_files):
            if file in remote_files and file in local_files:
                click.echo(file)
            elif file in remote_files:
                click.echo(f'{file} * ')
            else:
                click.echo(f' * {file}')

        if len(all_files) == 0:
            click.echo(f'\nNo media files found at {path if path is not None else "bucket"}')
            click.echo('Files with * are not present on your remote or local media folder.')
            return
        click.echo(f'\n{len(all_files)} media files found at {path if path is not None else "bucket"}')
        click.echo('Files with * are not present on your remote or local media folder.')
