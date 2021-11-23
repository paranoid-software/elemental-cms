from elementalcms.persistence.repositories import SnippetsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetOne:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, _id) -> UseCaseResult:
        repo = SnippetsRepository(self.__db_context)
        snippet = repo.find_one(_id)
        if snippet is None:
            return NoResult()
        return Success(snippet)
