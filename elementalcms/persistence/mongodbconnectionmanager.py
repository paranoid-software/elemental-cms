from dataclasses import dataclass

import pymongo.errors
from pymongo import MongoClient

from elementalcms.core import MongoDbContext


@dataclass
class MongoDbConnectionManager:

    __db_client: MongoClient = None

    @classmethod
    def _get_db(cls, context: MongoDbContext):
        if cls.__db_client is None:
            cls.__db_client = MongoClient(context.connection_string)
        return cls.__db_client.get_database(context.database_name)

    @classmethod
    def get_db_name(cls, context: MongoDbContext):
        try:
            db = cls._get_db(context)
            return db.name
        except pymongo.errors.ConnectionFailure:
            return None
