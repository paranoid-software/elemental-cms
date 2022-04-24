from elementalcms.persistence.repositories import SnippetsRepository
from elementalcms.services import UseCaseResult, NoResult, Success, Failure
from elementalcms.core import MongoDbContext


class GetMany:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, names) -> UseCaseResult:
        repo = SnippetsRepository(self.__db_context)
        result = repo.find({'name': { '$in': names }}, page=0, page_size=30)
        if result['total'] == 0:
            return NoResult()
        return Success(result['items'])
