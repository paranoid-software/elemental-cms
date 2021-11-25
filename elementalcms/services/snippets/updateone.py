import datetime
from elementalcms.persistence.repositories import SnippetsRepository
from elementalcms.services import UseCaseResult, Success
from elementalcms.core import MongoDbContext


class UpdateOne:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, _id, snippet) -> UseCaseResult:
        repo = SnippetsRepository(self.__db_context)
        if '_id' in snippet:
            del snippet['_id']
        snippet['lastModifiedAt'] = datetime.datetime.utcnow()
        success = repo.replace_one(_id, snippet, True)
        return Success(success)
