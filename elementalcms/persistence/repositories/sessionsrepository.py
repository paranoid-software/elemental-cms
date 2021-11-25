from elementalcms.core import MongoDbContext
from elementalcms.persistence.repositories import GenericRepository


class SessionsRepository(GenericRepository):

    coll_name = 'sessions'

    def __init__(self, db_context: MongoDbContext):
        super().__init__(db_context, 'sessions')

    def create_expiration_index(self):
        index_info = self._coll.index_information()
        if 'ix.expiration' in index_info:
            return
        self._coll.create_index('expiration',
                                name='ix.expiration',
                                expireAfterSeconds=0)
