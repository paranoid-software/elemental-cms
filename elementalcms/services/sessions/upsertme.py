from elementalcms.persistence.repositories import SessionsRepository
from elementalcms.services import UseCaseResult, NoResult, Success, Failure
from elementalcms.core import MongoDbContext


class UpsertMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, value) -> UseCaseResult:
        repo = SessionsRepository(self.__db_context)
        find_result = repo.find({'sid': value['sid']})
        if find_result['total'] == 0:
            return NoResult()
        if find_result['total'] > 1:
            return Failure({'duplicatedSession': True})
        current = find_result['items'][0]
        replace_one_result = repo.replace_one(current['_id'], value, True)
        return Success(replace_one_result)
