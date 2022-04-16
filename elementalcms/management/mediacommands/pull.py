import time
import os
from shutil import copyfile
from typing import Optional

import click
from bson import json_util
from google.cloud import storage
from google.cloud.storage import Bucket

from elementalcms.core import ElementalContext


class Pull:

    def __init__(self, ctx):
        self.context: ElementalContext = ctx.obj['elemental_context']

    def exec(self, folder):

        if isinstance(folder, str):
            prefix = None
            delimiter = None
        else:
            prefix = folder[0]
            delimiter = '/'

        media_folder = self.context.cms_core_context.MEDIA_FOLDER

        if self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO:
            client = storage.Client.from_service_account_info(self.context.cms_core_context.GOOGLE_SERVICE_ACCOUNT_INFO)
        else:
            client = storage.Client()

        bucket: Bucket = client.bucket(self.context.cms_core_context.MEDIA_BUCKET)
        objects = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        remote_files = []

        for obj in objects:
            obj_name_parts = obj.name.split('/')
            folder_path = f'{"/".join(obj_name_parts[:-1])}/'
            if obj.name != folder_path:
                remote_files.append(obj.name)

        for file in remote_files:
            blob = bucket.blob(file)
            blob_folder = '/'.join(file.split('/')[0:-1])
            local_folder = f'{media_folder}/{blob_folder}/'
            if not os.path.exists(local_folder):
                os.makedirs(local_folder)
            click.echo(f'Downloading {file}')
            blob.download_to_filename(f'{media_folder}/{file}')
            click.echo(f'{file} downloaded successfuly.')
