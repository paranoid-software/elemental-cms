import pymongo
from elementalcms.persistence import MongoDbConnectionManager

from elementalcms.core import MongoDbContext


class SessionsRepository(MongoDbConnectionManager):

    coll_name = 'sessions'

    def __init__(self, db_context: MongoDbContext):
        self.__db = self._get_db(db_context)

    def create_expiration_index(self):
        index_info = self.__db.get_collection(self.coll_name).index_information()
        if 'ix.expiration' in index_info:
            return
        self.__db.get_collection(self.coll_name).create_index('expiration',
                                                              name='ix.expiration',
                                                              expireAfterSeconds=0)

    def find(self, query=None, page=None, page_size=None):
        if page is not None and page_size is not None:
            raise Exception('Paging not implemented.')
        result = self.__db.get_collection(self.coll_name).find(query if query is not None else {})
        return list(result)

    def update(self, query, value, upsert):
        result = self.__db.get_collection(self.coll_name).replace_one(query, value, upsert)
        return result
