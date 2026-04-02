import threading

import pymongo.errors
from pymongo import MongoClient

from elementalcms.core import MongoDbContext

_clients: dict = {}
_lock = threading.Lock()


class MongoDbConnectionManager:

    @classmethod
    def _get_db(cls, context: MongoDbContext):
        conn_str = context.connection_string
        if conn_str not in _clients:
            with _lock:
                if conn_str not in _clients:
                    _clients[conn_str] = MongoClient(conn_str)
        return _clients[conn_str].get_database(context.database_name)

    @classmethod
    def get_db_name(cls, context: MongoDbContext):
        try:
            db = cls._get_db(context)
            return db.name
        except pymongo.errors.ConnectionFailure:
            return None
