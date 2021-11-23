from elementalcms.persistence.repositories import SessionsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class UpsertMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, value) -> UseCaseResult:
        repo = SessionsRepository(self.__db_context)
        result = repo.update({'sid': value['sid']}, value, True)
        if result.modified_count <= 0:
            return NoResult()
        return Success(result)
