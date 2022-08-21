from elementalcms.persistence.repositories import SessionsRepository
from elementalcms.services import UseCaseResult, Success, Failure
from elementalcms.core import MongoDbContext
import json
from deepdiff import DeepDiff


class UpsertMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, value) -> UseCaseResult:
        repo = SessionsRepository(self.__db_context)
        find_result = repo.find({'sid': value['sid']})
        if find_result['total'] == 0:
            new_id = repo.insert_one(value)
            return Success({'id': new_id})
        if find_result['total'] > 1:
            return Failure({'duplicatedSession': True})
        current = find_result['items'][0]
        diff = DeepDiff(dict(**value.get('data')), current.get('data'))
        if len(diff.keys()) >0 :
            replace_one_result = repo.replace_one(current['_id'], value, True)
            return Success(replace_one_result)
        if (value.get('expiration') - current.get('expiration')).total_seconds() > 30:
            replace_one_result = repo.replace_one(current['_id'], value, True)
            return Success(replace_one_result)
        return Failure({'updateUnnecessary': True})
