from elementalcms.persistence.repositories import SessionsRepository
from elementalcms.services import UseCaseResult, NoResult, Success, Failure
from elementalcms.core import MongoDbContext


class GetMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, sid) -> UseCaseResult:
        repo = SessionsRepository(self.__db_context)
        result = repo.find({'sid': sid})
        if result is None or len(result) == 0:
            return NoResult()

        if len(result) > 1:
            return Failure({'duplicatedSession': True})

        return Success(result[0])
