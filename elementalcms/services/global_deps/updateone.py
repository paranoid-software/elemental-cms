import datetime
from elementalcms.persistence.repositories import GlobalDepsRepository
from elementalcms.services import UseCaseResult, Success
from elementalcms.core import MongoDbContext


class UpdateOne:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, _id, dep) -> UseCaseResult:
        repo = GlobalDepsRepository(self.__db_context)
        if '_id' in dep:
            del dep['_id']
        dep['lastModifiedAt'] = datetime.datetime.utcnow()
        success = repo.replace_one(_id, dep, True)
        return Success(success)
