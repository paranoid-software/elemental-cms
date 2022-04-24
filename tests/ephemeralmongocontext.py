import os
import time
from typing import Any, Tuple
from bson import json_util, ObjectId
from dataclasses_serialization.bson import BSONSerializer

from pymongo import MongoClient
from typing import List, Optional

from pymongo.collection import Collection
from pymongo.database import Database


class MongoDbStateData:
    coll_name: str
    items: Optional[List[Any]]

    def __init__(self, coll_name, items):
        self.coll_name = coll_name
        self.items = items


class MongoDbState:
    db_name: str
    data: Optional[List[MongoDbStateData]]

    def __init__(self, db_name, data: Optional[List[MongoDbStateData]] = None):
        self.db_name = db_name
        self.data = data


class MongoDbStateDataFromFile:
    coll_name: str
    path: str

    def __init__(self, coll_name, path):
        self.coll_name = coll_name
        self.path = path


class MongoDbStateFromFile:
    db_name: str
    files: Optional[List[MongoDbStateDataFromFile]]

    def __init__(self, db_name, files: Optional[List[MongoDbStateDataFromFile]] = None):
        self.db_name = db_name
        self.files = files


class MongoDbReader:
    db: Database

    def __init__(self, client, db_name):
        self.db = client.get_database(db_name)

    def find_one(self, coll_name, _filter):
        return self.db.get_collection(coll_name).find_one(_filter)

    def count(self, coll_name):
        return self.db.get_collection(coll_name).estimated_document_count()


class EphemeralMongoContext:

    __connection_string: str
    __db_names = {}
    __readers = {}

    __state: List[MongoDbState] = []

    def __init__(self,
                 connection_string: str,
                 initial_state_from_files: Optional[List[MongoDbStateFromFile]] = None,
                 initial_state: Optional[List[MongoDbState]] = None):

        self.__connection_string = connection_string

        if (initial_state_from_files is None) == (initial_state is None):
            raise ValueError('Exactly one of `initial_state_from_files` or `initial_state` must be provided.')

        if initial_state_from_files is not None:

            self.__state: List[MongoDbState] = []

            for state in initial_state_from_files:
                data: List[MongoDbStateData] = []
                for file in state.files:
                    file_data = []
                    if os.path.exists(file.path):
                        with open(file.path) as f:
                            file_data = json_util.loads(f.read())
                    data.append(MongoDbStateData(coll_name=file.coll_name,
                                                 items=file_data))
                self.__state.append(MongoDbState(db_name=state.db_name,
                                                 data=data))

            return

        self.__state = [] + initial_state

    def __enter__(self):

        self.__db_names = {}
        first_db_name = None
        first_db_reader = None

        for state in self.__state:
            db_name = f'{state.db_name}_{round(time.time() * 1000)}'
            if first_db_name is None:
                first_db_name = db_name
            client = self._get_client()
            if first_db_reader is None:
                first_db_reader = MongoDbReader(client, db_name)
            self.__db_names[state.db_name] = db_name
            self.__readers[state.db_name] = MongoDbReader(client, db_name)
            if state.data is None:
                continue
            for data in state.data:
                coll_name = data.coll_name
                for item in data.items:
                    if 'id' in item:
                        item['_id'] = item['id']
                        del item['id']
                    client.get_database(db_name).get_collection(coll_name).insert_one(BSONSerializer.serialize(item))

        if len(self.__db_names) <= 1:
            return first_db_name, first_db_reader

        return self.__db_names, self.__readers

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for db_name in self.__db_names:
            client = self._get_client()
            client.drop_database(self.__db_names[db_name])

    def _get_client(self):
        client = MongoClient(self.__connection_string)
        return client
