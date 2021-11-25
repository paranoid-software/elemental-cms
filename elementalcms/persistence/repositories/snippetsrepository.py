from elementalcms.core import MongoDbContext
from elementalcms.persistence.repositories import GenericRepository


class SnippetsRepository(GenericRepository):

    def __init__(self, db_context: MongoDbContext):
        super().__init__(db_context, 'snippets')
