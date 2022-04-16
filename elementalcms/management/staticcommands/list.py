import os

import click
from google.cloud import storage
from google.cloud.storage import Bucket

from elementalcms.core import ElementalContext


class List:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, path):

        if not bool(self.context.cms_core_context.STATIC_BUCKET
                    and not self.context.cms_core_context.STATIC_BUCKET.isspace()):
            click.echo('STATIC_BUCKET parameter not found on current settings.')
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

        bucket: Bucket = client.bucket(self.context.cms_core_context.STATIC_BUCKET)
        objects = bucket.list_blobs(prefix=prefix, delimiter=delimiter)

        folders = set()
        remote_files = []

        for obj in objects:
            obj_name_parts = obj.name.split('/')
            if obj_name_parts[0] == 'admin':
                continue
            folder_path = f'{"/".join(obj_name_parts[:-1])}/'
            folders.add(folder_path if folder_path == '/' else folder_path[:-1])
            if obj.name != folder_path:
                remote_files.append(obj.name)

        static_folder = self.context.cms_core_context.STATIC_FOLDER
        local_files = []
        for root, directories, files in os.walk(static_folder):
            clean_root = root.replace(f'{static_folder}', '') or '/'
            clean_root = clean_root if clean_root == '/' else clean_root[1:]
            if clean_root not in folders:
                continue
            for file in files:
                local_files.append(os.path.join(root, file).replace(f'{static_folder}/', ''))
        all_files = set(local_files + remote_files)

        for file in sorted(all_files):
            if file in remote_files and file in local_files:
                click.echo(file)
            elif file in remote_files:
                click.echo(f'{file} * ')
            else:
                click.echo(f' * {file}')

        if len(all_files) == 0:
            if path:
                click.echo(f'\nNo static files found at {path}')
            else:
                click.echo(f'\nNo static files found')
            return
        if path:
            click.echo(f'\n{len(all_files)} static files found at {path}')
        else:
            click.echo(f'\n{len(all_files)} static files found')
        if local_files != remote_files:
            click.echo('* is an indicator of missing files either on remote folder (left) or local folder (right)')
