from elementalcms.core import MongoDbContext
from elementalcms.persistence.repositories import GenericRepository


class GlobalDepsRepository(GenericRepository):

    def __init__(self, db_context: MongoDbContext):
        super().__init__(db_context, 'global_deps')
