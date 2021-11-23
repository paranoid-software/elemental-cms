from elementalcms.persistence.repositories import SnippetsRepository
from elementalcms.services import UseCaseResult, NoResult, Success, Failure
from elementalcms.core import MongoDbContext


class GetMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, name) -> UseCaseResult:
        repo = SnippetsRepository(self.__db_context)
        result = repo.find({'name': name}, 0, 10)
        if result['total'] == 0:
            return NoResult()

        if result['total'] > 1:
            return Failure({'duplicatedSnippet': True})

        return Success(result['items'][0])
