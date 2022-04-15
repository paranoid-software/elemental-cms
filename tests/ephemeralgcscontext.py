import os
import time
from typing import Optional, List
from google.cloud import storage
from google.cloud.storage import Blob, Bucket


class GcsState:
    bucket_name: str
    files_names: Optional[List[str]]

    def __init__(self, bucket_name, files_names: Optional[List[str]] = None):
        self.bucket_name = bucket_name
        self.files_names = files_names


class EphemeralGcsContext:

    __bucket_names = {}
    __state: List[GcsState] = []

    def __init__(self,
                 initial_state: Optional[List[GcsState]] = None,
                 host_name: str = 'localhost',
                 port: int = 9023):

        # noinspection HttpUrlsUsage
        os.environ['STORAGE_EMULATOR_HOST'] = f'http://{host_name}:{port}'

        self.__state = initial_state

    def __enter__(self):

        self.__bucket_names = {}
        first_bucket_name = None

        client = storage.Client()

        for state in self.__state or []:
            bucket_name = f'{state.bucket_name}-{round(time.time() * 1000)}'
            if first_bucket_name is None:
                first_bucket_name = bucket_name
            self.__bucket_names[bucket_name] = bucket_name
            bucket = client.bucket(bucket_name)
            client.create_bucket(bucket)
            if state.files_names is None or len(state.files_names) == 0:
                continue
            for file_name in state.files_names:
                blob: Blob = bucket.blob(file_name)
                blob.upload_from_string('--- adding some text ---')

        return first_bucket_name if len(self.__bucket_names) <= 1 else self.__bucket_names

    def __exit__(self, exc_type, exc_val, exc_tb):
        client = storage.Client()
        for bucket_name in self.__bucket_names:
            bucket: Bucket = client.bucket(bucket_name)
            bucket.delete(force=True)
        del os.environ['STORAGE_EMULATOR_HOST']
